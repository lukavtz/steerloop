<p align="center">
  <img src="./assets/readme/hero.png" width="100%" alt="steerloop — one slice at a time, the agent asks before it writes code">
</p>

<p align="center">
  <a href="#install">Install</a> ·
  <a href="#what-changes">What changes</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#evidence">Evidence</a> ·
  <a href="#limits">Limits</a>
</p>

Two skill files for coding agents. One keeps the agent on a single slice and makes it ask before it codes. The other is the engineering method it runs inside.

They are small on purpose. `steerloop` is 65 lines. Every rule in it is a gate you can check, not a paragraph of advice.

## Install

```bash
npx skills add lukavtz/steerloop
```

Works with any agent that reads `SKILL.md`: OpenCode, Claude Code, Cursor, Codex, omp, Pi, Dsh and the rest of the [skills CLI](https://skills.sh) targets. To preview without installing:

```bash
npx skills add lukavtz/steerloop --list
```

## What changes

The failure this exists for is not bad code. It is code nobody asked for: an unrequested cache, an interface with one implementation, four hundred tests that assert what the code already does, and a loop that reruns them after every edit.

| Default agent | With `steerloop` |
| --- | --- |
| Picks a TTL, a storage, an error policy and ships them | Names the missing values, asks once, waits |
| Writes tests from the code it just wrote | Writes the check from the requirement, red first |
| Edits the failing test until it passes | Fixes the code the test describes; a test edit is a finding |
| Adds the abstraction someone might need later | A second abstraction waits for a second caller |
| Runs the suite after every edit, forever | One done-check per slice, targeted |
| Reports "done" | Reports changed / verified / not done / question |

## The pair

| Skill | Owns | Fires when |
| --- | --- | --- |
| **`steerloop`** | Interaction gates: when to stop, what a slice is, what a report contains | Every coding task, at the start |
| **`craftloop`** | Engineering depth: spec, architecture, security, verification, git and PR delivery | Substantial work |

`steerloop` is the newer half of the pair. `craftloop` is included here with one changed sentence: its old "ask only when a material decision cannot be safely inferred" clause licensed the agent to invent exactly the values this pair exists to protect. It now says a value the request does not state is the user's decision.

## How it works

<p align="center">
  <img src="./assets/readme/loop.svg" width="100%" alt="Five steps — restate, reuse, red check, smallest code, run — with an amber gate that sends missing values back to the human">
</p>

The gate sits between restating the slice and touching code. A value the request does not state blocks the slice. The agent asks once, proposes a default per item, and waits.

A blocked slice reports like this:

```text
changed: none
verified: inspected store.mjs (5 lines), no importer of saveUser
not done: all of it — blocked on the values below
question: TTL, storage, error policy, invalidation, rollout?
```

A finished slice reports like this:

```text
changed: parser.mjs, parser.test.mjs
verified: node --test parser.test.mjs → 4 pass, 0 fail (red first: 2 failed)
not done: none
question: none
```

Four keys, always. The report is the proof, and it is cheap to check: `verified` names a command, so a claim without a command is visibly incomplete.

## Evidence

Two instruments live in [`evals/`](./evals). Both are A/B against the same harness, so the only difference is this skill.

**Behaviour probes** — 9 baited tasks, 3 repetitions per cell:

| Arm | Passed |
| --- | ---: |
| Plain prompt | 11 / 24 |
| With `steerloop` | 15 / 24 |

Four cells out of 24. A hint that the gates fire more often, not a result. An earlier single-run version of this table read 4/8 vs 7/8 and was noise: the third repetition dropped `greenfield` from one pass to one pass in three.

**SlopCodeBench-lite** — three CLI tasks, three rounds each, the agent extends its own code while the spec grows. Design and metrics follow [SlopCodeBench](https://arxiv.org/abs/2603.24755): size, duplication, and how much code piles into one function. Two repetitions, 39 checkpoints per arm:

| Metric | Plain | `steerloop` |
| --- | ---: | ---: |
| Checkpoints passed | 36 / 39 | 39 / 39 |
| Production LOC | 65 | 68 |
| All code LOC | 77 | 112 |
| Erosion (largest function ÷ LOC) | 0.12 | 0.24 |

The skill did **not** produce leaner code. The extra lines are mostly the check harness its own rule demands, and on `calc` it wrote one large function where the plain arm split it. What it bought is one real thing: it never misread the `intervals` argument format that the plain arm failed once in three runs.

Reproduce:

```bash
# inside an agent with the eval kernel
%load "evals/run_evals.py"   # behaviour probes
await main()                 # slop benchmark, in evals/run_slop.py
```

## Limits

These are instructions, not enforcement. A prompt cannot make an agent stop.

- **The assumption rule does not fire.** In six runs of the cache task — three with a human present, three with the human explicitly unreachable — no run blocked and no run declared an assumption. The agents either answered the request or asked and then shipped. `assuming:` is a slot in the report that nobody filled.
- **The gate loses on tasks that look locally answerable.** "Add a cache" is one of them: the agent believes a sane default is a decision you would have made.
- **No code-size win.** The slop benchmark shows the skill writing more code, not less, and concentrating it slightly more. If your goal is smaller diffs, this is not the instrument.
- **One harness, one model family.** Every number here comes from a single setup whose system prompt already enforces verification. On a bare agent the delta could be larger or absent.
- **`craftloop` is broad.** It is a good default for substantial work and overkill for a one-line fix.

## Layout

```text
skills/steerloop/SKILL.md    the contract
skills/craftloop/SKILL.md    the method
evals/probes.py              nine baited fixtures
evals/run_evals.py           probe runner, three reps
evals/slop_tasks.py          three CLI tasks, three rounds
evals/run_slop.py            iterative-extension benchmark
assets/readme/               hero, loop diagram, social card, build script
```

`assets/readme/social.png` is the 1200×630 card for the repository's social preview.

## License

MIT.
