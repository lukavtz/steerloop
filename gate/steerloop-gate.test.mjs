import test from "node:test";
import { spawnSync } from "node:child_process";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import assert from "node:assert/strict";

import { validate } from "./steerloop-gate.mjs";

const REPORT = "changed: parser.mjs\nverified: npm test -> 4 pass\nassuming: none\nnot done: none\nquestion: none";

const cases = [
  ["complete block passes", `Add parser\n\n${REPORT}`, true],
  ["blocked slice passes with changed: none", "Fix bug\n\nchanged: none\nverified: node --test -> 1 fail\nassuming: none\nnot done: all\nquestion: TTL?", true],
  ["markdown formatting passes", `Add parser\n\n**changed:** a.mjs\n**verified:** \`node --test\` -> 3 pass\n**assuming:** 60 s TTL\n**not done:** none\n**question:** none`, true],
  ["missing assuming fails", "Add parser\n\nchanged: a.mjs\nverified: npm test\nnot done: none\nquestion: none", false],
  ["missing question fails", "Add parser\n\nchanged: a.mjs\nverified: npm test\nassuming: none\nnot done: none", false],
  ["verified: none fails", "Add parser\n\nchanged: a.mjs\nverified: none\nassuming: none\nnot done: none\nquestion: none", false],
  ["verified without a command fails", "Add parser\n\nchanged: a.mjs\nverified: looked right\nassuming: none\nnot done: none\nquestion: none", false],
  ["empty question fails", "Add parser\n\nchanged: a.mjs\nverified: npm test\nassuming: none\nnot done: none\nquestion:", false],
  ["any toolchain command passes", "changed: a\nverified: tsc --noEmit -> ok\nassuming: none\nnot done: none\nquestion: none", true],
  ["backticked command passes", "changed: a\nverified: `terraform plan` -> no changes\nassuming: none\nnot done: none\nquestion: none", true],
  ["eslint passes", "changed: a\nverified: eslint . -> 0 errors\nassuming: none\nnot done: none\nquestion: none", true],
  ["skip marker passes", "Add parser\n\n[skip-gate]", true],
  ["merge commit passes", "Merge branch 'main' into feature", true],
];

for (const [name, text, expected] of cases) {
  test(name, () => {
    assert.equal(validate(text).ok, expected);
  });
}

test("failures name the offending key", () => {
  const result = validate("Add parser\n\nchanged: a.mjs\nverified: npm test\nnot done: none\nquestion: none");
  assert.equal(result.ok, false);
  assert.ok(result.problems.some((p) => p.includes("assuming")));
});

const GATE = new URL("./steerloop-gate.mjs", import.meta.url).pathname.replace(/^\/(\w:)/, "$1");
const body = (text) => {
  const file = join(mkdtempSync(join(tmpdir(), "gate-")), "msg.txt");
  writeFileSync(file, text);
  return file;
};

test("merge of a remote-tracking branch passes", () => {
  assert.equal(validate("Merge remote-tracking branch 'origin/main'").ok, true);
});

test("merge of a tag passes", () => {
  assert.equal(validate("Merge tag 'v1.0.0'").ok, true);
});

test("skip marker inline in prose does not bypass", () => {
  assert.equal(validate("Fix parser, see [skip-gate] in the docs").ok, false);
});

test("cli: valid body exits 0", () => {
  const result = spawnSync(process.execPath, [GATE, body(REPORT)], { encoding: "utf8" });
  assert.equal(result.status, 0);
});

test("cli: invalid body exits 1", () => {
  const result = spawnSync(process.execPath, [GATE, body("Add nothing")], { encoding: "utf8" });
  assert.equal(result.status, 1);
  assert.match(result.stderr, /missing key: changed/);
});

test("cli: no argument exits 2", () => {
  assert.equal(spawnSync(process.execPath, [GATE], { encoding: "utf8" }).status, 2);
});

test("cli: missing file exits 2", () => {
  assert.equal(spawnSync(process.execPath, [GATE, "no-such-file.txt"], { encoding: "utf8" }).status, 2);
});

test("cli: oversized body exits 2", () => {
  const result = spawnSync(process.execPath, [GATE, body("x".repeat(1024 * 1024 + 1))], { encoding: "utf8" });
  assert.equal(result.status, 2);
});

test("cli: STEERLOOP_SKIP bypasses", () => {
  const result = spawnSync(process.execPath, [GATE, body("Add nothing")], {
    encoding: "utf8",
    env: { ...process.env, STEERLOOP_SKIP: "1" },
  });
  assert.equal(result.status, 0);
});
