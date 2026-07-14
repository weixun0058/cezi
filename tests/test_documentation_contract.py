from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path):
    return (ROOT / path).read_text(encoding="utf-8-sig")


def test_public_language_contract_is_documented():
    readme = _read("README.md")
    product_spec = _read("docs/business/wise-oracle-english-product-spec.md")

    assert "公开语言切换器只展示繁体中文和英文" in readme
    assert "`/zh-hans/*`" in readme
    assert "`/huangli`、`/suanshi`、`/lunming` 固定 301 到对应繁体页面" in readme
    assert "`/zh-hant/almanac`、`/zh-hant/divination`、`/zh-hant/bazi`" in product_spec


def test_english_almanac_and_pillar_contracts_are_documented():
    readme = _read("README.md")
    api_doc = _read("docs/API文档.md")
    product_spec = _read("docs/business/wise-oracle-english-product-spec.md")

    assert "英文 `/api/en/week-almanac` 返回 10 日" in readme
    assert "10 条英文黄历记录" in api_doc
    assert "固定返回 10 日" in product_spec
    assert "共九天的英文黄历" not in api_doc
    assert "四柱拼音" not in api_doc
    assert "Yang Metal Horse" in api_doc
    assert "Geng-Wu" in api_doc
    assert api_doc.count("### `POST /api/en/oracle/ask`") == 1
    assert api_doc.count("### `POST /api/en/birth-chart/analyze`") == 1
    assert "不再输出 `Jia-Zi`、`Geng-Wu`" in product_spec


def test_json_runtime_data_boundary_is_documented():
    agent_doc = _read("Agent.md")
    architecture = _read("docs/architecture/data-source-migration-2026-07-13.md")
    project_structure = _read("docs/PROJECT_STRUCTURE.md")
    reprocess_script = _read("scripts/reprocess_single_sign.py")
    adjudicate_script = _read("scripts/adjudicate_single_sign.py")

    assert "运行时只读取 `hanzi` 笔画表" in agent_doc
    assert "禁止运行 `backfill_reinterpreted_to_db.py`" in agent_doc
    assert "应用运行时不读取这些表" in architecture
    assert "旧签文/彭祖百忌表只用于历史构建产物可重建" in project_structure
    assert "如需同步数据库" not in reprocess_script
    assert "如需同步数据库" not in adjudicate_script


def test_deployment_commands_use_current_workspace_layout():
    deployment = _read("docs/部署指南.md")

    assert r"V:\诸葛神算V3" not in deployment
    assert r"V:\诸葛神算V4" in deployment
    assert r".\deploy\compose.prod.yml" in deployment
    assert "docker build -f deploy/Dockerfile" in deployment
