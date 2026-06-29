import fs from "node:fs/promises";
import path from "node:path";

import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

function parseArgs(argv) {
  const values = {};
  for (let index = 2; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!key?.startsWith("--") || value === undefined) {
      throw new Error(`参数格式错误：${key ?? "<missing>"}`);
    }
    values[key.slice(2)] = value;
  }
  for (const required of ["input", "output", "preview-dir"]) {
    if (!values[required]) {
      throw new Error(`缺少参数 --${required}`);
    }
  }
  return values;
}

function terminationLabel(sign) {
  if (sign.termination_reason === "placeholder") {
    return `空位终止（○@${sign.termination_index}）`;
  }
  return "字典末尾终止";
}

function roleLabel(role) {
  return {
    leading_placeholder: "前导空位",
    character: "签文字符",
    terminator: "终止符",
  }[role];
}

function setHeaderStyle(range) {
  range.format = {
    fill: "#5B4636",
    font: { bold: true, color: "#FFFFFF" },
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "inside", style: "thin", color: "#D8C9B8" },
  };
}

function setBodyStyle(range) {
  range.format = {
    verticalAlignment: "center",
    borders: {
      insideHorizontal: { style: "thin", color: "#E8DED3" },
    },
  };
}

const args = parseArgs(process.argv);
const document = JSON.parse(await fs.readFile(args.input, "utf8"));
const { metadata, signs } = document;
if (!Array.isArray(signs) || signs.length !== 384) {
  throw new Error(`预期 384 签，实际 ${signs?.length ?? 0}`);
}

const workbook = Workbook.create();
const rulesSheet = workbook.worksheets.add("规则说明");
const resultsSheet = workbook.worksheets.add("签文结果");
const evidenceSheet = workbook.worksheets.add("逐字证据");
const qualitySheet = workbook.worksheets.add("数据质量");

for (const sheet of [rulesSheet, resultsSheet, evidenceSheet, qualitySheet]) {
  sheet.showGridLines = false;
}

rulesSheet.mergeCells("A1:B1");
rulesSheet.getRange("A1").values = [["诸葛神算原始字表推导签文"]];
rulesSheet.getRange("A1:B1").format = {
  fill: "#3F3026",
  font: { bold: true, color: "#FFFFFF", size: 16 },
  horizontalAlignment: "center",
  verticalAlignment: "center",
};
rulesSheet.getRange("A2:B12").values = [
  ["项目", "内容"],
  ["字表来源", metadata.source_file],
  ["字表格数", metadata.dictionary_cell_count],
  ["签文数量", metadata.sign_count],
  ["步长", metadata.step],
  ["起查位置", "签号 r，范围 1—384"],
  ["取字序列", "r、r+384、r+2×384……"],
  ["前导空位", "取得首字前遇 ○，继续加 384"],
  ["终止规则", "取得首字后遇 ○ 停止；字表用尽则以字典末尾终止"],
  ["标点策略", metadata.punctuation_policy],
  ["原稿算例", "第24签：意孜孜心戚戚要平安防出入"],
];
setHeaderStyle(rulesSheet.getRange("A2:B2"));
setBodyStyle(rulesSheet.getRange("A3:B12"));
rulesSheet.getRange("A3:A12").format.font = { bold: true, color: "#5B4636" };
rulesSheet.getRange("A1:B12").format.wrapText = true;
rulesSheet.getRange("A1:B12").format.autofitRows();
rulesSheet.getRange("A1:A12").format.columnWidthPx = 130;
rulesSheet.getRange("B1:B12").format.columnWidthPx = 560;
rulesSheet.getRange("1:1").format.rowHeightPx = 36;
rulesSheet.freezePanes.freezeRows(2);

