#!/usr/bin/env node
// Validates the five-key slice report in a commit message or pull request body.
// Usage: steerloop-gate <message-file> | --body-file <path>

import { readFileSync, statSync } from "node:fs";
import { pathToFileURL } from "node:url";

const KEYS = ["changed", "verified", "assuming", "not done", "question"];
const RUNNERS = /\b(node|npm|npx|pnpm|yarn|bun|python3?|pytest|go|cargo|dotnet|make|bash|sh|deno|vitest|jest|tsc|eslint|prettier|git|docker|terraform|kubectl|ruff|mypy|gradle|mvn)\b/;
const MAX_BYTES = 1024 * 1024;

function field(text, key) {
  const match = text.match(new RegExp(`^[ \\t*#>-]*${key}[ \\t*]*:[ \\t*]*(.*)$`, "mi"));
  return match ? match[1].replace(/\*/g, "").trim() : null;
}

function missingProblems(text) {
  return KEYS.filter((key) => field(text, key) === null).map((key) => `missing key: ${key}`);
}

function emptyProblems(text) {
  return KEYS.filter((key) => {
    const value = field(text, key);
    return value !== null && value.length === 0;
  }).map((key) => `${key}: needs a value, write "none" when nothing applies`);
}

function duplicateProblems(text) {
  return KEYS.filter((key) => {
    const pattern = new RegExp(`^[ \\t*#>-]*${key}[ \\t*]*:[ \\t*]`, "gmi");
    return (text.match(pattern) ?? []).length > 1;
  }).map((key) => `duplicate key: ${key}`);
}

function evidenceProblem(text) {
  const value = field(text, "verified") ?? "";
  if (RUNNERS.test(value) || value.includes("`")) return [];
  return ["verified: names no command (expected something like \"npm test\" or `node --test`)"];
}

export function validate(raw) {
  const text = raw.replace(/^\uFEFF/, "").replace(/\r\n?/g, "\n");
  if (/^\[skip-gate\][ \t]*$/im.test(text) || /^Merge (branch|pull request|remote-tracking branch|tag)\b/i.test(text.trim())) {
    return { ok: true, problems: [], skipped: true };
  }
  const problems = [
    ...missingProblems(text),
    ...duplicateProblems(text),
    ...emptyProblems(text),
    ...evidenceProblem(text),
  ];
  return { ok: problems.length === 0, problems, skipped: false };
}

function readBody(path) {
  const stat = statSync(path);
  if (!stat.isFile()) throw new Error(`${path} is not a file`);
  if (stat.size > MAX_BYTES) throw new Error(`${path} is larger than 1 MiB`);
  return readFileSync(path, "utf8");
}

function usage() {
  console.error("usage: steerloop-gate <message-file> | --body-file <path>");
  return 2;
}

function main(argv) {
  if (process.env.STEERLOOP_SKIP === "1") return 0;
  const flag = argv.indexOf("--body-file");
  const path = flag >= 0 ? argv[flag + 1] : argv[0];
  if (!path) return usage();
  let text;
  try {
    text = readBody(path);
  } catch (error) {
    console.error(`steerloop-gate: ${error.message}`);
    return 2;
  }
  const result = validate(text);
  if (result.ok) return 0;
  console.error("steerloop-gate: the slice report is incomplete.\n");
  for (const problem of result.problems) console.error(`  - ${problem}`);
  console.error(
    "\nRequired block:\n  changed: <files>\n  verified: <command and its result>\n  assuming: <shipped defaults, or none>\n  not done: <or none>\n  question: <or none>",
  );
  console.error("\nBypass once with STEERLOOP_SKIP=1 or [skip-gate] when the gate itself is wrong.");
  return 1;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  process.exit(main(process.argv.slice(2)));
}
