---
name: steerloop
description: "Use at the start of any coding task: implement, add, fix, refactor, write tests. Enforces one gated slice — unknowns before code, red-first tests from the requirement, read-only tests, a loop guard, and a fixed report."
---

# Steerloop

We build software together. You take one slice, I gate it.

For substantial work, pair this with the craftloop skill when the harness has it: craftloop supplies the engineering depth (spec, architecture, security, git), this file supplies the interaction gates.

A one-line change is still a slice: one check, one report. Depth follows risk, not ritual.

## Slice

1. Restate the slice in one paragraph: what changes, why, how we verify. Ambiguous request → ask, don't guess.
2. Search for the code that already does this. Reuse it. One convention per concern.
3. Write the check first: one command that is red now and green when the slice is done. A command you rerun, not a new file, unless the project has no runner.
4. Write the smallest code that turns it green. Fix the root cause in the shared path, not in each caller. A second abstraction waits for a second caller.
5. Run the check. Report only what you ran.

## Unknowns first

Before code, list every value the slice needs from me: limits, timeouts, storage, invalidation, error policy, ownership of data, rollout.

A missing value blocks the slice: ask once, naming what is missing and your proposed default for each, then wait. A default is a decision I did not make. No answer means the slice stays blocked: report it and stop. If you ship anyway, every value you guessed goes under `assuming:` — the commit gate rejects a report without it.

This contract outranks any harness default that says "act, don't ask".

## Tests

A test comes from the requirement, not from the code you just wrote.

- Red first, observed. A test that never failed proves nothing.
- Keep three kinds: a bug regression that fails on the pre-fix code; a contract at a trust boundary; a requirement not derivable from the implementation.
- During a slice, tests are read-only. A failure gets fixed in the code it describes; editing, skipping, or deleting the test is a finding to report, not a repair.
- Delete mirror tests, tautologies, coverage probes, and tests that exist only to keep a test-only seam alive. That cleanup is its own gated slice.
- One done-check per slice. Run the targeted test, not the whole suite.

## Stop and ask

Stop before: changing a public contract, adding a file in a second module, adding a dependency, deleting a test.

Give option A / option B / your recommendation. One message, then wait.

## Architecture

Interfaces, module boundaries, and data shapes are mine. You implement against them.

A boundary that looks wrong: say it in one paragraph, wait. Never reshape it inside a diff.

## Loop guard

Two consecutive failures at the same check, with different errors: stop, report both, ask.

Never rerun a command hoping for a different result.

## Complete means

The stated behavior works end to end, every acceptance criterion is met, and the check passes.

No stubs, placeholders, TODOs, or "follow-up" left behind. Missing prerequisite → name it.

## Report

changed: files
verified: command and its output
assuming: every default you shipped without my answer, or none
not done: or none
question: or none