const resultHeaders = [
  "签号",
  "字表推导原文",
  "字数",
  "起查位置",
  "首字位置",
  "前导空位数",
  "终止位置",
  "终止方式",
  "取字位置",
  "来源待核字数",
  "来源待核位置",
  "来源状态统计",
];
const resultRows = signs.map((sign) => [
  sign.sign_number,
  sign.raw_text,
  null,
  sign.start_index,
  sign.first_character_index,
  sign.leading_placeholder_count,
  sign.termination_index,
  terminationLabel(sign),
  sign.positions.join(" "),
  null,
  sign.review_positions.join(" "),
  Object.entries(sign.source_status_counts)
    .map(([status, count]) => `${status}:${count}`)
    .join("; "),
]);
resultsSheet.getRange("A1:L1").values = [resultHeaders];
resultsSheet.getRange(`A2:L${signs.length + 1}`).values = resultRows;
resultsSheet.getRange("C2").formulas = [["=LEN(B2)"]];
resultsSheet.getRange(`C2:C${signs.length + 1}`).fillDown();

const evidenceRows = [];
for (const sign of signs) {
  for (const item of sign.evidence) {
    evidenceRows.push([
      sign.sign_number,
      item.character_order,
      item.global_index,
      item.value,
      roleLabel(item.role),
      item.status,
      item.confidence,
      item.file,
      item.page_range,
      item.column,
      item.row,
      item.cell_id,
      item.needs_review ? "是" : "否",
    ]);
  }
}
const evidenceHeaders = [
  "签号",
  "字序",
  "字表位置",
  "字符",
  "角色",
  "来源状态",
  "置信度",
  "来源文件",
  "百字范围",
  "列",
  "行",
  "格号",
  "需核",
];
evidenceSheet.getRange("A1:M1").values = [evidenceHeaders];
evidenceSheet.getRange(`A2:M${evidenceRows.length + 1}`).values = evidenceRows;

const evidenceLastRow = evidenceRows.length + 1;
resultsSheet.getRange("J2").formulas = [
  [
    `=COUNTIFS('逐字证据'!$A$2:$A$${evidenceLastRow},A2,'逐字证据'!$M$2:$M$${evidenceLastRow},"是")`,
  ],
];
resultsSheet.getRange(`J2:J${signs.length + 1}`).fillDown();

setHeaderStyle(resultsSheet.getRange("A1:L1"));
setBodyStyle(resultsSheet.getRange(`A2:L${signs.length + 1}`));
resultsSheet.getRange(`A2:A${signs.length + 1}`).format.numberFormat = "0";
resultsSheet.getRange(`C2:G${signs.length + 1}`).format.numberFormat = "0";
resultsSheet.getRange(`J2:J${signs.length + 1}`).format.numberFormat = "0";
resultsSheet.getRange(`B2:B${signs.length + 1}`).format.wrapText = true;
resultsSheet.getRange(`L2:L${signs.length + 1}`).format.wrapText = true;
resultsSheet.freezePanes.freezeRows(1);
resultsSheet.getRange(`A1:A${signs.length + 1}`).format.columnWidthPx = 60;
resultsSheet.getRange(`B1:B${signs.length + 1}`).format.columnWidthPx = 330;
resultsSheet.getRange(`C1:G${signs.length + 1}`).format.columnWidthPx = 90;
resultsSheet.getRange(`H1:H${signs.length + 1}`).format.columnWidthPx = 180;
resultsSheet.getRange(`I1:I${signs.length + 1}`).format.columnWidthPx = 440;
resultsSheet.getRange(`J1:J${signs.length + 1}`).format.columnWidthPx = 110;
resultsSheet.getRange(`K1:K${signs.length + 1}`).format.columnWidthPx = 220;
resultsSheet.getRange(`L1:L${signs.length + 1}`).format.columnWidthPx = 340;
resultsSheet.tables.add(`A1:L${signs.length + 1}`, true, "OriginalOracleSigns");

