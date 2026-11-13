#!/usr/bin/env python3
"""問題の解答を手元で実行し、テストデータを確かめる。

    python3 scripts/solutions.py check [問題ID ...]
    python3 scripts/solutions.py answers 問題ID [--solution パス] [--overwrite]

check は solutions/accepted/ の解答が全テストに正解し、solutions/wrong/ の解答が
少なくとも1件で不正解になることを確かめる。answers は accepted の解答で .in から
.ans を作る。作成者が書いた解答だけを手元で実行するための道具で、CodeDeckの
サーバーでは実行しない。採点はJudge0が行い、ここでの時間計測は目安にすぎない。

依存はPython 3.10以降の標準ライブラリだけ。C/C++はgcc・g++、JavaScriptはnodeが
あれば実行し、なければ skip と表示する（--strict では失敗扱い）。
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGUAGES = {".py": "python", ".cpp": "cpp", ".c": "c", ".js": "javascript", ".d": "d", ".java": "java", ".rs": "rust", ".cs": "csharp", ".rb": "ruby", ".go": "go"}
# 同じ拡張子が複数ある場合、answers で既定にする言語の優先順。
PREFERENCE = ["python", "pypy3", "cpp", "c", "javascript", "d", "java", "rust", "csharp", "ruby", "go"]


def source_language(source: Path) -> str:
    return "pypy3" if source.name.endswith(".pypy3.py") else LANGUAGES.get(source.suffix, "")


@dataclass
class Result:
    verdict: str
    detail: str = ""


def normalize(text: str) -> str:
    """Judge0の既定比較に合わせ、各行末の空白と末尾の空行を無視する。"""
    return "\n".join(line.rstrip() for line in text.split("\n")).rstrip()


def find_problems() -> dict[str, Path]:
    """problems/ 以下のフォルダ構造から、問題ID（ディレクトリ名）と場所を集める。"""
    return {p.parent.name: p.parent for p in sorted((ROOT / "problems").rglob("problem.yaml"))}


def time_limit_ms(problem: Path) -> int:
    match = re.search(r"^timeLimitMs:\s*(\d+)\s*$", (problem / "problem.yaml").read_text(encoding="utf-8"), re.M)
    return int(match.group(1)) if match else 2000


def tests(problem: Path) -> list[tuple[Path, Path]]:
    pairs = []
    for group in ("sample", "secret"):
        for source in sorted((problem / "data" / group).glob("*.in")):
            pairs.append((source, source.with_suffix(".ans")))
    return pairs


def build(solution: Path, work: Path) -> tuple[list[str] | None, str]:
    """実行コマンドを返す。処理系がない場合は (None, 理由)。"""
    language = source_language(solution)
    if language == "python":
        return [sys.executable, "-I", str(solution)], ""
    if language in ("javascript", "pypy3", "ruby"):
        executable = {"javascript": "node", "pypy3": "pypy3", "ruby": "ruby"}[language]
        interpreter = shutil.which(executable)
        return ([interpreter, str(solution)], "") if interpreter else (None, executable + " not found")
    binary = work / (solution.stem + "-" + language)
    if language == "java":
        compiler, runtime = shutil.which("javac"), shutil.which("java")
        if not compiler or not runtime:
            return None, "javac and java are required"
        classes = work / (solution.stem + "-classes")
        classes.mkdir(exist_ok=True)
        command = [compiler, "-encoding", "UTF-8", "-d", str(classes), str(solution)]
        compiled = subprocess.run(command, capture_output=True, text=True)
        if compiled.returncode != 0:
            return [], compiled.stderr.strip()[-2000:]
        return [runtime, "-cp", str(classes), solution.stem], ""
    if language == "csharp":
        compiler, runtime = shutil.which("mcs"), shutil.which("mono")
        if not compiler or not runtime:
            return None, "mcs and mono are required"
        command = [compiler, "-out:" + str(binary), str(solution)]
    elif language == "d":
        compiler = shutil.which("dmd") or shutil.which("ldc2")
        if not compiler:
            return None, "dmd or ldc2 not found"
        command = [compiler, "-O", "-of=" + str(binary), str(solution)]
    else:
        executable = {"cpp": "g++", "c": "gcc", "rust": "rustc", "go": "go"}.get(language)
        compiler = shutil.which(executable) if executable else None
        if not compiler:
            return None, (executable or language) + " not found"
        if language == "go":
            command = [compiler, "build", "-o", str(binary), str(solution)]
        elif language == "rust":
            command = [compiler, "--edition=2021", "-O", "-o", str(binary), str(solution)]
        else:
            flags = ["-std=c++17", "-O2"] if language == "cpp" else ["-std=c11", "-O2"]
            command = [compiler, *flags, "-o", str(binary), str(solution)]
            if language == "c":
                command.append("-lm")
    compiled = subprocess.run(command, capture_output=True, text=True)
    if compiled.returncode != 0:
        return [], compiled.stderr.strip()[-2000:]
    return ([runtime, str(binary)] if language == "csharp" else [str(binary)]), ""


def run(command: list[str], source: Path, limit_ms: int) -> tuple[Result, str]:
    try:
        completed = subprocess.run(
            command,
            stdin=source.open("rb"),
            capture_output=True,
            timeout=max(1.0, limit_ms / 1000 * 2),
        )
    except subprocess.TimeoutExpired:
        return Result("TLE"), ""
    if completed.returncode != 0:
        return Result("RE", completed.stderr.decode("utf-8", "replace").strip()[-500:]), ""
    return Result("OK"), completed.stdout.decode("utf-8", "replace")


def solutions(problem: Path, group: str) -> list[Path]:
    return sorted(p for p in (problem / "solutions" / group).glob("*") if p.is_file() and source_language(p))


def check(problem: Path, strict: bool) -> bool:
    ok = True
    pairs = tests(problem)
    limit = time_limit_ms(problem)
    accepted = solutions(problem, "accepted")
    if not accepted:
        print(f"FAIL {problem.name}: solutions/accepted/ に解答がありません")
        return False
    with tempfile.TemporaryDirectory() as directory:
        for group in ("accepted", "wrong"):
            for solution in solutions(problem, group):
                name = solution.relative_to(ROOT)
                command, reason = build(solution, Path(directory))
                if command is None:
                    print(f"{'FAIL' if strict else 'SKIP'} {name}: {reason}")
                    ok = ok and not strict
                    continue
                if command == []:
                    print(f"FAIL {name}: コンパイルエラー\n{reason}")
                    ok = False
                    continue
                failures = []
                for source, answer in pairs:
                    result, output = run(command, source, limit)
                    if result.verdict == "OK" and normalize(output) != normalize(answer.read_text(encoding="utf-8")):
                        result = Result("WA")
                    if result.verdict != "OK":
                        failures.append(f"{source.relative_to(problem)}: {result.verdict} {result.detail}".rstrip())
                if group == "accepted" and failures:
                    ok = False
                    print(f"FAIL {name}: 正解のはずの解答が不正解です")
                    for failure in failures:
                        print("  " + failure)
                elif group == "wrong" and not failures:
                    ok = False
                    print(f"FAIL {name}: 誤答のはずの解答が全テストに正解しました。誤りを検出するテストを追加してください")
                else:
                    detail = f"{len(failures)}件で不正解を検出" if group == "wrong" else f"{len(pairs)}件すべて正解"
                    print(f"OK   {name}: {detail}")
    return ok


def answers(problem: Path, solution: Path | None, overwrite: bool) -> bool:
    if solution is None:
        candidates = solutions(problem, "accepted")
        candidates.sort(key=lambda p: PREFERENCE.index(source_language(p)))
        if not candidates:
            print(f"FAIL {problem.name}: solutions/accepted/ に解答がありません")
            return False
        solution = candidates[0]
    limit = time_limit_ms(problem)
    with tempfile.TemporaryDirectory() as directory:
        command, reason = build(solution.resolve(), Path(directory))
        if not command:
            print(f"FAIL {solution}: {reason or 'コンパイルエラー'}")
            return False
        for source, answer in tests(problem):
            if answer.exists() and not overwrite:
                continue
            result, output = run(command, source, limit)
            if result.verdict != "OK":
                print(f"FAIL {source.relative_to(ROOT)}: {result.verdict} {result.detail}")
                return False
            text = normalize(output)
            answer.write_text(text + "\n" if text else "", encoding="utf-8")
            print(f"WROTE {answer.relative_to(ROOT)}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    check_parser = commands.add_parser("check")
    check_parser.add_argument("problems", nargs="*")
    check_parser.add_argument("--strict", action="store_true", help="処理系がない解答も失敗にする")
    answer_parser = commands.add_parser("answers")
    answer_parser.add_argument("problem")
    answer_parser.add_argument("--solution", type=Path)
    answer_parser.add_argument("--overwrite", action="store_true", help="既存の .ans も作り直す")
    args = parser.parse_args()
    problems = find_problems()
    names = [args.problem] if args.command == "answers" else args.problems or sorted(problems)
    unknown = [name for name in names if name not in problems]
    if unknown:
        print("FAIL 問題が見つかりません: " + ", ".join(unknown))
        return 1
    if args.command == "answers":
        return 0 if answers(problems[args.problem], args.solution, args.overwrite) else 1
    results = [check(problems[name], args.strict) for name in names]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
