"""把 md 和 json 输出文件按签号顺序重新排列。

背景：retry-failed 会把重跑的签文追加到 md 文件末尾，导致签号顺序错乱。
      json 文件的 append 也会让顺序不对。本脚本按 sign_number 升序重排两个文件。

操作：
  1. 读取 json，按 sign_number 排序后重写
  2. 读取 md，按签号顺序重排章节后重写
"""

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
JSON_FILE = PROJECT_ROOT / "data" / "content" / "oracle_signs_reinterpreted.json"
MD_FILE = PROJECT_ROOT / "data" / "content" / "oracle_signs_reinterpreted.md"


def sort_json():
    """按 sign_number 升序重排 json 文件。"""
    data = json.loads(JSON_FILE.read_text(encoding="utf-8"))
    before_order = [d["sign_number"] for d in data]
    data.sort(key=lambda d: d["sign_number"])
    after_order = [d["sign_number"] for d in data]

    JSON_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    moved = sum(
        1 for i, (a, b) in enumerate(zip(before_order, after_order, strict=False)) if a != b
    )
    print(f"[JSON] 总签数: {len(data)}, 排序后位置变动: {moved}")
    print(f"[JSON] 首签: 第{after_order[0]}签, 末签: 第{after_order[-1]}签")
    return len(data)


def sort_md():
    """按签号升序重排 md 文件的章节。"""
    content = MD_FILE.read_text(encoding="utf-8")

    # 提取文件头部（第一个 "## 第N签" 之前的内容）
    first_sign_match = re.search(r"^##\s*第\s*\d+\s*签", content, re.MULTILINE)
    if not first_sign_match:
        print("[MD] 未找到任何签文章节")
        return 0

    header = content[: first_sign_match.start()]

    # 按签号章节切分（每个章节从 "## 第N签" 开始到下一个 "## 第" 或文件末尾）
    # 用 split 保留分隔符
    sections = re.split(
        r"(?=^##\s*第\s*\d+\s*签)", content[first_sign_match.start() :], flags=re.MULTILINE
    )
    sections = [s for s in sections if s.strip()]

    # 提取签号并按签号排序
    def get_sign_number(section):
        match = re.search(r"##\s*第\s*(\d+)\s*签", section)
        return int(match.group(1)) if match else 0

    sections.sort(key=get_sign_number)

    # 重新拼接
    new_content = header + "".join(sections)
    MD_FILE.write_text(new_content, encoding="utf-8")

    sign_numbers = [get_sign_number(s) for s in sections]
    print(
        f"[MD] 总章节: {len(sections)}, 首签: 第{sign_numbers[0]}签, 末签: 第{sign_numbers[-1]}签"
    )

    # 验证连续性
    expected = list(range(1, len(sections) + 1))
    if sign_numbers == expected:
        print(f"[MD] 签号连续性: OK (1-{len(sections)} 连续)")
    else:
        missing = set(expected) - set(sign_numbers)
        extra = set(sign_numbers) - set(expected)
        print(f"[MD] 签号连续性: 异常 | 缺失: {sorted(missing)} | 多余: {sorted(extra)}")

    return len(sections)


def main():
    print("=" * 60)
    print("重排解签输出文件（按签号升序）")
    print("=" * 60)

    json_count = sort_json()
    print()
    md_count = sort_md()

    print()
    print("=" * 60)
    if json_count == md_count:
        print(f"完成：JSON {json_count} 条，MD {md_count} 章，数量一致")
    else:
        print(f"警告：JSON {json_count} 条 ≠ MD {md_count} 章，数量不一致")
    print("=" * 60)


if __name__ == "__main__":
    main()
