"""Run SlopCodeBench-lite: three tasks, three rounds, two arms.

Metrics per round follow arXiv:2603.24755 (verbosity, structural erosion)
plus a progress signal (checkpoints passed). Run inside the eval kernel:

    await main()
"""

import asyncio
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals"))
from slop_tasks import TASKS  # noqa: E402

RUNS = ROOT / "evals" / "runs_slop"
SKILL = ROOT / "skills" / "steerloop" / "SKILL.md"
STRING_RE = re.compile(r"'[^']*'|\"[^\"]*\"|`[^`]*`")


HARNESS = re.compile(r"(^check\.|^test_|\.test\.)")


def _sources(d, all_files=False):
    return [p for p in sorted(d.glob("*.mjs")) if all_files or not HARNESS.search(p.name)]


def _loc(text):
    return sum(1 for line in text.splitlines() if line.strip() and not line.strip().startswith("//"))


def _norm(line):
    return re.sub(r"\s+", "", STRING_RE.sub("S", line))


def _dups(texts):
    counts = {}
    for text in texts:
        for line in text.splitlines():
            key = _norm(line)
            if len(key) >= 12:
                counts[key] = counts.get(key, 0) + 1
    return sum(n - 1 for n in counts.values() if n > 1)


def _span(text, start):
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i - start
    return len(text) - start


def _spans(text):
    spans = []
    for match in re.finditer(r"function\b|=>", text):
        brace = match.end()
        if match.group() != "=>":
            brace = text.find("{", brace)
            if brace < 0:
                break
        while brace < len(text) and text[brace] in " \n":
            brace += 1
        if brace < len(text) and text[brace] == "{":
            body = text[brace : brace + _span(text, brace)]
            spans.append(body.count("\n") + 1)
    return spans


def metrics(d):
    texts = [p.read_text(encoding="utf-8") for p in _sources(d)]
    loc = sum(_loc(t) for t in texts)
    all_loc = sum(_loc(p.read_text(encoding="utf-8")) for p in _sources(d, all_files=True))
    spans = [s for t in texts for s in _spans(t)]
    erosion = round(max(spans) / loc, 3) if spans and loc else 0.0
    return {"loc": loc, "all_loc": all_loc, "dup": _dups(texts), "erosion": erosion}


def _run(d, entry, args, timeout=20):
    try:
        r = subprocess.run(["node", entry, *args], cwd=d, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout
    except Exception:  # noqa: BLE001
        return -1, ""


def _score(task, d, upto):
    passed = total = 0
    for rnd in task["rounds"][:upto]:
        for _, args, test in rnd["checks"]:
            total += 1
            passed += bool(test(*_run(d, task["entry"], args)))
    return {"passed": passed, "total": total, **metrics(d)}


def _prompt(d, arm, round_no):
    head = f"Work only inside this directory: {d}\nThe files already there are the project.\n\n"
    if arm == "A":
        body = SKILL.read_text(encoding="utf-8").split("---", 2)[2].strip()
        head += "This contract governs the session:\n\n" + body + "\n\n"
    return head + f"# Task\nImplement SPEC.md, round {round_no}. Every requirement in it must hold, earlier rounds included.\n"


def _prepare(task, arm):
    d = RUNS / f"{task['id']}__{arm}"
    d.mkdir(parents=True, exist_ok=True)
    for name, content in task["fixture"].items():
        (d / name).write_text(content, encoding="utf-8", newline="\n")
    return d


async def chain(task, arm, rep, spawn):
    d = RUNS / f"{task['id']}__{arm}__r{rep}"
    d.mkdir(parents=True, exist_ok=True)
    for name, content in task["fixture"].items():
        (d / name).write_text(content, encoding="utf-8", newline="\n")
    spec, rows = [], []
    for number, rnd in enumerate(task["rounds"], 1):
        spec.append(rnd["spec"].strip())
        (d / "SPEC.md").write_text("\n\n".join(spec) + "\n", encoding="utf-8", newline="\n")
        await spawn(_prompt(d, arm, number))
        rows.append({"task": task["id"], "arm": arm, "rep": rep, "round": number, **_score(task, d, number)})
    return rows


def _finals(rows):
    best = {}
    for row in rows:
        key = (row["task"], row["arm"], row["rep"])
        if key not in best or row["round"] > best[key]["round"]:
            best[key] = row
    return list(best.values())


def _avg(values):
    return round(sum(values) / len(values), 3) if values else 0.0


def _summary(rows):
    finals = _finals(rows)
    print(f"{'task':<12}{'arm':>4}{'pass':>9}{'loc':>6}{'all':>6}{'dup':>6}{'erosion':>9}")
    for task in dict.fromkeys(r["task"] for r in finals):
        for arm in ("A", "B"):
            cell = [r for r in finals if r["task"] == task and r["arm"] == arm]
            print(
                f"{task:<12}{arm:>4}"
                f"{sum(r['passed'] for r in cell)}/{sum(r['total'] for r in cell):<7}"
                f"{_avg([r['loc'] for r in cell]):>6}{_avg([r['all_loc'] for r in cell]):>6}"
                f"{_avg([r['dup'] for r in cell]):>6}{_avg([r['erosion'] for r in cell]):>9}"
            )
    for arm in ("A", "B"):
        cell = [r for r in finals if r["arm"] == arm]
        print(
            f"TOTAL {arm}: checkpoints {sum(r['passed'] for r in cell)}/{sum(r['total'] for r in cell)}, "
            f"loc {_avg([r['loc'] for r in cell])}, all {_avg([r['all_loc'] for r in cell])}, "
            f"erosion {_avg([r['erosion'] for r in cell])}"
        )


async def main(spawn=None, reps=2):
    if spawn is None:
        spawn = getattr(sys.modules["__main__"], "agent")
    shutil.rmtree(RUNS, ignore_errors=True)
    chains = [chain(task, arm, rep, spawn) for task in TASKS for arm in ("A", "B") for rep in range(reps)]
    rows = [row for group in await asyncio.gather(*chains) for row in group]
    _summary(rows)
    (ROOT / "evals" / "slop_results.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return rows
