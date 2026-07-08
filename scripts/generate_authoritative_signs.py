"""生成权威签文文本文件（简体+繁体）。

数据源：
  - data/reference/zhugeshenshuan_jq.xlsx  简体，有标点（基础框架）
  - data/reference/original_oracle_signs.csv  繁体，无标点（底本，保留异体字）

简体生成策略：
  以 xlsx 为基础，应用 A/B/C 类文字修正 + 标点修订

繁体生成策略（不使用 s2t 转换，保留底本异体字）：
  1. 以 CSV 底本繁体原文为基础（保留异体字如「盃」「啣」「軛」等）
  2. 将简体权威文本的标点模式转移到繁体原文上
  3. 对少数签（文字与底本不同）手动指定繁体文本

修正分类：
  - A类（13签）：回退到 CSV 底本文字（部分签混合裁定，如213）
  - B类（9签）：采用第三方考据文字
  - C类特殊（1签）：260签简体「轮回」/繁体「輪廻」
  - 标点修订（3签）：文字不变，仅调整标点
  - 二轮校勘（4签）：85/167/216/256，删除乱码/多余标点/修正录入错误

输出：
  - data/reference/oracle_signs_authoritative_sc.csv  简体权威文本
  - data/reference/oracle_signs_authoritative_tc.csv  繁体权威文本
"""
import csv
from pathlib import Path

import openpyxl
from opencc import OpenCC

XLSX_PATH = Path("data/reference/zhugeshenshuan_jq.xlsx")
CSV_PATH = Path("data/reference/original_oracle_signs.csv")
SC_OUTPUT = Path("data/reference/oracle_signs_authoritative_sc.csv")
TC_OUTPUT = Path("data/reference/oracle_signs_authoritative_tc.csv")

PUNCTUATION = set('，。、；：""''""''！？·…—（）()[]【】《》〈〉「」『』 \n\r\t.,;:!?\'"')

# OpenCC t2s 不识别的异体字补充映射（csv底本字 → 对应简体字）
# 这些字 t2s 转换后不等于简体字，但实为异体字，应保留底本原貌
# 依据 scripts/check_variants.py 诊断结果人工筛选
VARIANT_TO_SIMP = {
    '啣': '衔', '凟': '渎', '疴': '痾', '歛': '敛', '尅': '克',
    '濶': '阔', '嚦': '唳', '氷': '冰', '妬': '妒', '覩': '睹',
    '朶': '朵', '兎': '兔', '沈': '沉', '麟': '鳞',
}

# A类（13签，回退到CSV底本）+ B类（9签，第三方考据）+ C类特殊（260签）
# + 二轮校勘（4签）
# 文字修正（含标点）
TEXT_FIXES = {
    # === A类：回退到CSV底本 ===
    124: "宝镜亲照两人，心中结，合同心。",
    144: "一重水一重山，风波道坦然，壶中别有天。",
    146: "船棹中流急，花开春又逢，事宁心不静，惹起许多疑。",
    192: "事若羁留，人不出头，往来闭塞，要见无有。",
    212: "望去几重山，高深渐可攀，举头天上看，明月出人间。",
    213: "用之则行，舍之则藏，一骑出重门，佳音咫尺间。",
    226: "佳信至，开笑颜，飞腾一去，披云上天。",
    235: "道路在招呼，风波一点无，时乖心绪乱，全仗贵人扶。",
    263: "数尾金鱼吞饵，丝竿钓了回头，家食翻嫌太费，五湖四海遨游。",
    276: "来去原无定处，时来时去安身，跋涉无虞，荣辱不计。",
    302: "闲云野鹤望东行，惟有乡人便是知音，经营布置两三春，联街灯火后，锦片前程。",
    320: "风起西南，红日当天，奇门妙诀，一掌能看。",
    331: "山穷路转迷，水急舟难渡，万事莫强为，出处遭奸妒。",
    # === B类：第三方考据 ===
    # 注：14签「藏却拙」语序取CSV底本，但「蹉跎」保留xlsx原版
    # （CSV底本「嗟跎」为OCR误认，二轮校勘纠正）
    14:  "鼎沸起风波，孤舟要渡河，巧中藏却拙，人事转蹉跎。",
    96:  "可以寄百里之命，可以托六尺之孤，钟期既遇毋迟误。笑呼呼，他乡聚首，各自乐康。",
    142: "利在中邦出战征，一番获丑在王庭，凤衔丹诏归阳畔，得享佳名四海荣。",
    313: "耕牛伏轭，辟土开疆，坐看收获，黍稷稻梁。",
    332: "时变多艰，战战兢兢，戒谨恐惧，如履薄冰，须识前程危与险，一笼风里一枝灯。",
    366: "此去万里程，却遇知音，同心共济，大立勋名。",
    373: "世界似清宁，不知辞已休，打叠要小心，须防遭火毒。",
    380: "疏食饮水，乐在其中，膏粱美味，反使心朦。",
    382: "蛇可化龙，头角将出，平地一声雷轰，方显龙蛇力。",
    # === C类特殊：260签 ===
    # 简体取「轮回」，繁体取「輪廻」（非OpenCC默认的「輪迴」）
    # 保留「免」字：轮回不能免，永落深坑堑
    260: "终身不习上，在世却枉然，轮回不能免，永落深坑堑。",
    # === 二轮校勘（繁体CSV审查后发现的新问题）===
    # 85签：删除OCR乱码「??」（CSV底本为「展愁眉」无乱码）
    85:  "倾一杯，展愁眉，天地合，好思为。",
    # 167签：删除多余右括号「）」（无匹配左括号）
    167: "大事可成功，有益还无咎，云中执鞭人，报在三秋后。",
    # 216签：删除OCR乱码「??」（CSV底本为「朱衣臨日月」无乱码）
    216: "门内起干戈，亲仇两不和，朱衣临日月，始觉笑呵呵。",
    # 256签：「南北」→「南地」（xlsx多录一个「北」字，底本为「东南地」）
    256: "东南地将来成故墟，燕蓟地苍生无存济，若要大奋雄心，水源不知何处？",
}

