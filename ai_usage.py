import hashlib
import hmac
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from itsdangerous import BadSignature, URLSafeSerializer

from database import sqlite_connection

DEVICE_COOKIE = "zgs_device"
SHANGHAI = ZoneInfo("Asia/Shanghai")


class UsageLimitError(RuntimeError):
    def __init__(self, code, message, retry_after):
        super().__init__(message)
        self.code = code
        self.message = message
        self.retry_after = max(1, int(retry_after))


@dataclass(frozen=True)
class UsageGrant:
    lease_id: str
    client_id: str
    signed_client_id: str


class AIUsagePolicy:
    def __init__(
        self,
        runtime_db,
        secret_key,
        global_daily_limit,
        daily_limit=3,
        rate_limit=3,
        max_concurrent=4,
        lease_seconds=150,
    ):
        self.runtime_db = runtime_db
        self.secret_key = secret_key
        self.global_daily_limit = global_daily_limit
        self.daily_limit = daily_limit
        self.rate_limit = rate_limit
        self.max_concurrent = max_concurrent
        self.lease_seconds = lease_seconds
        self.serializer = URLSafeSerializer(secret_key, salt="zgs-ai-device")
        self._init_db()

    def _init_db(self):
        with sqlite_connection(self.runtime_db) as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS ai_daily_usage (
                    scope TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    usage_date TEXT NOT NULL,
                    request_count INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (scope, subject, usage_date)
                );
                CREATE TABLE IF NOT EXISTS ai_rate_usage (
                    scope TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    window_start INTEGER NOT NULL,
                    request_count INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (scope, subject, window_start)
                );
                CREATE TABLE IF NOT EXISTS ai_leases (
                    lease_id TEXT PRIMARY KEY,
                    device_subject TEXT NOT NULL,
                    expires_at INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS ai_bonus_grants (
                    device_subject TEXT NOT NULL,
                    usage_date TEXT NOT NULL,
                    grant_count INTEGER NOT NULL DEFAULT 0,
                    source TEXT NOT NULL,
                    PRIMARY KEY (device_subject, usage_date, source)
                );
                """
            )

    def resolve_client(self, signed_client_id=None):
        client_id = None
        if signed_client_id:
            try:
                candidate = self.serializer.loads(signed_client_id)
                if isinstance(candidate, str) and len(candidate) == 32:
                    client_id = candidate
            except BadSignature:
                pass
        client_id = client_id or uuid.uuid4().hex
        return client_id, self.serializer.dumps(client_id)

    def _subject(self, scope, value):
        digest = hmac.new(
            self.secret_key.encode("utf-8"),
            f"{scope}:{value}".encode(),
            hashlib.sha256,
        ).hexdigest()
        return digest

    @staticmethod
    def _retry_until_tomorrow(now):
        tomorrow = (now + timedelta(days=1)).date()
        reset = datetime.combine(tomorrow, datetime.min.time(), tzinfo=SHANGHAI)
        return (reset - now).total_seconds()

    def acquire(self, client_id, ip_address, now=None):
        now = (now or datetime.now(SHANGHAI)).astimezone(SHANGHAI)
        usage_date = now.date().isoformat()
        timestamp = int(now.timestamp())
        window_start = timestamp - timestamp % 60
        device_subject = self._subject("device", client_id)
        ip_subject = self._subject("ip", ip_address or "unknown")
        lease_id = uuid.uuid4().hex

        with sqlite_connection(self.runtime_db) as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("DELETE FROM ai_leases WHERE expires_at <= ?", (timestamp,))
            connection.execute(
                "DELETE FROM ai_rate_usage WHERE window_start < ?", (window_start - 120,)
            )

            daily_count = self._count_daily(connection, "device", device_subject, usage_date)
            bonus_count = connection.execute(
                """
                SELECT COALESCE(SUM(grant_count), 0) FROM ai_bonus_grants
                WHERE device_subject = ? AND usage_date = ?
                """,
                (device_subject, usage_date),
            ).fetchone()[0]
            if daily_count >= self.daily_limit + bonus_count:
                raise UsageLimitError(
                    "AI_DAILY_QUOTA_EXHAUSTED",
                    "今日免费论命次数已用完",
                    self._retry_until_tomorrow(now),
                )

            global_count = self._count_daily(connection, "global", "all", usage_date)
            if self.global_daily_limit is not None and global_count >= self.global_daily_limit:
                raise UsageLimitError(
                    "AI_GLOBAL_QUOTA_EXHAUSTED",
                    "今日分析服务额度已用完",
                    self._retry_until_tomorrow(now),
                )

            for scope, subject in (("device", device_subject), ("ip", ip_subject)):
                rate_count = connection.execute(
                    """
                    SELECT request_count FROM ai_rate_usage
                    WHERE scope = ? AND subject = ? AND window_start = ?
                    """,
                    (scope, subject, window_start),
                ).fetchone()
                if rate_count and rate_count[0] >= self.rate_limit:
                    raise UsageLimitError(
                        "AI_RATE_LIMITED", "请求过于频繁，请稍后再试", 60 - timestamp % 60
                    )

            device_concurrent = connection.execute(
                "SELECT COUNT(*) FROM ai_leases WHERE device_subject = ?", (device_subject,)
            ).fetchone()[0]
            global_concurrent = connection.execute("SELECT COUNT(*) FROM ai_leases").fetchone()[0]
            if device_concurrent >= 1 or global_concurrent >= self.max_concurrent:
                raise UsageLimitError("AI_CONCURRENCY_LIMITED", "分析服务繁忙，请稍后再试", 5)

            self._increment_daily(connection, "device", device_subject, usage_date)
            self._increment_daily(connection, "global", "all", usage_date)
            for scope, subject in (("device", device_subject), ("ip", ip_subject)):
                connection.execute(
                    """
                    INSERT INTO ai_rate_usage (scope, subject, window_start, request_count)
                    VALUES (?, ?, ?, 1)
                    ON CONFLICT(scope, subject, window_start)
                    DO UPDATE SET request_count=request_count + 1
                    """,
                    (scope, subject, window_start),
                )
            connection.execute(
                "INSERT INTO ai_leases VALUES (?, ?, ?)",
                (lease_id, device_subject, timestamp + self.lease_seconds),
            )

        return UsageGrant(lease_id, client_id, self.serializer.dumps(client_id))

    @staticmethod
    def _count_daily(connection, scope, subject, usage_date):
        row = connection.execute(
            """
            SELECT request_count FROM ai_daily_usage
            WHERE scope = ? AND subject = ? AND usage_date = ?
            """,
            (scope, subject, usage_date),
        ).fetchone()
        return row[0] if row else 0

    @staticmethod
    def _increment_daily(connection, scope, subject, usage_date):
        connection.execute(
            """
            INSERT INTO ai_daily_usage (scope, subject, usage_date, request_count)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(scope, subject, usage_date)
            DO UPDATE SET request_count=request_count + 1
            """,
            (scope, subject, usage_date),
        )

    def release(self, lease_id):
        with sqlite_connection(self.runtime_db) as connection:
            connection.execute("DELETE FROM ai_leases WHERE lease_id = ?", (lease_id,))

    def add_bonus(self, client_id, count, source="advertisement"):
        if count < 1:
            raise ValueError("bonus count must be positive")
        usage_date = datetime.now(SHANGHAI).date().isoformat()
        subject = self._subject("device", client_id)
        with sqlite_connection(self.runtime_db) as connection:
            connection.execute(
                """
                INSERT INTO ai_bonus_grants (device_subject, usage_date, grant_count, source)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(device_subject, usage_date, source)
                DO UPDATE SET grant_count=grant_count + excluded.grant_count
                """,
                (subject, usage_date, count, source),
            )

    def check_ready(self):
        try:
            with sqlite_connection(self.runtime_db) as connection:
                return connection.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        except sqlite3.Error:
            return False
