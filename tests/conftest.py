from pathlib import Path

import pytest

from app import create_app
from scripts.build_reference_db import build_reference_database

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def reference_db(tmp_path_factory):
    output = tmp_path_factory.mktemp("reference") / "reference.db"
    build_reference_database(
        output,
        ROOT / "data" / "reference" / "kanxi_dict.db",
        ROOT / "data" / "reference" / "zhugeshenshuan_jq.xlsx",
        ROOT / "data" / "reference" / "pzbj.json",
    )
    return output


@pytest.fixture()
def app(tmp_path, reference_db):
    application = create_app(
        {
            "TESTING": True,
            "AI_API_KEY": "",
            "AI_GLOBAL_DAILY_LIMIT": 100,
            "REFERENCE_DB_PATH": reference_db,
            "RUNTIME_DB_PATH": tmp_path / "runtime.db",
        }
    )
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()