# 标点修订（3签，文字不变）
PUNCT_FIXES = {
    4:  "春花娇媚，不禁雨打风飘；秋菊幽芳，反耐霜凌雪傲。",
    25: "见不见，也防人背面；遇不遇，到底无凭据。",
    26: "一番桃李一番春，谁识当初气象新。林下水边寻活计，见山了了称心意。",
}

# 繁体手动覆盖（逃生口）
# 标点转移法已能区分「异体字（保留底本）」与「OCR错误（用s2t修正）」，
# 仅当字符数不一致无法标点转移、且需保留异体字时才需手动指定。
TC_OVERRIDES = {
    # 260签：CSV底本缺「免」字（19字vs简体20字），无法标点转移；
    # 且需保留异体字「廻」（s2t 会标准化为「迴」），故手动指定
    260: "終身不習上，在世卻枉然，輪廻不能免，永落深坑塹。",
}


def load_xlsx_signs():
    """从 xlsx 读取所有签文（第 4 列，含标点）。"""
    wb = openpyxl.load_workbook(XLSX_PATH, read_only=True, data_only=True)
    ws = wb["Sheet1"]
    signs = {}
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue
        sn = row[0]
        if sn is not None:
            signs[int(sn)] = str(row[3]).strip()
    wb.close()
    return signs


def load_csv_signs():
    """从 CSV 底本读取繁体原文（raw_text 字段，无标点）。"""
    signs = {}
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            signs[int(row["sign_number"])] = row["raw_text"].strip()
    return signs


def transfer_punct(sc_text, tc_no_punct, s2t, t2s):
    """将简体文本的标点转移到繁体原文上，保留异体字、修正OCR错误。

    输入：
      sc_text: 简体文本（含标点）
      tc_no_punct: CSV底本繁体原文（无标点）
      s2t, t2s: OpenCC 转换器
    输出：繁体文本（含标点），或 None（如果字符数不一致）

    原理：逐字遍历简体文本。
      - 标点：直接复制
      - 文字：从CSV底本按序取字 tc_char
        * 若 t2s(tc_char) == 简体字：异体字或同字，保留 tc_char（保持原文权威性）
        * 若 t2s(tc_char) != 简体字：CSV底本可能为OCR错误或真正异文，
          用 s2t(简体字) 修正（避免把 OCR 错误当作"原文"保留）
    前提：简体去标点后的字符数 == 繁体原文字符数。
    """
    result = []
    tc_idx = 0
    for c in sc_text:
        if c in PUNCTUATION:
            result.append(c)
        else:
            if tc_idx < len(tc_no_punct):
                tc_char = tc_no_punct[tc_idx]
                tc_idx += 1
                if t2s.convert(tc_char) == c or VARIANT_TO_SIMP.get(tc_char) == c:
                    result.append(tc_char)
                else:
                    result.append(s2t.convert(c))
            else:
                return None
    if tc_idx != len(tc_no_punct):
        return None
    return "".join(result)