setHeaderStyle(evidenceSheet.getRange("A1:M1"));
setBodyStyle(evidenceSheet.getRange(`A2:M${evidenceRows.length + 1}`));
evidenceSheet.getRange(`A2:C${evidenceRows.length + 1}`).format.numberFormat = "0";
evidenceSheet.getRange(`G2:G${evidenceRows.length + 1}`).format.numberFormat = "0.000000";
evidenceSheet.freezePanes.freezeRows(1);
evidenceSheet.getRange(`A1:C${evidenceRows.length + 1}`).format.columnWidthPx = 90;
evidenceSheet.getRange(`D1:D${evidenceRows.length + 1}`).format.columnWidthPx = 60;
evidenceSheet.getRange(`E1:E${evidenceRows.length + 1}`).format.columnWidthPx = 120;
evidenceSheet.getRange(`F1:F${evidenceRows.length + 1}`).format.columnWidthPx = 180;
evidenceSheet.getRange(`G1:G${evidenceRows.length + 1}`).format.columnWidthPx = 100;
evidenceSheet.getRange(`H1:H${evidenceRows.length + 1}`).format.columnWidthPx = 180;
evidenceSheet.getRange(`I1:I${evidenceRows.length + 1}`).format.columnWidthPx = 110;
evidenceSheet.getRange(`J1:M${evidenceRows.length + 1}`).format.columnWidthPx = 70;
evidenceSheet.tables.add(`A1:M${evidenceRows.length + 1}`, true, "OriginalOracleEvidence");

const statusEntries = Object.entries(metadata.dictionary_status_counts);
qualitySheet.getRange("A1:B1").values = [["指标", "数值"]];
qualitySheet.getRange("A2:B10").values = [
  ["字表总格数", metadata.dictionary_cell_count],
  ["空位格数", metadata.dictionary_placeholder_count],
  ["签文总数", metadata.sign_count],
  ["空位终止签数", metadata.termination_counts.placeholder ?? 0],
  ["字典末尾终止签数", metadata.termination_counts.dictionary_end ?? 0],
  ["最短签文字数", metadata.minimum_character_count],
  ["最长签文字数", metadata.maximum_character_count],
  ["含来源待核字位的签数", metadata.review_sign_count],
  ["推导证据行数", evidenceRows.length],
];
qualitySheet.getRange("D1:E1").values = [["来源状态", "字表格数"]];
qualitySheet.getRange(`D2:E${statusEntries.length + 1}`).values = statusEntries;
setHeaderStyle(qualitySheet.getRange("A1:B1"));
setHeaderStyle(qualitySheet.getRange("D1:E1"));
setBodyStyle(qualitySheet.getRange("A2:B10"));
setBodyStyle(qualitySheet.getRange(`D2:E${statusEntries.length + 1}`));
qualitySheet.getRange("A1:A10").format.columnWidthPx = 190;
qualitySheet.getRange("B1:B10").format.columnWidthPx = 110;
qualitySheet.getRange(`D1:D${statusEntries.length + 1}`).format.columnWidthPx = 190;
qualitySheet.getRange(`E1:E${statusEntries.length + 1}`).format.columnWidthPx = 110;
qualitySheet.freezePanes.freezeRows(1);

const resultInspection = await workbook.inspect({
  kind: "table",
  sheetId: "签文结果",
  range: "A1:L8",
  include: "values,formulas",
  tableMaxRows: 8,
  tableMaxCols: 12,
  maxChars: 7000,
});
console.log(resultInspection.ndjson);

const errorInspection = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
  maxChars: 3000,
});
console.log(errorInspection.ndjson);

await fs.mkdir(args["preview-dir"], { recursive: true });
const previews = [
  ["规则说明", "A1:B12", "rules.png"],
  ["签文结果", "A1:L22", "results.png"],
  ["逐字证据", "A1:M22", "evidence.png"],
  ["数据质量", "A1:E10", "quality.png"],
];
for (const [sheetName, range, filename] of previews) {
  const preview = await workbook.render({ sheetName, range, scale: 1.5, format: "png" });
  await fs.writeFile(
    path.join(args["preview-dir"], filename),
    new Uint8Array(await preview.arrayBuffer()),
  );
}

await fs.mkdir(path.dirname(args.output), { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(args.output);
console.log(
  JSON.stringify({ output: args.output, signs: signs.length, evidence_rows: evidenceRows.length }),
);
