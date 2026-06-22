from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from multiprocessing import get_context
from zoneinfo import ZoneInfo

import pytest

from ai_usage import AIUsagePolicy, UsageLimitError

NOW = datetime(2026, 6, 21, 12, 0, tzinfo=ZoneInfo("Asia/Shanghai"))


def acquire_in_process(runtime_db, index, start_event, results):
    policy = AIUsagePolicy(
        runtime_db=runtime_db,
        secret_key="test-secret-key-with-enough-length",
        global_daily_limit=5,
        daily_limit=3,
        rate_limit=3,
        max_concurrent=20,
        lease_seconds=90,
    )
    start_event.wait()
    try:
        policy.acquire(f"process-device-{index}", f"10.1.0.{index}", NOW)
        results.put(True)
    except UsageLimitError:
        results.put(False)


def make_policy(tmp_path, **overrides):
    settings = {
        "runtime_db": tmp_path / "runtime.db",
        "secret_key": "test-secret-key-with-enough-length",
        "global_daily_limit": 100,
        "daily_limit": 3,
        "rate_limit": 3,
        "max_concurrent": 4,
        "lease_seconds": 90,
    }
    settings.update(overrides)
    return AIUsagePolicy(**settings)


def test_fourth_daily_request_is_rejected(tmp_path):
    policy = make_policy(tmp_path, max_concurrent=10)

    for _ in range(3):
        grant = policy.acquire("device-a", "127.0.0.1", NOW)
        policy.release(grant.lease_id)

    with pytest.raises(UsageLimitError) as error:
        policy.acquire("device-a", "127.0.0.1", NOW)

    assert error.value.code == "AI_DAILY_QUOTA_EXHAUSTED"
    assert error.value.retry_after > 0


def test_per_device_concurrency_is_one(tmp_path):
    policy = make_policy(tmp_path)
    grant = policy.acquire("device-a", "127.0.0.1", NOW)

    with pytest.raises(UsageLimitError) as error:
        policy.acquire("device-a", "127.0.0.1", NOW)

    assert error.value.code == "AI_CONCURRENCY_LIMITED"
    policy.release(grant.lease_id)


def test_global_limit_is_atomic_across_threads(tmp_path):
    policy = make_policy(tmp_path, global_daily_limit=10, max_concurrent=20)

    def acquire(index):
        try:
            return policy.acquire(f"device-{index}", f"10.0.0.{index}", NOW)
        except UsageLimitError:
            return None

    with ThreadPoolExecutor(max_workers=20) as executor:
        grants = list(executor.map(acquire, range(20)))

    accepted = [grant for grant in grants if grant]
    assert len(accepted) == 10
    for grant in accepted:
        policy.release(grant.lease_id)


def test_global_limit_is_atomic_across_processes(tmp_path):
    context = get_context("spawn")
    start_event = context.Event()
    results = context.Queue()
    runtime_db = str(tmp_path / "runtime.db")
    processes = [
        context.Process(
            target=acquire_in_process,
            args=(runtime_db, index, start_event, results),
        )
        for index in range(12)
    ]

    for process in processes:
        process.start()
    start_event.set()
    accepted = [results.get(timeout=30) for _ in processes]
    for process in processes:
        process.join(timeout=30)
        assert process.exitcode == 0

    assert sum(accepted) == 5
