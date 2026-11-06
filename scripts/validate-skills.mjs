#!/usr/bin/env node
// Validates every skills/<name>/SKILL.md against the Agent Skills frontmatter rules,
// and checks stack.json against the tree.
// Usage: node scripts/validate-skills.mjs

import { existsSync, readFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SKILLS = join(ROOT, "skills");
const NAME = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const LIMITS = { name: 64, description: 1024, compatibility: 500 };

function frontmatter(raw) {
  const lines = raw.replace(/^\uFEFF/, "").replace(/\r\n?/g, "\n").split("\n");
  if (lines[0]?.trim() !== "---") return null;
  const end = lines.findIndex((line, index) => index > 0 && line.trim() === "---");
  return end < 0 ? null : parseBlock(lines.slice(1, end));
}

function parseBlock(lines) {
  const out = {};
  for (let i = 0; i < lines.length; i += 1) {
    const match = lines[i].match(/^([a-z0-9-]+):\s*(.*)$/);
    if (!match) continue;
    const key = match[1];
    const rest = match[2];
    if (rest === ">" || rest === "|") {
      const parts = [];
      while (i + 1 < lines.length && /^\s+\S/.test(lines[i + 1])) parts.push(lines[++i].trim());
      out[key] = parts.join(" ");
    } else {
      out[key] = rest.replace(/^["']|["']$/g, "").trim();
    }
  }
  return out;
}

function skillProblems(dir) {
  const file = join(SKILLS, dir, "SKILL.md");
  if (!existsSync(file)) return [`${dir}: SKILL.md is missing`];
  const data = frontmatter(readFileSync(file, "utf8"));
  if (!data) return [`${dir}: no frontmatter block`];
  const problems = [];
  if (!data.name) problems.push(`${dir}: name is missing`);
  else if (data.name !== dir) problems.push(`${dir}: name "${data.name}" does not match the folder`);
  else if (!NAME.test(data.name)) problems.push(`${dir}: name must be lowercase words joined by single hyphens`);
  if (!data.description) problems.push(`${dir}: description is missing`);
  for (const [key, max] of Object.entries(LIMITS)) {
    if (data[key] && data[key].length > max) problems.push(`${dir}: ${key} is ${data[key].length} chars, limit ${max}`);
  }
  return problems;
}

function listingProblems(skills, stack) {
  const listed = Object.keys(stack.skills ?? {});
  const missingFromStack = skills.filter((name) => !listed.includes(name)).map((n) => `stack.json: ${n} is not listed in skills`);
  const missingFromTree = listed.filter((name) => !skills.includes(name)).map((n) => `stack.json: ${n} has no skills/${n}/SKILL.md`);
  return [...missingFromStack, ...missingFromTree];
}

function profileProblems(skills, stack) {
  return Object.entries(stack.profiles ?? {}).flatMap(([profile, names]) =>
    names.filter((name) => !skills.includes(name)).map((name) => `stack.json: profile ${profile} names unknown skill ${name}`),
  );
}

function stackProblems(skills) {
  const file = join(ROOT, "stack.json");
  if (!existsSync(file)) return ["stack.json is missing"];
  const stack = JSON.parse(readFileSync(file, "utf8"));
  return [...listingProblems(skills, stack), ...profileProblems(skills, stack)];
}

function main() {
  const skills = readdirSync(SKILLS, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
  const problems = [...skills.flatMap(skillProblems), ...stackProblems(skills)];
  if (problems.length === 0) {
    console.log(`skills: ${skills.length} valid, stack.json consistent`);
    return 0;
  }
  for (const problem of problems) console.error(`  - ${problem}`);
  console.error(`\n${problems.length} problem(s)`);
  return 1;
}

process.exit(main());