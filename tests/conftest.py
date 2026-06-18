from pathlib import Path

import pytest

from app import create_app

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def app(tmp_path):
    application = create_app(
        {
            "TESTING": True,
            "AI_API_KEY": "",
            "HUANGLI_DB_PATH": tmp_path / "huangli.db",
            "HANZI_DB_PATH": ROOT / "database" / "kanxi_dict.db",
            "GUA_DATA_PATH": ROOT / "database" / "zhugeshenshuan_jq.xlsx",
            "PZBJ_DATA_PATH": ROOT / "database" / "pzbj.json",
        }
    )
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()
