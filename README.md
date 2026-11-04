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

The pair was measured against eight baited tasks, two arms, one run per cell:

| Arm | Passed |
| --- | ---: |
| Plain prompt | 4 / 8 |
| With `steerloop` | 7 / 8 |

Each task baits one failure mode: unrequested caching, scope creep on a typo, tests written from buggy code, a red test suite the agent could edit, an unstoppable dependency loop, an interface with one implementation, a report with no evidence, a greenfield CLI.

The one clean loss for the control arm is the abstraction case: without the contract the agent invented a `UserRepository` for a five-line file with no second caller. The contract case refused and asked.

Reproduce with the probes in [`evals/`](./evals): `probes.py` holds the fixtures, `run_evals.py` spawns the runs and scores them.

**Read the numbers as directional, not as a benchmark.** Eight cells per arm, scored by reading transcripts after the LLM judge failed. And the gate is not absolute — see below.

## Limits

These are instructions, not enforcement. A prompt cannot make an agent stop.

- With no human answer available, 0 of 2 runs held the line: both asked, then shipped defaults anyway. Only a human review or a code check actually blocks.
- The gate loses more often on tasks that look locally answerable. "Add a cache" is one of them; the agent believes a sane default is a decision you would have made.
- `craftloop` is broad and opinionated. It is a good default for substantial work and overkill for a one-line fix.
- The evidence table is 16 runs on one harness. A different harness has a different default; the delta will move.

## Layout

```text
skills/steerloop/SKILL.md    the contract
skills/craftloop/SKILL.md    the method
evals/probes.py              eight baited fixtures
evals/run_evals.py           runner and scoring
assets/readme/               hero, loop diagram, social card, build script
```

`assets/readme/social.png` is the 1200×630 card for the repository's social preview.

## License

MIT.
