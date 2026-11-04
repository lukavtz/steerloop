import test from "node:test";
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
