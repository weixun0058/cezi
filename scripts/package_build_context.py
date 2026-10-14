"""按 .dockerignore 打包 Docker 构建上下文，用于在生产服务器上构建镜像。

本地到生产服务器的跨境上行带宽很低，上传 100 MB 以上的镜像 tar 需要二十分钟以上；
改为上传按 .dockerignore 过滤后的源码包（约 17 MB），在服务器上执行 docker build。
过滤规则与 docker build 一致：按顺序匹配、后出现的规则优先，`!` 重新包含，
`**` 匹配任意层目录，规则命中父目录时其下文件一并排除。

输出前会再次检查文件名，发现 .env 或凭据类文件进入构建上下文时拒绝打包。

用法：
  python scripts/package_build_context.py zhugeshensuan-4.1.6-analytics-context.tar.gz
"""

import argparse
import os
import posixpath
import re
import sys
import tarfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
FORBIDDEN_PATTERNS = (
    re.compile(r"(?:^|/)\.env(?:\.(?!example$)[^/]+)?$"),
    re.compile(r"(?:^|/)client_secret[^/]*\.json$", re.IGNORECASE),
    re.compile(r"\.(?:pem|key|p12)$", re.IGNORECASE),
    re.compile(r"令牌|token[^/]*\.txt$", re.IGNORECASE),
)


def _compile(pattern):
    regex = []
    index = 0
    while index < len(pattern):
        if pattern.startswith("**/", index):
            regex.append("(?:.*/)?")
            index += 3
        elif pattern.startswith("**", index):
            regex.append(".*")
            index += 2
        elif pattern[index] == "*":
            regex.append("[^/]*")
            index += 1
        elif pattern[index] == "?":
            regex.append("[^/]")
            index += 1
        else:
            regex.append(re.escape(pattern[index]))
            index += 1
    return re.compile("".join(regex) + r"\Z")


def parse_dockerignore(text):
    """返回按出现顺序排列的 (是否为 ! 规则, 规范化规则, 正则) 列表。"""
    rules = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        negated = line.startswith("!")
        if negated:
            line = line[1:].strip()
        if "[" in line or "\\" in line:
            raise ValueError(f"不支持的 .dockerignore 规则：{raw_line}")
        pattern = posixpath.normpath(line.lstrip("/"))
        rules.append((negated, pattern, _compile(pattern)))
    return rules


def is_excluded(relative_path, rules):
    """规则命中路径本身或任一父目录即生效，最后一条命中的规则决定结果。"""
    parts = relative_path.split("/")
    candidates = ["/".join(parts[:count]) for count in range(1, len(parts) + 1)]
    excluded = False
    for negated, _, regex in rules:
        if any(regex.match(candidate) for candidate in candidates):
            excluded = not negated
    return excluded


def _may_reinclude_below(relative_dir, rules):
    for negated, pattern, _ in rules:
        if not negated:
            continue
        if "*" in pattern or "?" in pattern:
            return True
        if pattern == relative_dir or pattern.startswith(relative_dir + "/"):
            return True
    return False


def collect_files(root, rules):
    """返回构建上下文中的文件相对路径（POSIX 分隔符，已排序）。"""
    root = Path(root)
    files = []
    for directory, dirnames, filenames in os.walk(root):
        relative_dir = Path(directory).relative_to(root).as_posix()
        prefix = "" if relative_dir == "." else relative_dir + "/"
        dirnames[:] = sorted(
            name
            for name in dirnames
            if not is_excluded(prefix + name, rules) or _may_reinclude_below(prefix + name, rules)
        )
        files.extend(
            prefix + name for name in sorted(filenames) if not is_excluded(prefix + name, rules)
        )
    return files


def find_forbidden(files):
    return [path for path in files if any(rule.search(path) for rule in FORBIDDEN_PATTERNS)]


def _normalize(info):
    info.uid = info.gid = 0
    info.uname = info.gname = "root"
    info.mode = 0o755 if info.isdir() else 0o644
    return info


def write_archive(root, files, output):
    root = Path(root)
    with tarfile.open(output, "w:gz") as archive:
        for relative in files:
            archive.add(root / relative, arcname=relative, recursive=False, filter=_normalize)


def main(argv=None, project=PROJECT):
    parser = argparse.ArgumentParser(description="按 .dockerignore 打包 Docker 构建上下文")
    parser.add_argument("output", type=Path, help="输出的 .tar.gz 文件路径")
    args = parser.parse_args(argv)

    project = Path(project)
    rules = parse_dockerignore((project / ".dockerignore").read_text(encoding="utf-8"))
    output = args.output.resolve()
    files = [path for path in collect_files(project, rules) if (project / path).resolve() != output]
    leaked = find_forbidden(files)
    if leaked:
        print("拒绝打包：以下文件须先在 .dockerignore 中排除：", file=sys.stderr)
        for path in leaked:
            print(f"  {path}", file=sys.stderr)
        return 1

    write_archive(project, files, output)
    size_mb = output.stat().st_size / 1_000_000
    print(f"已打包 {len(files)} 个文件，{size_mb:.1f} MB -> {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
