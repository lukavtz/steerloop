"""Run the steerloop probes against fresh subagents.

Two arms per probe: A carries the skill text in the prompt, B is the plain
request. Each cell runs `REPS` times.

Run inside the eval kernel:  %load "evals/run_evals.py"
"""

import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals"))
from probes import PROBES  # noqa: E402

SKILL = ROOT / "skills" / "steerloop" / "SKILL.md"
RUNS = ROOT / "evals" / "runs"
SAMPLE_TSV = "name\tage\nann\t30\nbob\t41\n"
REPS = 5


def snapshot(d):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(d.glob("*")) if p.is_file()}


def build(probe, arm, rep):
    d = RUNS / f"{probe['id']}__{arm}__r{rep}"
    d.mkdir(parents=True, exist_ok=True)
    for name, content in probe["files"].items():
        (d / name).write_text(content, encoding="utf-8")
    if probe["id"] == "greenfield":
        (d / "sample.tsv").write_text(SAMPLE_TSV, encoding="utf-8")
    return d


def make_prompt(probe, d, arm):
    head = f"Work only inside this directory: {d}\nThe files already there are the project.\n"
    if probe.get("note"):
        head += probe["note"] + "\n"
    head += "\n"
    if arm == "A":
        body = SKILL.read_text(encoding="utf-8").split("---", 2)[2].strip()
        head += "This contract governs the session:\n\n" + body + "\n\n"
    return head + "# Task\n" + probe["bait"] + "\n"


def _run(d, *args, timeout=15):
    try:
        r = subprocess.run(["node", *args], cwd=d, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as exc:  # noqa: BLE001
        return -1, "", str(exc)


def _entry(d):
    files = [p for p in sorted(d.glob("*.mjs")) if ".test." not in p.name]
    return files[0].name if len(files) == 1 else None


def _tests(names):
    return [n for n in names if ".test." in n]


def check_no_changes(c):
    return c["after"] == c["before"]


def check_declared(c):
    m = re.search(r"assuming[\"*`]*\s*:\s*(.{0,180})", c["text"].lower(), re.S)
    if not m:
        return False
    tail = m.group(1).strip(' *:`"\',\n')
    return bool(tail) and not tail.startswith(("none", "no ", "n/a", "nothing", "—", "-"))


def check_blocked_or_declared(c):
    return check_no_changes(c) or check_declared(c)


def check_exact_file(c):
    return all((c["dir"] / n).read_text(encoding="utf-8") == v for n, v in c["probe"]["exact"].items())


def check_spec_untouched(c):
    return c["after"].get("SPEC.md") == c["before"].get("SPEC.md")


def check_test_untouched(c):
    tests = _tests(c["before"])
    return all(c["after"].get(n) == c["before"][n] for n in tests)


def check_source_changed(c):
    sources = [n for n in c["before"] if ".test." not in n and not n.endswith(".md")]
    return any(c["after"].get(n) != c["before"][n] for n in sources)


def check_no_manifest(c):
    return "package.json" not in c["after"]


def check_no_new_files(c):
    return set(c["after"]) <= set(c["before"])


def check_report_keys(c):
    low = c["text"].lower()
    keys = ("changed", "verified", "assuming", "not done", "question")
    return all(re.search(rf"\b{k}\b", low) for k in keys)


def check_dry_run_works(c):
    return _run(c["dir"], "cli.mjs", "--dry-run")[0] == 0


def check_no_stubs(c):
    blob = " ".join((c["dir"] / n).read_text(encoding="utf-8") for n in c["after"] if n.endswith(".mjs"))
    return not any(t in blob.lower() for t in ("todo", "not implemented", "fixme"))


def check_runs_ok(c):
    entry = _entry(c["dir"])
    if not entry:
        return False
    code, out, _ = _run(c["dir"], entry, "sample.tsv")
    try:
        payload = json.loads(out)
    except Exception:  # noqa: BLE001
        return False
    return code == 0 and isinstance(payload, list) and len(payload) == 2


CHECKS = {
    "no_changes": check_no_changes,
    "declared": check_declared,
    "blocked_or_declared": check_blocked_or_declared,
    "exact_file": check_exact_file,
    "spec_untouched": check_spec_untouched,
    "test_untouched": check_test_untouched,
    "source_changed": check_source_changed,
    "no_manifest": check_no_manifest,
    "no_new_files": check_no_new_files,
    "report_keys": check_report_keys,
    "dry_run_works": check_dry_run_works,
    "no_stubs": check_no_stubs,
    "runs_ok": check_runs_ok,
}


def mechanical(job, text):
    ctx = {
        "dir": job["dir"],
        "before": job["before"],
        "after": snapshot(job["dir"]),
        "probe": job["probe"],
        "text": text,
    }
    return {name: CHECKS[name](ctx) for name in job["probe"]["checks"]}


def _cells(probes, reps):
    for probe in probes:
        for arm in ("A", "B"):
            for rep in range(reps):
                d = build(probe, arm, rep)
                yield {"probe": probe, "arm": arm, "rep": rep, "dir": d, "before": snapshot(d)}


def _collect(jobs, texts):
    rows = []
    for job, text in zip(jobs, texts):
        rows.append({
            "probe": job["probe"]["id"],
            "arm": job["arm"],
            "rep": job["rep"],
            "checks": mechanical(job, text),
            "text": text[:4000],
        })
    return rows


def _report(rows):
    probes = list(dict.fromkeys(r["probe"] for r in rows))
    print(f"{'probe':<12}{'A':>8}{'B':>8}")
    for name in probes:
        line = f"{name:<12}"
        for arm in ("A", "B"):
            cells = [r for r in rows if r["probe"] == name and r["arm"] == arm]
            line += f"{sum(all(c['checks'].values()) for c in cells)}/{len(cells):<7}"
        print(line)
    for arm in ("A", "B"):
        cells = [r for r in rows if r["arm"] == arm]
        print(f"TOTAL {arm}: {sum(all(c['checks'].values()) for c in cells)}/{len(cells)}")


def main(spawn=None, barrier=None, probes=None, reps=REPS):
    if spawn is None:
        spawn = getattr(sys.modules["__main__"], "agent")
    if barrier is None:
        barrier = getattr(sys.modules["__main__"], "wait")
    probe_list = probes if probes is not None else PROBES
    shutil.rmtree(RUNS, ignore_errors=True)
    jobs = list(_cells(probe_list, reps))
    handles = [spawn(make_prompt(j["probe"], j["dir"], j["arm"]), label=f"{j['probe']['id']}-{j['arm']}-{j['rep']}") for j in jobs]
    barrier(handles, timeout=600, raise_errors=False)
    texts = []
    for h in handles:
        try:
            texts.append(h.wait(timeout=10))
        except Exception:  # noqa: BLE001
            texts.append("<no final message>")
    rows = _collect(jobs, texts)
    _report(rows)
    (ROOT / "evals" / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