def build_authoritative_sc(xlsx_signs):
    """构建权威简体签文。

    输入：xlsx 原始签文（含标点）
    输出：应用 A/B/C 类文字修正 + 标点修订后的简体签文
    """
    authoritative = {}
    for sn, text in xlsx_signs.items():
        if sn in TEXT_FIXES:
            authoritative[sn] = TEXT_FIXES[sn]
        elif sn in PUNCT_FIXES:
            authoritative[sn] = PUNCT_FIXES[sn]
        else:
            authoritative[sn] = text
    return authoritative


def build_authoritative_tc(sc_signs, csv_signs):
    """构建权威繁体签文（从CSV底本出发，保留异体字）。

    策略：
      1. TC_OVERRIDES 中的签：使用手动指定的繁体文本
      2. 其他签：从CSV底本读取繁体原文，将简体标点转移到繁体原文上
      3. 若字符数不一致（简繁文字有差异）：回退到 s2t 转换并警告

    输入：权威简体签文，CSV底本繁体原文
    输出：权威繁体签文（保留底本异体字）
    """
    converter = OpenCC("s2t")
    t2s = OpenCC("t2s")
    authoritative = {}
    fallback_warnings = []

    for sn, sc_text in sc_signs.items():
        if sn in TC_OVERRIDES:
            authoritative[sn] = TC_OVERRIDES[sn]
            continue

        tc_no_punct = csv_signs.get(sn, "")
        if not tc_no_punct:
            authoritative[sn] = converter.convert(sc_text)
            fallback_warnings.append((sn, "CSV底本无此签"))
            continue

        tc_text = transfer_punct(sc_text, tc_no_punct, converter, t2s)
        if tc_text is not None:
            authoritative[sn] = tc_text
        else:
            # 字符数不一致，回退到 s2t
            authoritative[sn] = converter.convert(sc_text)
            fallback_warnings.append((sn, f"字符数不一致(s2t回退)"))

    if fallback_warnings:
        print(f"警告: {len(fallback_warnings)} 签回退到 s2t 转换:")
        for sn, reason in fallback_warnings:
            print(f"  第 {sn} 签: {reason}")

    return authoritative


def write_csv(path, signs):
    """写入 CSV 文件（sign_number, sign_text 两列，utf-8-sig 编码）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sign_number", "sign_text"])
        for sn in sorted(signs):
            writer.writerow([sn, signs[sn]])


def main():
    xlsx_signs = load_xlsx_signs()
    csv_signs = load_csv_signs()
    print(f"xlsx 签数: {len(xlsx_signs)}")
    print(f"csv  底本签数: {len(csv_signs)}")

    sc_signs = build_authoritative_sc(xlsx_signs)
    tc_signs = build_authoritative_tc(sc_signs, csv_signs)

    # 验证修正是否生效
    all_fixes = set(list(TEXT_FIXES.keys()) + list(PUNCT_FIXES.keys()))
    changed = 0
    unchanged_warnings = []
    for sn in sorted(all_fixes):
        if sc_signs[sn] != xlsx_signs[sn]:
            changed += 1
        else:
            unchanged_warnings.append(sn)
    print(f"\n文字修正: {len(TEXT_FIXES)} 签（A类+B类+C类+二轮校勘）")
    print(f"标点修订: {len(PUNCT_FIXES)} 签")
    print(f"繁体覆盖: {len(TC_OVERRIDES)} 签")
    print(f"实际变化: {changed} 签")
    if unchanged_warnings:
        print(f"警告: 以下签修正后与原文本相同: {unchanged_warnings}")

    write_csv(SC_OUTPUT, sc_signs)
    write_csv(TC_OUTPUT, tc_signs)
    print(f"\n简体权威文本: {SC_OUTPUT}")
    print(f"繁体权威文本: {TC_OUTPUT}")

    # 抽样验证
    print("\n=== 修正抽样验证 ===")
    for sn in [4, 14, 25, 26, 41, 85, 96, 124, 142, 167, 211, 213, 216, 256, 260, 373, 382]:
        print(f"\n第 {sn} 签:")
        print(f"  原xlsx: {xlsx_signs[sn]}")
        print(f"  简体:   {sc_signs[sn]}")
        print(f"  繁体:   {tc_signs[sn]}")

    # 额外抽样：验证异体字保留
    print("\n=== 异体字保留验证 ===")
    for sn in [1, 8, 41, 85, 142, 211, 380]:
        print(f"\n第 {sn} 签:")
        print(f"  csv底本: {csv_signs.get(sn, '[无]')}")
        print(f"  繁体:    {tc_signs[sn]}")


if __name__ == "__main__":
    main()
