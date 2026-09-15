#!/usr/bin/env node
/* Wayfinder version-1 Node.js adapter. Standard-library only. */

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const RELEASE_ID = "v1-candidate-revision-10";
const RELEASE_STATUS = "unactivated-frozen";
const CONTRACT_STATUS = "frozen";
const CONTRACT_VERSION = 1;
const CANDIDATE_REVISION = 10;
const ADAPTER_ID = "node-v1";
const ADAPTER_PATH = "scripts/adapters/wayfinder-node.mjs";
const RELEASE_PATH = "assets/contract-v1/release.json";
const CONTRACT_PATH = "assets/contract-v1/contract.json";
const RESULT_FIELDS = ["format", "schemaVersion", "ok", "command", "code", "data", "diagnostics"];
const HEX = /^[0-9a-f]{64}$/;
const SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const DOC_ID = /^wf-([0-9]{4,})-([a-z0-9]+(?:-[a-z0-9]+)*)$/;
const QUESTION_ID = /^wfq-([0-9]{4,})-([a-z0-9]+(?:-[a-z0-9]+)*)$/;
const SOURCE_ID = /^src-([0-9]{2,})$/;
const STANDARD_MODULES = ["decisions", "research", "product", "architecture", "development"];
const COMMANDS = ["probe", "discover", "inventory", "initialize-plan", "initialize-apply", "initialize-recover", "validate", "generate"];
const CAPABILITIES = [
  "canonical-json-integer-subset", "document-catalog-v1", "document-index-v1", "document-render-v1",
  "initialize-apply-v1", "initialize-plan-v1", "initialize-recover-v1", "nfc", "record-validation-v1",
  "sha256", "source-inventory-v1", "strict-json", "symlink-inspection", "utf8-strict",
];

class WFError extends Error {
  constructor(code, message, exitClass = 4, details = {}) {
    super(message);
    this.name = "WFError";
    this.code = code;
    this.exitClass = exitClass;
    this.details = details;
  }
  diagnostic() {
    const value = { code: this.code, message: this.message };
    for (const key of ["path", "field", "expected", "actual", "remediation"]) {
      if (Object.hasOwn(this.details, key)) value[key] = this.details[key];
    }
    return value;
  }
}

const fail = (code, message, exitClass = 4, details = {}) => { throw new WFError(code, message, exitClass, details); };
const sha256 = raw => crypto.createHash("sha256").update(raw).digest("hex");
const utf8Bytes = text => Buffer.from(text, "utf8");
const isPlainObject = value => value !== null && typeof value === "object" && !Array.isArray(value);
const pointerPart = value => value.replaceAll("~", "~0").replaceAll("/", "~1");

class StrictJsonParser {
  constructor(raw, label, exitClass) {
    this.raw = raw;
    this.label = label;
    this.exitClass = exitClass;
    if (raw.subarray(0, 3).equals(Buffer.from([0xef, 0xbb, 0xbf]))) fail("text.bom", "JSON must not contain a UTF-8 BOM", exitClass, { path: label });
    if (raw.includes(0x0d)) fail("text.newline", "JSON must use LF newlines", exitClass, { path: label });
    try { this.text = new TextDecoder("utf-8", { fatal: true }).decode(raw); }
    catch { fail("text.invalid-utf8", "JSON is not well-formed UTF-8", exitClass, { path: label }); }
    this.i = 0;
  }
  error(code = "json.invalid", message = "JSON is invalid", details = {}) { fail(code, message, this.exitClass, { path: this.label, ...details }); }
  ws() { while (this.i < this.text.length && /[\x20\x09\x0a\x0d]/.test(this.text[this.i])) this.i += 1; }
  parse() {
    this.ws();
    const value = this.value("");
    this.ws();
    if (this.i !== this.text.length) this.error();
    checkNfc(value, "", this.exitClass);
    return value;
  }
  value(pointer) {
    this.ws();
    const c = this.text[this.i];
    if (c === "{") return this.object(pointer);
    if (c === "[") return this.array(pointer);
    if (c === '"') return this.string();
    if (c === "t" && this.text.startsWith("true", this.i)) { this.i += 4; return true; }
    if (c === "f" && this.text.startsWith("false", this.i)) { this.i += 5; return false; }
    if (c === "n" && this.text.startsWith("null", this.i)) { this.i += 4; return null; }
    if (c === "-" || (c >= "0" && c <= "9")) return this.number(pointer);
    this.error();
  }
  object(pointer) {
    this.i += 1; this.ws();
    const out = {}; const seen = new Set();
    if (this.text[this.i] === "}") { this.i += 1; return out; }
    while (true) {
      if (this.text[this.i] !== '"') this.error();
      const key = this.string();
      if (seen.has(key)) this.error("json.duplicate-key", "JSON object contains a duplicate field", { field: `${pointer}/${pointerPart(key)}` });
      seen.add(key); this.ws();
      if (this.text[this.i] !== ":") this.error();
      this.i += 1;
      out[key] = this.value(`${pointer}/${pointerPart(key)}`);
      this.ws();
      if (this.text[this.i] === "}") { this.i += 1; return out; }
      if (this.text[this.i] !== ",") this.error();
      this.i += 1; this.ws();
    }
  }
  array(pointer) {
    this.i += 1; this.ws();
    const out = [];
    if (this.text[this.i] === "]") { this.i += 1; return out; }
    while (true) {
      out.push(this.value(`${pointer}/${out.length}`)); this.ws();
      if (this.text[this.i] === "]") { this.i += 1; return out; }
      if (this.text[this.i] !== ",") this.error();
      this.i += 1; this.ws();
    }
  }
  string() {
    const start = this.i;
    this.i += 1;
    while (this.i < this.text.length) {
      const code = this.text.charCodeAt(this.i);
      if (code === 0x22) {
        this.i += 1;
        let value;
        try { value = JSON.parse(this.text.slice(start, this.i)); } catch { this.error(); }
        for (let j = 0; j < value.length; j += 1) {
          const unit = value.charCodeAt(j);
          if (unit >= 0xd800 && unit <= 0xdbff) {
            if (j + 1 >= value.length || value.charCodeAt(j + 1) < 0xdc00 || value.charCodeAt(j + 1) > 0xdfff) this.error("text.invalid-unicode", "JSON string contains an unpaired surrogate");
            j += 1;
          } else if (unit >= 0xdc00 && unit <= 0xdfff) this.error("text.invalid-unicode", "JSON string contains an unpaired surrogate");
        }
        return value;
      }
      if (code < 0x20) this.error();
      if (code === 0x5c) {
        this.i += 1;
        if (this.i >= this.text.length || !/["\\/bfnrtu]/.test(this.text[this.i])) this.error();
        if (this.text[this.i] === "u") {
          if (!/^[0-9a-fA-F]{4}$/.test(this.text.slice(this.i + 1, this.i + 5))) this.error();
          this.i += 4;
        }
      }
      this.i += 1;
    }
    this.error();
  }
  number(pointer) {
    const rest = this.text.slice(this.i);
    const match = /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/.exec(rest);
    if (!match) this.error();
    const token = match[0]; this.i += token.length;
    if (/[.eE]/.test(token) || token === "-0") this.error("json.number", "only canonical integers are accepted", { field: pointer });
    let big;
    try { big = BigInt(token); } catch { this.error("json.number", "integer is invalid", { field: pointer }); }
    if (big < -9007199254740991n || big > 9007199254740991n) this.error("json.number", "integer is outside the exact version-1 range", { field: pointer });
    return Number(big);
  }
}

function checkNfc(value, pointer = "", exitClass = 4) {
  if (typeof value === "string") {
    if (value.normalize("NFC") !== value) fail("text.non-nfc", "JSON strings must be NFC", exitClass, { field: pointer || "/" });
    return;
  }
  if (Array.isArray(value)) value.forEach((item, i) => checkNfc(item, `${pointer}/${i}`, exitClass));
  else if (isPlainObject(value)) for (const [key, item] of Object.entries(value)) { checkNfc(key, `${pointer}/${pointerPart(key)}`, exitClass); checkNfc(item, `${pointer}/${pointerPart(key)}`, exitClass); }
}

function strictJsonBytes(raw, label, { governed = false, exitClass = 4 } = {}) {
  if (governed && (raw.length === 0 || raw[raw.length - 1] !== 0x0a || (raw.length > 1 && raw[raw.length - 2] === 0x0a))) fail("text.newline", "governed JSON must have exactly one terminal LF", exitClass, { path: label });
  return new StrictJsonParser(raw, label, exitClass).parse();
}

function canonicalJson(value) {
  if (value === null) return "null";
  if (value === true) return "true";
  if (value === false) return "false";
  if (typeof value === "number") {
    if (!Number.isSafeInteger(value)) fail("json.integer-range", "canonical JSON accepts only exact integers", 2);
    return String(value);
  }
  if (typeof value === "string") return JSON.stringify(value).replaceAll(" ", "\\u2028").replaceAll(" ", "\\u2029");
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (isPlainObject(value)) return `{${Object.keys(value).sort().map(key => `${canonicalJson(key)}:${canonicalJson(value[key])}`).join(",")}}`;
  fail("json.type", "value cannot be encoded as canonical JSON", 2);
}

function objectValue(value, field, exitClass = 4) { if (!isPlainObject(value)) fail("json.type", "expected object", exitClass, { field }); return value; }
function arrayValue(value, field, exitClass = 4) { if (!Array.isArray(value)) fail("json.type", "expected array", exitClass, { field }); return value; }
function closed(obj, required, field, exitClass = 4) {
  const missing = required.filter(key => !Object.hasOwn(obj, key));
  if (missing.length) fail("json.missing-field", "required field is missing", exitClass, { field, expected: required, actual: missing });
  const unknown = Object.keys(obj).filter(key => !required.includes(key));
  if (unknown.length) fail("json.unknown-field", "object contains an unknown field", exitClass, { field, expected: required, actual: unknown });
}
function literal(value, expected, field, code, exitClass = 4) { if (value !== expected) fail(code, "value does not match the required literal", exitClass, { field, expected, actual: value }); }

function portablePath(value, field, { allowDot = false, exitClass = 4 } = {}) {
  if (typeof value !== "string") fail("json.type", "path must be a string", exitClass, { field });
  if (allowDot && value === ".") return value;
  if (value.startsWith("/") || /^[A-Za-z]:/.test(value) || value.startsWith("//")) fail("path.absolute", "path must be relative", exitClass, { field, actual: value });
  if (value.includes("\\")) fail("path.backslash", "path must use forward slashes", exitClass, { field, actual: value });
  if (value.includes("\0")) fail("path.nul", "path contains NUL", exitClass, { field });
  if (!value) fail("path.empty-segment", "path is empty", exitClass, { field });
  const devices = /^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i;
  const parts = value.split("/");
  for (const part of parts) {
    if (!part || part === "." || part === "..") fail(part === ".." ? "path.traversal" : part === "." ? "path.dot-segment" : "path.empty-segment", "path contains a forbidden segment", exitClass, { field, actual: value });
    if (devices.test(part)) fail("path.reserved-name", "path contains a reserved device name", exitClass, { field, actual: value });
    if (/[. ]$/.test(part)) fail("path.nonportable", "path contains a nonportable segment", exitClass, { field, actual: value });
    if (!/^[A-Za-z0-9._-]+$/.test(part) || part.includes(":")) fail("path.portable", "path contains a nonportable segment", exitClass, { field, actual: value });
  }
  return value;
}
const pathKey = value => value.split("/").map(part => part.toLowerCase());
const keyText = value => pathKey(value).join("/");
function within(child, parent, allowEqual = true) { const c = keyText(child); const p = keyText(parent); return (allowEqual && c === p) || c.startsWith(`${p}/`); }
function overlaps(a, b) { return within(a, b) || within(b, a); }
function windowsDirent(target) {
  if (process.platform !== "win32") return null;
  try {
    const base = path.basename(target).toLowerCase();
    return fs.readdirSync(path.dirname(target), { withFileTypes: true }).find(item => item.name.toLowerCase() === base) ?? null;
  } catch { return null; }
}
function lstatKind(target, dirent = null) {
  const entry = dirent ?? windowsDirent(target);
  if (process.platform === "win32" && entry?.isSymbolicLink()) {
    try { fs.readlinkSync(target); return "symlink"; }
    catch (error) {
      if (error.code !== "EINVAL") throw error;
      const refreshed = windowsDirent(target);
      if (!refreshed?.isSymbolicLink()) throw error;
      return "unsupported-file";
    }
  }
  try {
    const stat = fs.lstatSync(target);
    if (stat.isSymbolicLink()) return "symlink";
    return stat.isDirectory() ? "directory" : stat.isFile() ? "regular-file" : "unsupported-file";
  } catch (error) {
    if (error.code === "ENOENT" || error.code === "ENOTDIR") return "missing";
    throw error;
  }
}
function physicalDirectory(value, label, exitClass = 3) {
  if (typeof value !== "string" || !value) fail("command.option", `${label} is required`, 2, { field: label });
  let resolved;
  try { resolved = fs.realpathSync.native(value); } catch (error) { fail("workspace.invalid", `${label} must name an existing directory`, exitClass, { path: value, actual: error.message }); }
  if (lstatKind(resolved) !== "directory") fail("workspace.invalid", `${label} must name an existing directory`, exitClass, { path: value });
  return resolved;
}
function inspectContained(owner, relative, { requireKind = null, exitClass = 4 } = {}) {
  let current = owner;
  for (const segment of relative === "." ? [] : relative.split("/")) {
    current = path.join(current, segment);
    const kind = lstatKind(current);
    if (kind === "symlink") fail("path.symlink", "managed path contains a symbolic link", exitClass, { path: relative });
    if (kind === "missing") break;
  }
  if (fs.existsSync(current)) {
    const real = fs.realpathSync.native(current);
    if (!(real === owner || real.startsWith(`${owner}${path.sep}`))) fail("path.traversal", "managed path escapes its owner", exitClass, { path: relative });
  }
  if (requireKind && lstatKind(path.join(owner, relative)) !== requireKind) fail("manifest.path-missing", "declared path is missing or has the wrong type", exitClass, { path: relative, expected: requireKind });
}

function validateManifest(value, workspace, { live = true } = {}) {
  const manifest = objectValue(value, "/");
  const fields = ["format", "schemaVersion", "recordRoot", "entrypoint", "canonicalBaseline", "modules", "generatedArtifacts"];
  closed(manifest, fields, "/");
  literal(manifest.format, "wayfinder-project-record", "/format", "manifest.format");
  literal(manifest.schemaVersion, 1, "/schemaVersion", "manifest.unsupported-version");
  const recordRoot = portablePath(manifest.recordRoot, "/recordRoot", { allowDot: true });
  const recordRootPath = recordRoot === "." ? workspace : path.join(workspace, ...recordRoot.split("/"));
  inspectContained(workspace, recordRoot, { requireKind: live ? "directory" : null });
  const entrypoint = portablePath(manifest.entrypoint, "/entrypoint");
  if (!entrypoint.toLowerCase().endsWith(".md")) fail("manifest.entrypoint", "entrypoint must end in .md", 4, { field: "/entrypoint" });
  const baseline = objectValue(manifest.canonicalBaseline, "/canonicalBaseline");
  if (baseline.kind === "git-ref") {
    closed(baseline, ["kind", "ref"], "/canonicalBaseline");
    if (typeof baseline.ref !== "string" || !/^refs\/[A-Za-z0-9._/-]+$/.test(baseline.ref) || baseline.ref.includes("..")) fail("manifest.baseline", "git-ref baseline is invalid", 4, { field: "/canonicalBaseline/ref" });
  } else if (baseline.kind === "snapshot") {
    closed(baseline, ["kind", "path", "sha256"], "/canonicalBaseline");
    const snapshot = portablePath(baseline.path, "/canonicalBaseline/path");
    if (!within(snapshot, ".wayfinder/baselines")) fail("manifest.snapshot-path", "snapshot must be beneath .wayfinder/baselines", 4, { field: "/canonicalBaseline/path" });
    if (typeof baseline.sha256 !== "string" || !HEX.test(baseline.sha256)) fail("manifest.baseline", "snapshot digest is invalid", 4, { field: "/canonicalBaseline/sha256" });
    inspectContained(workspace, snapshot, { requireKind: live ? "regular-file" : null });
  } else fail("manifest.baseline", "baseline kind is invalid", 4, { field: "/canonicalBaseline/kind" });
  const modules = arrayValue(manifest.modules, "/modules");
  const moduleIds = new Set(); const roots = []; const entrypoints = new Set([keyText(entrypoint)]); const collections = [];
  for (let i = 0; i < modules.length; i += 1) {
    const module = objectValue(modules[i], `/modules/${i}`); closed(module, ["id", "root", "entrypoint", "subjects"], `/modules/${i}`);
    if (typeof module.id !== "string" || !(STANDARD_MODULES.includes(module.id) || /^local-[a-z0-9]+(?:-[a-z0-9]+)*$/.test(module.id))) fail("manifest.module-id", "module ID is invalid", 4, { field: `/modules/${i}/id` });
    if (moduleIds.has(module.id)) fail("manifest.duplicate-module-id", "module IDs must be unique", 4, { field: `/modules/${i}/id` }); moduleIds.add(module.id);
    const root = portablePath(module.root, `/modules/${i}/root`); const moduleEntry = portablePath(module.entrypoint, `/modules/${i}/entrypoint`);
    if (!within(moduleEntry, root) || !moduleEntry.toLowerCase().endsWith(".md")) fail("manifest.entrypoint-outside-owner", "module entrypoint must be Markdown inside its root", 4, { field: `/modules/${i}/entrypoint` });
    if (roots.some(other => overlaps(root, other))) fail("manifest.module-root-overlap", "module roots overlap", 4, { field: `/modules/${i}/root` }); roots.push(root);
    if (entrypoints.has(keyText(moduleEntry))) fail("manifest.entrypoint-duplicate", "entrypoints must be unique", 4, { field: `/modules/${i}/entrypoint` }); entrypoints.add(keyText(moduleEntry));
    inspectContained(recordRootPath, root, { requireKind: live ? "directory" : null }); inspectContained(recordRootPath, moduleEntry, { requireKind: live ? "regular-file" : null });
    const subjects = arrayValue(module.subjects, `/modules/${i}/subjects`); const subjectIds = new Set(); const moduleCollections = [];
    for (let j = 0; j < subjects.length; j += 1) {
      const subject = objectValue(subjects[j], `/modules/${i}/subjects/${j}`);
      const expected = subject.kind === "collection" ? ["id", "kind", "root", "entrypoint"] : ["id", "kind", "entrypoint"];
      closed(subject, expected, `/modules/${i}/subjects/${j}`);
      if (typeof subject.id !== "string" || !SLUG.test(subject.id)) fail("manifest.subject-id", "subject ID is invalid", 4, { field: `/modules/${i}/subjects/${j}/id` });
      if (subjectIds.has(subject.id)) fail("manifest.duplicate-subject-id", "subject ID is duplicated", 4, { field: `/modules/${i}/subjects/${j}/id` }); subjectIds.add(subject.id);
      if (!["document", "collection"].includes(subject.kind)) fail("manifest.subject-kind", "subject kind is invalid", 4, { field: `/modules/${i}/subjects/${j}/kind` });
      const subjectEntry = portablePath(subject.entrypoint, `/modules/${i}/subjects/${j}/entrypoint`);
      if (!within(subjectEntry, root) || !subjectEntry.toLowerCase().endsWith(".md")) fail("manifest.entrypoint-outside-owner", "subject entrypoint must be Markdown inside its module", 4, { field: `/modules/${i}/subjects/${j}/entrypoint` });
      if (entrypoints.has(keyText(subjectEntry))) fail("manifest.entrypoint-duplicate", "entrypoints must be unique", 4, { field: `/modules/${i}/subjects/${j}/entrypoint` }); entrypoints.add(keyText(subjectEntry));
      if (subject.kind === "collection") {
        const collectionRoot = portablePath(subject.root, `/modules/${i}/subjects/${j}/root`);
        if (!within(collectionRoot, root)) fail("manifest.subject-containment", "collection root must be inside its module", 4, { field: `/modules/${i}/subjects/${j}/root` });
        if (moduleCollections.some(other => overlaps(collectionRoot, other))) fail("manifest.subject-root-overlap", "collection roots overlap", 4, { field: `/modules/${i}/subjects/${j}/root` }); moduleCollections.push(collectionRoot); collections.push(collectionRoot);
        if (!within(subjectEntry, collectionRoot)) fail("manifest.subject-containment", "collection entrypoint must be inside its root", 4, { field: `/modules/${i}/subjects/${j}/entrypoint` });
        inspectContained(recordRootPath, collectionRoot, { requireKind: live ? "directory" : null });
      } else if (moduleCollections.some(collectionRoot => within(subjectEntry, collectionRoot))) fail("manifest.subject-containment", "document subject may not be inside a collection", 4, { field: `/modules/${i}/subjects/${j}/entrypoint` });
      inspectContained(recordRootPath, subjectEntry, { requireKind: live ? "regular-file" : null });
    }
    for (const subject of subjects.filter(item => item.kind === "document")) if (moduleCollections.some(collectionRoot => within(subject.entrypoint, collectionRoot))) fail("manifest.document-in-collection", "document subject may not be inside a collection", 4, { field: `/modules/${i}/subjects` });
  }
  if (!moduleIds.has("decisions")) fail("manifest.required-module", "decisions module is required", 4, { field: "/modules" });
  inspectContained(recordRootPath, entrypoint, { requireKind: live ? "regular-file" : null });
  const artifacts = arrayValue(manifest.generatedArtifacts, "/generatedArtifacts"); const artifactPaths = new Set();
  for (let i = 0; i < artifacts.length; i += 1) {
    const artifact = objectValue(artifacts[i], `/generatedArtifacts/${i}`); closed(artifact, ["path", "generator"], `/generatedArtifacts/${i}`);
    const artifactPath = portablePath(artifact.path, `/generatedArtifacts/${i}/path`);
    if (artifact.generator !== "document-catalog-v1") fail("manifest.unknown-generator", "generator is not registered", 4, { field: `/generatedArtifacts/${i}/generator` });
    if (artifactPaths.has(keyText(artifactPath)) || entrypoints.has(keyText(artifactPath))) fail("manifest.artifact-entrypoint-conflict", "generated artifact path collides", 4, { field: `/generatedArtifacts/${i}/path` }); artifactPaths.add(keyText(artifactPath));
    inspectContained(recordRootPath, artifactPath, { requireKind: live ? "regular-file" : null });
  }
  return manifest;
}

function readStrictFile(target, label, { governed = false, exitClass = 4 } = {}) {
  let raw;
  try { raw = fs.readFileSync(target); } catch (error) { fail("manifest.path-missing", `${label} cannot be read`, exitClass, { path: target, actual: error.message }); }
  return [raw, strictJsonBytes(raw, label, { governed, exitClass })];
}

function validateRelease(value) {
  const release = objectValue(value, "/", 2); closed(release, ["format", "schemaVersion", "releaseId", "status", "contractVersion", "contractManifest", "adapters", "certifications"], "/", 2);
  literal(release.format, "wayfinder-contract-release", "/format", "package.release-format", 2); literal(release.schemaVersion, 1, "/schemaVersion", "package.release-version", 2);
  literal(release.releaseId, RELEASE_ID, "/releaseId", "package.release-id", 2); literal(release.status, RELEASE_STATUS, "/status", "package.activation-state", 2); literal(release.contractVersion, 1, "/contractVersion", "package.contract-version", 2);
  const contract = objectValue(release.contractManifest, "/contractManifest", 2); closed(contract, ["path", "sha256"], "/contractManifest", 2); literal(contract.path, CONTRACT_PATH, "/contractManifest/path", "package.contract-path", 2);
  const adapters = arrayValue(release.adapters, "/adapters", 2); if (!adapters.length) fail("package.adapter-entry", "release must list at least one adapter", 2, { field: "/adapters" });
  const ids = new Set(), paths = new Set(); let current = null;
  for (let i = 0; i < adapters.length; i += 1) {
    const item = objectValue(adapters[i], `/adapters/${i}`, 2); closed(item, ["id", "path", "sha256"], `/adapters/${i}`, 2);
    if (typeof item.id !== "string" || !/^[a-z0-9]+(?:-[a-z0-9]+)*-v1$/.test(item.id)) fail("package.adapter-entry", "adapter ID is invalid", 2, { field: `/adapters/${i}/id` });
    const adapterPath = portablePath(item.path, `/adapters/${i}/path`, { exitClass: 2 });
    if (!/^scripts\/adapters\/[a-z0-9]+(?:-[a-z0-9]+)*\.(?:py|mjs|ps1)$/.test(adapterPath) || ids.has(item.id) || paths.has(keyText(adapterPath))) fail("package.adapter-entry", "adapter ID or path is invalid or duplicated", 2, { field: `/adapters/${i}` });
    ids.add(item.id); paths.add(keyText(adapterPath)); if (item.id === ADAPTER_ID) current = item;
  }
  if (!current || current.path !== ADAPTER_PATH) fail("package.adapter-entry", "release does not identify the executing adapter", 2, { field: "/adapters" });
  if (!HEX.test(contract.sha256) || !HEX.test(current.sha256)) fail("package.digest-format", "package digest must be lowercase 64-hex", 2);
  const certifications = arrayValue(release.certifications, "/certifications", 2); if (certifications.length) fail("package.certification-state", "unactivated release must not claim certification", 2, { field: "/certifications" });
  return release;
}

function validateContract(value) {
  const contract = objectValue(value, "/", 2); closed(contract, ["format", "schemaVersion", "contractVersion", "candidateRevision", "status", "governedScopes", "governedResources", "registries"], "/", 2);
  literal(contract.format, "wayfinder-executable-contract", "/format", "package.contract-format", 2); literal(contract.schemaVersion, 1, "/schemaVersion", "package.contract-schema-version", 2);
  literal(contract.contractVersion, 1, "/contractVersion", "package.contract-version", 2); literal(contract.candidateRevision, CANDIDATE_REVISION, "/candidateRevision", "package.candidate-revision", 2); literal(contract.status, CONTRACT_STATUS, "/status", "package.activation-state", 2);
  const scopes = arrayValue(contract.governedScopes, "/governedScopes", 2); const resources = arrayValue(contract.governedResources, "/governedResources", 2); const listed = new Set();
  for (let i = 0; i < scopes.length; i += 1) { const item = objectValue(scopes[i], `/governedScopes/${i}`, 2); closed(item, ["path", "recursive"], `/governedScopes/${i}`, 2); portablePath(item.path, `/governedScopes/${i}/path`, { exitClass: 2 }); if (typeof item.recursive !== "boolean") fail("json.type", "recursive must be boolean", 2, { field: `/governedScopes/${i}/recursive` }); }
  for (let i = 0; i < resources.length; i += 1) { const item = objectValue(resources[i], `/governedResources/${i}`, 2); closed(item, ["path", "role", "sha256"], `/governedResources/${i}`, 2); const itemPath = portablePath(item.path, `/governedResources/${i}/path`, { exitClass: 2 }); if (listed.has(itemPath)) fail("package.duplicate-resource", "governed resource is duplicated", 2, { field: `/governedResources/${i}/path` }); listed.add(itemPath); if (typeof item.role !== "string" || !SLUG.test(item.role)) fail("package.resource-role", "resource role is invalid", 2); if (typeof item.sha256 !== "string" || !HEX.test(item.sha256)) fail("package.digest-format", "resource digest is invalid", 2); }
  const registries = objectValue(contract.registries, "/registries", 2); closed(registries, ["commands", "exitClasses", "generators", "standardModules"], "/registries", 2);
  if (canonicalJson(registries.commands) !== canonicalJson(COMMANDS) || canonicalJson(registries.exitClasses) !== "[0,2,3,4,5,70]" || canonicalJson(registries.generators) !== '["document-catalog-v1","document-index-v1"]' || canonicalJson(registries.standardModules) !== canonicalJson(STANDARD_MODULES)) fail("package.registry", "contract registry does not match version 1", 2);
  return contract;
}

function walkFiles(target) {
  const values = [];
  function visit(current) {
    for (const name of fs.readdirSync(current).sort()) {
      const child = path.join(current, name); const stat = fs.lstatSync(child);
      if (stat.isSymbolicLink()) fail("package.resource-symlink", "governed resource may not be a symbolic link", 2, { path: child });
      if (stat.isDirectory()) visit(child); else if (stat.isFile()) values.push(child);
    }
  }
  if (lstatKind(target) === "directory") visit(target); else if (lstatKind(target) === "regular-file") values.push(target);
  return values;
}

function verifyPackage() {
  const skillRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../.."); const releaseFile = path.join(skillRoot, ...RELEASE_PATH.split("/"));
  let releaseRaw;
  try { releaseRaw = fs.readFileSync(releaseFile); }
  catch { fail("package.release-missing", "release descriptor cannot be read", 2, { path: releaseFile }); }
  let releaseValue;
  try { releaseValue = strictJsonBytes(releaseRaw, RELEASE_PATH, { governed: true, exitClass: 2 }); }
  catch (error) { if (error instanceof WFError) fail("package.release-invalid", `release descriptor is invalid: ${error.code}`, 2, { path: RELEASE_PATH, actual: error.code }); throw error; }
  const release = validateRelease(releaseValue);
  let adapterDigest = "";
  for (const adapter of release.adapters) {
    const target = path.join(skillRoot, ...adapter.path.split("/")); let raw;
    try { raw = fs.readFileSync(target); } catch (error) { fail("package.adapter-missing", "adapter cannot be read", 2, { path: adapter.path, actual: error.message }); }
    const observed = sha256(raw); if (observed !== adapter.sha256) fail("package.adapter-digest", "adapter digest does not match release descriptor", 2, { path: adapter.path, expected: adapter.sha256, actual: observed }); if (adapter.id === ADAPTER_ID) adapterDigest = observed;
  }
  const contractFile = path.join(skillRoot, ...CONTRACT_PATH.split("/")); let contractRaw;
  try { contractRaw = fs.readFileSync(contractFile); } catch (error) { fail("package.contract-missing", "contract manifest cannot be read", 2, { path: CONTRACT_PATH, actual: error.message }); }
  const contractDigest = sha256(contractRaw); if (contractDigest !== release.contractManifest.sha256) fail("package.contract-digest", "contract manifest digest does not match release descriptor", 2, { path: CONTRACT_PATH, expected: release.contractManifest.sha256, actual: contractDigest });
  let contractValue;
  try { contractValue = strictJsonBytes(contractRaw, CONTRACT_PATH, { governed: true, exitClass: 2 }); } catch (error) { if (error instanceof WFError) fail("package.contract-invalid", `contract manifest is invalid: ${error.code}`, 2, { path: CONTRACT_PATH, actual: error.code }); throw error; }
  const contract = validateContract(contractValue);
  const listed = new Map(contract.governedResources.map(item => [item.path, item])); const observed = new Set();
  for (const scope of contract.governedScopes) {
    const target = path.join(skillRoot, ...scope.path.split("/"));
    if (lstatKind(target) === "missing") { if (scope.recursive) fail("package.missing-scope", "governed scope is missing", 2, { path: scope.path }); continue; }
    for (const item of scope.recursive ? walkFiles(target) : [target]) observed.add(path.relative(skillRoot, item).split(path.sep).join("/"));
  }
  const unexpected = [...observed].filter(item => !listed.has(item)).sort(); const missing = [...listed.keys()].filter(item => !observed.has(item)).sort();
  if (unexpected.length) fail("package.unlisted-resource", "governed scope contains an unlisted resource", 2, { actual: unexpected }); if (missing.length) fail("package.missing-resource", "listed governed resource is missing", 2, { actual: missing });
  for (const [relative, resource] of [...listed.entries()].sort()) {
    const raw = fs.readFileSync(path.join(skillRoot, ...relative.split("/"))); const digest = sha256(raw); if (digest !== resource.sha256) fail("package.resource-digest", "governed resource digest mismatch", 2, { path: relative, expected: resource.sha256, actual: digest });
    if (raw.subarray(0, 3).equals(Buffer.from([0xef, 0xbb, 0xbf])) || raw.includes(0x0d) || raw.length === 0 || raw[raw.length - 1] !== 0x0a || (raw.length > 1 && raw[raw.length - 2] === 0x0a)) fail("package.resource-text-profile", "governed resource violates UTF-8/LF profile", 2, { path: relative });
    let text; try { text = new TextDecoder("utf-8", { fatal: true }).decode(raw); } catch { fail("package.resource-text-profile", "governed resource is not UTF-8", 2, { path: relative }); } if (text.normalize("NFC") !== text) fail("package.resource-text-profile", "governed resource is not NFC", 2, { path: relative });
  }
  const schemaPath = "assets/contract-v1/schemas/release.schema.json"; const schema = strictJsonBytes(fs.readFileSync(path.join(skillRoot, ...schemaPath.split("/"))), schemaPath, { governed: true, exitClass: 2 });
  const releaseIdSchema = schema?.properties?.releaseId, statusSchema = schema?.properties?.status, adapterSchema = schema?.properties?.adapters;
  const agrees = canonicalJson(releaseIdSchema) === canonicalJson({ type: "string", pattern: "^v1-candidate-revision-[1-9][0-9]*$" }) && canonicalJson(statusSchema) === canonicalJson({ enum: ["unactivated-candidate", "unactivated-frozen", "activated-frozen"] }) && adapterSchema?.type === "array" && adapterSchema?.minItems === 1 && adapterSchema?.items?.properties?.id?.pattern === "^[a-z0-9]+(?:-[a-z0-9]+)*-v1$" && adapterSchema?.items?.properties?.path?.pattern === "^scripts/adapters/[a-z0-9]+(?:-[a-z0-9]+)*\\.(?:py|mjs|ps1)$";
  if (!agrees || !/^v1-candidate-revision-[1-9][0-9]*$/.test(release.releaseId)) fail("package.release-schema", "release schema and descriptor identities disagree", 2, { path: schemaPath });
  return { skillRoot, release, releaseDigest: sha256(releaseRaw), contract, contractDigest, adapterDigest };
}

function runKnownAnswers(pkg) {
  const relative = "assets/contract-v1/known-answer.json"; const target = path.join(pkg.skillRoot, ...relative.split("/")); const raw = fs.readFileSync(target); const known = strictJsonBytes(raw, relative, { governed: true, exitClass: 2 });
  const obj = objectValue(known, "/", 2); closed(obj, ["format", "schemaVersion", "canonicalJson", "sha256", "nfc", "portablePaths"], "/", 2); literal(obj.format, "wayfinder-known-answer", "/format", "probe.known-answer-format", 2); literal(obj.schemaVersion, 1, "/schemaVersion", "probe.known-answer-version", 2);
  let count = 0;
  for (const vector of obj.canonicalJson) { if (canonicalJson(vector.input) !== vector.expected) fail("probe.known-answer", "canonical JSON known answer failed", 2); count += 1; }
  for (const vector of obj.sha256) { if (sha256(Buffer.from(vector.utf8)) !== vector.expected) fail("probe.known-answer", "SHA-256 known answer failed", 2); count += 1; }
  for (const vector of obj.nfc) { if (String.fromCodePoint(...vector.codePoints).normalize("NFC") !== vector.expected) fail("probe.known-answer", "NFC known answer failed", 2); count += 1; }
  for (const vector of obj.portablePaths) { let accepted = true; try { portablePath(vector.value, "/portablePaths", { allowDot: vector.allowDot === true, exitClass: 2 }); } catch (error) { if (error instanceof WFError) accepted = false; else throw error; } if (accepted !== vector.accepted) fail("probe.known-answer", "portable path known answer failed", 2); count += 1; }
  return { passed: true, count, vectorsDigest: sha256(raw) };
}

function commandProbe() {
  const major = Number(process.versions.node.split(".")[0]); if (major < 22) fail("runtime.unsupported", "Node.js 22 or newer is required", 2, { actual: process.version });
  const pkg = verifyPackage(), knownAnswers = runKnownAnswers(pkg);
  return {
    adapter: { id: ADAPTER_ID, path: ADAPTER_PATH, sha256: pkg.adapterDigest },
    contract: { version: pkg.release.contractVersion, releaseId: pkg.release.releaseId, status: pkg.release.status, releaseDescriptor: RELEASE_PATH, releaseSha256: pkg.releaseDigest, manifest: CONTRACT_PATH, manifestSha256: pkg.contractDigest, resources: pkg.contract.governedResources },
    deterministic: { knownAnswers, capabilities: CAPABILITIES },
    environment: { implementation: "Node.js", version: process.versions.node, platform: process.platform, architecture: process.arch },
  };
}

function manifestAt(directory) {
  const control = path.join(directory, ".wayfinder"); const controlKind = lstatKind(control);
  if (controlKind === "symlink") fail("discover.control-symlink", "discovery control directory is symbolic", 4, { path: control });
  const target = path.join(control, "manifest.json"); const kind = lstatKind(target);
  if (kind === "symlink") fail("discover.manifest-symlink", "manifest is symbolic", 4, { path: target });
  return kind === "regular-file" ? target : kind === "missing" ? null : fail("manifest.path-type", "manifest path is not a regular file", 4, { path: target });
}
function gitBoundary(start) {
  let current = start;
  while (true) {
    const kind = lstatKind(path.join(current, ".git")); if (["directory", "regular-file", "symlink"].includes(kind)) return current;
    const parent = path.dirname(current); if (parent === current) return null; current = parent;
  }
}
function loadLiveManifest(workspace, target) { const raw = fs.readFileSync(target); const value = strictJsonBytes(raw, path.relative(workspace, target).split(path.sep).join("/") || ".wayfinder/manifest.json", { exitClass: 4 }); return validateManifest(value, workspace); }
function commandDiscover(options) {
  let workspace, manifestPath;
  if (options["workspace-root"] !== undefined) { workspace = physicalDirectory(options["workspace-root"], "--workspace-root"); manifestPath = manifestAt(workspace); if (!manifestPath) fail("discover.manifest-not-found", "workspace does not contain a Wayfinder manifest", 3, { path: workspace }); }
  else {
    let start = options.start ?? process.cwd(); let resolved; try { resolved = fs.realpathSync.native(start); } catch (error) { fail("discover.start", "discovery start does not exist", 3, { path: start, actual: error.message }); }
    if (lstatKind(resolved) === "regular-file") resolved = path.dirname(resolved); if (lstatKind(resolved) !== "directory") fail("discover.start", "discovery start must be a file or directory", 3, { path: start });
    const stop = gitBoundary(resolved); let current = resolved; manifestPath = null;
    while (true) { const found = manifestAt(current); if (found) { workspace = current; manifestPath = found; break; } if ((stop && current === stop) || path.dirname(current) === current) break; current = path.dirname(current); }
    if (!manifestPath) fail("discover.manifest-not-found", "no Wayfinder manifest was discovered", 3, { path: resolved });
  }
  const manifest = loadLiveManifest(workspace, manifestPath); const recordRoot = manifest.recordRoot === "." ? workspace : path.join(workspace, ...manifest.recordRoot.split("/"));
  return { workspace: { workspaceRoot: workspace, manifestPath, recordRoot: fs.realpathSync.native(recordRoot), entrypoint: path.join(recordRoot, ...manifest.entrypoint.split("/")) }, manifest };
}

const utf8Compare = (a, b) => Buffer.compare(Buffer.from(a, "utf8"), Buffer.from(b, "utf8"));

function sourcePath(value, field, exitClass = 2) {
  if (typeof value !== "string") fail("json.type", "source path must be a string", exitClass, { field });
  if (!value || value.startsWith("/") || /^[A-Za-z]:/.test(value) || value.startsWith("//")) fail("path.absolute", "source path must be relative", exitClass, { field, actual: value });
  if (value.includes("\\")) fail("path.backslash", "source path must use forward slashes", exitClass, { field, actual: value });
  if (value.includes("\0")) fail("path.nul", "source path contains NUL", exitClass, { field });
  const parts = value.split("/");
  if (parts.some(part => part === "")) fail("path.empty-segment", "source path contains an empty segment", exitClass, { field, actual: value });
  if (parts.some(part => part === ".")) fail("path.dot-segment", "source path contains a dot segment", exitClass, { field, actual: value });
  if (parts.some(part => part === "..")) fail("path.traversal", "source path contains traversal", exitClass, { field, actual: value });
  if (value.normalize("NFC") !== value) fail("text.non-nfc", "source path must be NFC", exitClass, { field });
  return value;
}

function strictInputFile(target, label, exitClass = 2) {
  if (typeof target !== "string" || !target) fail("command.option", `${label} is required`, 2, { field: label });
  if (lstatKind(target) === "symlink") fail("path.symlink", `${label} must not be symbolic`, exitClass, { path: target });
  if (lstatKind(target) !== "regular-file") fail("command.file", `${label} must be a regular file`, exitClass, { path: target });
  return readStrictFile(target, label, { exitClass });
}

function validateInventoryRequest(value) {
  const request = objectValue(value, "/", 2);
  closed(request, ["format", "schemaVersion", "selections", "targetRoots", "limits"], "/", 2);
  literal(request.format, "wayfinder-source-inventory-request", "/format", "inventory.format", 2);
  literal(request.schemaVersion, 1, "/schemaVersion", "inventory.unsupported-version", 2);
  const selections = arrayValue(request.selections, "/selections", 2);
  if (!selections.length) fail("inventory.selections", "at least one selection is required", 2, { field: "/selections" });
  const normalizedSelections = selections.map((item, index) => sourcePath(item, `/selections/${index}`));
  if (new Set(normalizedSelections).size !== normalizedSelections.length) fail("inventory.duplicate-selection", "inventory selections must be unique", 2, { field: "/selections" });
  const roots = arrayValue(request.targetRoots, "/targetRoots", 2).map((item, index) => sourcePath(item, `/targetRoots/${index}`));
  if (new Set(roots).size !== roots.length) fail("inventory.duplicate-target-root", "target roots must be unique", 2, { field: "/targetRoots" });
  const limits = objectValue(request.limits, "/limits", 2);
  closed(limits, ["maxEntries", "maxFileBytes", "maxTotalBytes", "maxDepth"], "/limits", 2);
  for (const name of ["maxEntries", "maxFileBytes", "maxTotalBytes", "maxDepth"]) {
    if (!Number.isSafeInteger(limits[name]) || limits[name] < 1 || (name === "maxEntries" && limits[name] > 1000000) || (name === "maxDepth" && limits[name] > 1024)) fail("json.type", "inventory limit must be a positive bounded integer", 2, { field: `/limits/${name}` });
  }
  return { ...request, selections: normalizedSelections, targetRoots: roots };
}

function markdownCues(text) {
  if (text.normalize("NFC") !== text) return { accepted: false, reason: "non-nfc-text", h1: null, outline: [] };
  const outline = []; let fence = null;
  const lines = text.split("\n");
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index]; const opening = /^( {0,3})(`{3,}|~{3,})(.*)$/.exec(line);
    if (fence) {
      const close = new RegExp(`^ {0,3}${fence.char}{${fence.length},}[ \\t]*$`);
      if (close.test(line)) fence = null;
      continue;
    }
    if (opening) { fence = { char: opening[2][0], length: opening[2].length }; continue; }
    const heading = /^( {0,3})(#{1,6})[ \\t]+(.+?)[ \\t]*$/.exec(line);
    if (!heading) continue;
    let value = heading[3].replace(/[ \\t]+#+[ \\t]*$/, "").trim();
    if (value) outline.push({ level: heading[2].length, text: value, line: index + 1 });
  }
  return { accepted: true, h1: outline.find(item => item.level === 1)?.text ?? null, outline };
}

function exclusionFor(relative, kind, targetRoots, explicitRegular) {
  if (kind === "symlink") return "symbolic-link";
  if (kind === "unsupported-file") return "unsupported-special-file";
  const parts = relative.split("/"); const base = parts.at(-1).toLowerCase();
  if (parts.some(part => [".git", ".hg", ".svn"].includes(part.toLowerCase()))) return "vcs-administration";
  if (parts.some(part => part.toLowerCase() === ".wayfinder")) return "wayfinder-state";
  if (targetRoots.some(root => within(relative, root))) return "declared-target-root";
  const secret = base === ".env" || base.startsWith(".env.") || /(?:^|[-_.])(?:private[-_.]?key|credentials?|secrets?)(?:[-_.]|$)/i.test(base) || /\.(?:pem|p12|pfx|key)$/i.test(base);
  if (secret) return "secret-safety";
  const dependency = parts.some(part => ["node_modules", "vendor", ".venv", "venv"].includes(part.toLowerCase()));
  const build = parts.some(part => ["build", "dist", "out", "target", "coverage", ".cache"].includes(part.toLowerCase()));
  const archive = /\.(?:zip|tar|tgz|gz|bz2|xz|7z|rar|jar|war)$/i.test(base);
  if (!explicitRegular) {
    if (dependency) return "dependency-directory";
    if (build) return "build-output-directory";
    if (archive && kind === "regular-file") return "archive-file";
  }
  return null;
}

function safeInventoryFile(workspace, relative, limit) {
  const target = path.join(workspace, ...relative.split("/"));
  let before;
  try { before = fs.lstatSync(target, { bigint: true }); } catch { fail("inventory.source-race", "source could not be inspected", 3, { path: relative }); }
  if (!before.isFile() || before.isSymbolicLink()) fail("inventory.source-race", "source changed during inventory", 3, { path: relative });
  if (before.size > BigInt(limit)) fail("inventory.limit-file-bytes", "source exceeds maxFileBytes", 3, { path: relative, expected: limit, actual: Number(before.size) });
  let raw;
  try { raw = fs.readFileSync(target); } catch { fail("inventory.source-race", "source could not be read safely", 3, { path: relative }); }
  let after;
  try { after = fs.lstatSync(target, { bigint: true }); } catch { fail("inventory.source-race", "source changed during inventory", 3, { path: relative }); }
  if (!after.isFile() || before.dev !== after.dev || before.ino !== after.ino || before.size !== after.size || before.mtimeNs !== after.mtimeNs || BigInt(raw.length) !== after.size) fail("inventory.source-race", "source changed during inventory", 3, { path: relative });
  return raw;
}

function buildInventory(workspace, request) {
  const entries = new Map(); const explicit = new Set(request.selections); let totalBytes = 0;
  const addEntry = (relative, depth, dirent = null) => {
    if (entries.has(relative)) return;
    if (depth > request.limits.maxDepth) fail("inventory.limit-depth", "inventory traversal exceeds maxDepth", 3, { path: relative, expected: request.limits.maxDepth, actual: depth });
    const target = path.join(workspace, ...relative.split("/")); const kind = lstatKind(target, dirent);
    if (kind === "missing") fail("inventory.selection-missing", "inventory selection is missing", 3, { path: relative });
    if (entries.size + 1 > request.limits.maxEntries) fail("inventory.limit-entries", "inventory exceeds maxEntries", 3, { expected: request.limits.maxEntries, actual: entries.size + 1 });
    const reason = exclusionFor(relative, kind, request.targetRoots, explicit.has(relative) && kind === "regular-file");
    const item = { path: relative, type: kind, included: reason === null, exclusion: reason, byteLength: null, sha256: null, content: null, markdown: null };
    if (kind === "regular-file") {
      let stat; try { stat = fs.lstatSync(target); } catch { fail("inventory.source-race", "source could not be inspected", 3, { path: relative }); }
      item.byteLength = stat.size;
      if (!reason) {
        const raw = safeInventoryFile(workspace, relative, request.limits.maxFileBytes);
        totalBytes += raw.length;
        if (totalBytes > request.limits.maxTotalBytes) fail("inventory.limit-total-bytes", "inventory exceeds maxTotalBytes", 3, { expected: request.limits.maxTotalBytes, actual: totalBytes });
        item.sha256 = sha256(raw);
        try { const text = new TextDecoder("utf-8", { fatal: true }).decode(raw); item.content = "strict-utf8"; if (relative.toLowerCase().endsWith(".md")) item.markdown = markdownCues(text); }
        catch { item.content = "opaque-bytes"; }
      }
    }
    entries.set(relative, item);
    if (kind === "directory" && !reason) {
      let children; try { children = fs.readdirSync(target, { withFileTypes: true }); } catch { fail("inventory.source-race", "directory could not be read", 3, { path: relative }); }
      children.sort((left, right) => utf8Compare(left.name, right.name));
      for (const child of children) addEntry(`${relative}/${child.name}`, depth + 1, child);
    }
  };
  for (const selection of [...request.selections].sort(utf8Compare)) {
    const parts = selection.split("/"); let current = workspace;
    for (let index = 0; index < parts.length - 1; index += 1) {
      current = path.join(current, parts[index]);
      if (lstatKind(current) === "symlink") fail("inventory.selection-symlink-component", "selection contains a symbolic-link component", 3, { path: selection });
    }
    addEntry(selection, 0);
  }
  const values = [...entries.values()].sort((a, b) => utf8Compare(a.path, b.path));
  const digestGroups = new Map();
  for (const item of values) if (item.included && item.type === "regular-file") { const paths = digestGroups.get(item.sha256) ?? []; paths.push(item.path); digestGroups.set(item.sha256, paths); }
  const duplicateGroups = [...digestGroups].filter(([, paths]) => paths.length > 1).sort(([a], [b]) => a.localeCompare(b)).map(([digest, paths]) => ({ sha256: digest, paths: paths.sort(utf8Compare) }));
  const byType = { "regular-file": 0, directory: 0, symlink: 0, "unsupported-file": 0 };
  values.forEach(item => { byType[item.type] += 1; });
  return {
    format: "wayfinder-source-inventory", schemaVersion: 1,
    selections: [...request.selections].sort(utf8Compare).map(item => ({ path: item, type: lstatKind(path.join(workspace, ...item.split("/"))) })),
    targetRoots: [...request.targetRoots].sort(utf8Compare), limits: request.limits, entries: values, duplicateGroups,
    summary: { entries: values.length, includedRegularFiles: values.filter(item => item.included && item.type === "regular-file").length, excluded: values.filter(item => !item.included).length, totalIncludedBytes: totalBytes, byType, duplicateGroups: duplicateGroups.length },
  };
}

function uniqueStrings(value, field, pattern, code = "intake.identifier") {
  const items = arrayValue(value, field, 2);
  if (new Set(items).size !== items.length) fail(code, "values must be unique", 2, { field });
  for (let index = 0; index < items.length; index += 1) if (typeof items[index] !== "string" || (pattern && !pattern.test(items[index]))) fail(code, "identifier is invalid", 2, { field: `${field}/${index}` });
  return items;
}

function validateIntake(value, inventory, inventoryDigest, workspace) {
  const ledger = objectValue(value, "/", 2); closed(ledger, ["format", "schemaVersion", "inventorySha256", "sources"], "/", 2);
  literal(ledger.format, "wayfinder-intake-ledger", "/format", "intake.format", 2); literal(ledger.schemaVersion, 1, "/schemaVersion", "intake.unsupported-version", 2);
  if (typeof ledger.inventorySha256 !== "string" || !HEX.test(ledger.inventorySha256)) fail("intake.inventory-digest", "inventory digest is invalid", 3, { field: "/inventorySha256" });
  const included = new Map(inventory.entries.filter(item => item.included && item.type === "regular-file").map(item => [item.path, item]));
  const sources = arrayValue(ledger.sources, "/sources", 2); const paths = new Set();
  const counts = { incorporate: 0, reference: 0, "preserve-out-of-scope": 0, unresolved: 0 };
  for (let index = 0; index < sources.length; index += 1) {
    const field = `/sources/${index}`; const source = objectValue(sources[index], field, 2);
    closed(source, ["path", "sha256", "byteLength", "disposition", "reason", "targetIds", "transformationNote", "evidenceKeys", "questionIds"], field, 2);
    sourcePath(source.path, `${field}/path`); if (paths.has(source.path)) fail("intake.duplicate-source", "ledger source paths must be unique", 2, { field: `${field}/path` }); paths.add(source.path);
    if (!included.has(source.path)) fail("intake.source-binding", "ledger source is not an included regular file", 2, { path: source.path });
    if (typeof source.sha256 !== "string" || !HEX.test(source.sha256) || !Number.isSafeInteger(source.byteLength) || source.byteLength < 0 || typeof source.reason !== "string" || !source.reason) fail("json.type", "ledger source field has the wrong type", 2, { field });
    if (!Object.hasOwn(counts, source.disposition)) fail("intake.disposition", "ledger disposition is invalid", 2, { field: `${field}/disposition` });
    const targets = uniqueStrings(source.targetIds, `${field}/targetIds`, DOC_ID); const evidence = uniqueStrings(source.evidenceKeys, `${field}/evidenceKeys`, SOURCE_ID); const questions = uniqueStrings(source.questionIds, `${field}/questionIds`, QUESTION_ID);
    if (source.transformationNote !== null && (typeof source.transformationNote !== "string" || !source.transformationNote)) fail("json.type", "transformationNote must be null or nonempty", 2, { field: `${field}/transformationNote` });
    if (source.disposition === "incorporate" && (!targets.length || !source.transformationNote || evidence.length || questions.length)) fail("intake.incorporate-fields", "incorporate disposition fields are invalid", 2, { field });
    if (source.disposition === "reference" && (!evidence.length || targets.length || questions.length || source.transformationNote !== null)) fail("intake.reference-fields", "reference disposition fields are invalid", 2, { field });
    if (source.disposition === "preserve-out-of-scope" && (targets.length || evidence.length || questions.length || source.transformationNote !== null)) fail("intake.preserve-fields", "preserve disposition fields are invalid", 2, { field });
    if (source.disposition === "unresolved" && (!questions.length || targets.length || evidence.length || source.transformationNote !== null)) fail("intake.unresolved-fields", "unresolved disposition fields are invalid", 2, { field });
    const expected = included.get(source.path); const raw = safeInventoryFile(workspace, source.path, Number.MAX_SAFE_INTEGER);
    if (raw.length !== source.byteLength || sha256(raw) !== source.sha256 || expected.byteLength !== source.byteLength || expected.sha256 !== source.sha256) fail("intake.source-stale", "ledger source bytes are stale", 3, { path: source.path });
    counts[source.disposition] += 1;
  }
  if (ledger.inventorySha256 !== inventoryDigest) fail("intake.inventory-digest", "ledger does not bind the current inventory", 3, { expected: inventoryDigest, actual: ledger.inventorySha256 });
  return { ledger, dispositionCounts: counts, sourceDigestsRechecked: sources.length };
}

function commandInventory(options) {
  const workspace = physicalDirectory(options["workspace-root"], "--workspace-root");
  const [, requestValue] = strictInputFile(options.request, "--request", 2); const request = validateInventoryRequest(requestValue);
  const inventory = buildInventory(workspace, request); const inventorySha256 = sha256(Buffer.from(canonicalJson(inventory)));
  const data = { inventory, inventorySha256, environment: { workspaceRoot: workspace } };
  if (options.ledger !== undefined) {
    const [ledgerRaw, ledgerValue] = strictInputFile(options.ledger, "--ledger", 2); const intake = validateIntake(ledgerValue, inventory, inventorySha256, workspace);
    data.intake = { ledger: intake.ledger, ledgerSha256: sha256(Buffer.from(canonicalJson(intake.ledger))), dispositionCounts: intake.dispositionCounts, sourceDigestsRechecked: intake.sourceDigestsRechecked };
  }
  return data;
}

function validDate(value) {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const [y, m, d] = value.split("-").map(Number); const date = new Date(Date.UTC(y, m - 1, d));
  return date.getUTCFullYear() === y && date.getUTCMonth() === m - 1 && date.getUTCDate() === d;
}
function idOrdinal(identifier, pattern, code, sourcePathValue) {
  const match = pattern.exec(identifier ?? "");
  if (!match || Number(match[1]) < 1 || (Number(match[1]) < 1000 && match[1].length !== 4) || match[2].length > 48) fail(code, "identifier is invalid", 4, { path: sourcePathValue, actual: identifier });
  return Number(match[1]);
}
function parseLink(value, code, sourcePathValue) {
  const match = /^\[(wf-[0-9]{4,}-[a-z0-9]+(?:-[a-z0-9]+)*)\]\(([^)]+)\)$/.exec(value);
  if (!match) fail(code, "typed link is invalid", 4, { path: sourcePathValue, actual: value });
  return { id: match[1], destination: match[2] };
}
function normalizeLink(ownerPath, destination) {
  if (!destination || destination.includes("\\") || destination.startsWith("/") || /^[A-Za-z]:/.test(destination) || destination.includes("\0")) fail("path.traversal", "link path is unsafe", 4, { path: destination });
  const value = path.posix.normalize(path.posix.join(path.posix.dirname(ownerPath), destination));
  if (value === ".." || value.startsWith("../") || path.posix.isAbsolute(value)) fail("path.traversal", "link escapes the record", 4, { path: destination });
  return value;
}

function readAuthored(target, relative) {
  let raw; try { raw = fs.readFileSync(target); } catch { fail("manifest.path-missing", "authored document cannot be read", 4, { path: relative }); }
  if (raw.subarray(0, 3).equals(Buffer.from([0xef, 0xbb, 0xbf]))) fail("text.bom", "document must not contain BOM", 4, { path: relative });
  if (raw.includes(0x0d)) fail("text.newline", "document must use LF", 4, { path: relative });
  if (!raw.length || raw[raw.length - 1] !== 0x0a || (raw.length > 1 && raw[raw.length - 2] === 0x0a)) fail("text.newline", "document must have exactly one terminal LF", 4, { path: relative });
  let text; try { text = new TextDecoder("utf-8", { fatal: true }).decode(raw); } catch { fail("text.invalid-utf8", "document is not valid UTF-8", 4, { path: relative }); }
  if (text.normalize("NFC") !== text) fail("text.non-nfc", "document must be NFC", 4, { path: relative });
  if (text.split("\n").some(line => /[ \t]+$/.test(line))) fail("text.trailing-whitespace", "document contains trailing whitespace", 4, { path: relative });
  return text;
}

function parseFieldBlock(lines, start, close, relative, family) {
  const values = []; let index = start;
  for (; index < lines.length && lines[index] !== close; index += 1) {
    const match = /^- \*\*([A-Za-z-]+):\*\* (.+)$/.exec(lines[index]);
    if (!match) fail(lines[index].startsWith("<!-- /wayfinder:") ? `${family}.delimiter` : `${family}.field-syntax`, `${family} field syntax is invalid`, 4, { path: relative, actual: lines[index] });
    values.push([match[1], match[2]]);
  }
  if (index >= lines.length) fail(`${family}.delimiter`, `${family} closing delimiter is missing`, 4, { path: relative });
  return { values, end: index };
}

function parseQuestionBlock(block, relative) {
  const lines = block.split("\n"); const anchor = /^<a id="([^"]+)"><\/a>$/.exec(lines[0] ?? ""); const title = /^### (.+)$/.exec(lines[1] ?? "");
  if (!anchor || !title) fail("question.anchor", "question anchor or title is invalid", 4, { path: relative });
  let cursor = 2; const fields = [];
  while (cursor < lines.length && lines[cursor] !== "") { const match = /^- \*\*([A-Za-z-]+):\*\* (.+)$/.exec(lines[cursor]); if (!match) fail("question.field-syntax", "question field is invalid", 4, { path: relative }); fields.push([match[1], match[2]]); cursor += 1; }
  const names = fields.map(([name]) => name); const first = Object.fromEntries(fields);
  if (!first.ID || anchor[1] !== first.ID) fail("question.anchor", "question anchor must equal ID", 4, { path: relative });
  const ordinal = idOrdinal(first.ID, QUESTION_ID, "record.question-id", relative);
  if (!first.State || !["Open", "Investigating", "Deferred", "Resolved", "Retired"].includes(first.State)) fail("question.state", "question state is invalid", 4, { path: relative });
  if (!validDate(first.Raised)) fail("record.date", "question raised date is invalid", 4, { path: relative });
  const applies = fields.filter(([name]) => name === "Applies-To").map(([, value]) => parseLink(value, "question.target", relative));
  const scope = fields.find(([name]) => name === "Scope")?.[1] ?? null;
  if ((scope === "Record-Wide") === (applies.length > 0)) fail("question.scope", "question needs exactly one scope form", 4, { path: relative });
  const addressed = fields.filter(([name]) => name === "Addressed-By").map(([, value]) => parseLink(value, "question.target", relative));
  const resolved = fields.filter(([name]) => name === "Resolved-By").map(([, value]) => parseLink(value, "question.target", relative));
  const resolutionDate = first["Resolution-Date"] ?? null;
  if (first.State === "Resolved" ? (!resolved.length || !validDate(resolutionDate)) : (resolved.length || resolutionDate !== null)) fail("question.conditional-content", "question conditional fields do not match state", 4, { path: relative });
  const expectedSections = { Open: ["Why it matters", "Next step", "History"], Investigating: ["Why it matters", "Current activity", "History"], Deferred: ["Why it matters", "Deferral reason", "Revisit trigger", "History"], Resolved: ["Why it matters", "Resolution", "History"], Retired: ["Why it matters", "Retirement reason", "History"] }[first.State];
  const sections = []; const contents = {};
  while (cursor < lines.length) {
    if (lines[cursor] === "") { cursor += 1; continue; }
    const heading = /^#### (.+)$/.exec(lines[cursor]); if (!heading) fail("question.conditional-content", "question section is invalid", 4, { path: relative });
    cursor += 1; if (lines[cursor] !== "") fail("question.conditional-content", "question section spacing is invalid", 4, { path: relative }); cursor += 1;
    const body = []; while (cursor < lines.length && !lines[cursor].startsWith("#### ")) { body.push(lines[cursor]); cursor += 1; }
    while (body.at(-1) === "") body.pop(); if (!body.length) fail("question.conditional-content", "question section is empty", 4, { path: relative });
    sections.push(heading[1]); contents[heading[1]] = body.join("\n");
  }
  if (canonicalJson(sections) !== canonicalJson(expectedSections)) fail("question.conditional-content", "question sections do not match state", 4, { path: relative, expected: expectedSections, actual: sections });
  const history = contents.History.split("\n"); let previous = "None";
  const allowed = { None: new Set(["Open", "Investigating", "Deferred", "Resolved", "Retired"]), Open: new Set(["Investigating", "Deferred", "Resolved", "Retired"]), Investigating: new Set(["Open", "Deferred", "Resolved", "Retired"]), Deferred: new Set(["Open", "Investigating", "Resolved", "Retired"]), Resolved: new Set(["Open", "Retired"]), Retired: new Set() };
  for (let index = 0; index < history.length; index += 1) {
    const match = /^- (\d{4}-\d{2}-\d{2}): (None|Open|Investigating|Deferred|Resolved|Retired) -> (Open|Investigating|Deferred|Resolved|Retired) - (.+)$/.exec(history[index]);
    if (!match || !validDate(match[1]) || match[2] !== previous) fail("question.history-state", "question history is not continuous", 4, { path: relative });
    if (!allowed[match[2]].has(match[3])) fail("question.transition", "question transition is not allowed", 4, { path: relative });
    if (match[2] === "Resolved" && match[3] === "Open" && !/reopen/i.test(match[4])) fail("question.reopen-reason", "reopened question history must say reopen", 4, { path: relative });
    previous = match[3];
  }
  if (previous !== first.State) fail("question.history-state", "question history does not end at current state", 4, { path: relative });
  const resumption = first.State === "Open" ? contents["Next step"] : first.State === "Investigating" ? contents["Current activity"] : first.State === "Deferred" ? contents["Revisit trigger"] : first.State === "Resolved" ? contents.Resolution : contents["Retirement reason"];
  return { id: first.ID, ordinal, title: title[1], state: first.State, raised: first.Raised, applies, addressed, resolved, resolutionDate, scope, sections: contents, resumption };
}

function parseSourceBlock(block, relative) {
  const lines = block.split("\n"); const anchor = /^<a id="([^"]+)"><\/a>$/.exec(lines[0] ?? ""); const title = /^### (src-[0-9]{2,}) — (.+)$/.exec(lines[1] ?? "");
  if (!anchor || !title || anchor[1] !== title[1]) fail("source.anchor", "source anchor and key differ", 4, { path: relative });
  const key = title[1]; if (!SOURCE_ID.test(key) || Number(SOURCE_ID.exec(key)[1]) < 1) fail("source.anchor", "source key is invalid", 4, { path: relative });
  let cursor = 2; const fields = [];
  while (cursor < lines.length && lines[cursor] !== "") { const match = /^- \*\*([A-Za-z-]+):\*\* (.+)$/.exec(lines[cursor]); if (!match) fail("source.field-syntax", "source field is invalid", 4, { path: relative }); fields.push([match[1], match[2]]); cursor += 1; }
  const names = fields.map(([name]) => name); if (new Set(names).size !== names.length) fail("source.duplicate-field", "source field is duplicated", 4, { path: relative });
  const required = ["Citation", "Original", ...(names.includes("Published") ? ["Published"] : []), "Accessed", "Applicability"];
  if (canonicalJson(names) !== canonicalJson(required)) fail("source.missing-field", "source fields are missing or out of order", 4, { path: relative, expected: required, actual: names });
  const values = Object.fromEntries(fields); if (!validDate(values.Accessed) || (values.Published && !validDate(values.Published))) fail("record.date", "source date is invalid", 4, { path: relative });
  if (!["Direct", "Adjacent", "General"].includes(values.Applicability)) fail("source.applicability", "source applicability is invalid", 4, { path: relative });
  const sections = {};
  while (cursor < lines.length) { if (lines[cursor] === "") { cursor += 1; continue; } const heading = /^#### (Used for|Limitations)$/.exec(lines[cursor]); if (!heading) fail("source.section", "source section is invalid", 4, { path: relative }); cursor += 2; const body=[]; while(cursor<lines.length&&!lines[cursor].startsWith("#### ")){body.push(lines[cursor]);cursor+=1;} while(body.at(-1)==="")body.pop(); if(!body.length)fail("source.section","source section is empty",4,{path:relative}); sections[heading[1]]=body.join("\n"); }
  if (!sections["Used for"] || !sections.Limitations) fail("source.section", "source sections are incomplete", 4, { path: relative });
  return { key, title: title[2], citation: values.Citation, original: values.Original, published: values.Published ?? null, accessed: values.Accessed, applicability: values.Applicability, usedFor: sections["Used for"], limitations: sections.Limitations };
}

function parseDocument(text, relative, workspace) {
  const lines = text.slice(0, -1).split("\n"); const title = /^# (.+)$/.exec(lines[0] ?? "");
  if (!title || lines[1] !== "" || lines[2] !== "<!-- wayfinder:metadata -->") fail(!title ? "document.h1" : "metadata.location", "document envelope is invalid", 4, { path: relative });
  if (lines.filter(line => /^# /.test(line)).length !== 1) fail("document.h1", "document must contain exactly one H1", 4, { path: relative });
  const metadata = parseFieldBlock(lines, 3, "<!-- /wayfinder:metadata -->", relative, "metadata"); const names = metadata.values.map(([name]) => name);
  if (new Set(names).size !== names.length) fail("metadata.duplicate-field", "metadata field is duplicated", 4, { path: relative });
  const allowed = ["ID", "Kind", "Status", "Updated", "Summary", "Decision-Date", "Supersedes", "Superseded-By"];
  const unknown = names.find(name => !allowed.includes(name)); if (unknown) fail("metadata.unknown-field", "metadata field is unknown", 4, { path: relative, actual: unknown });
  const required = ["ID", "Kind", "Status", "Updated", "Summary"];
  if (required.some(name => !names.includes(name))) fail("metadata.missing-field", "metadata field is missing", 4, { path: relative });
  if (names.some((name, index) => allowed.indexOf(name) < (index ? allowed.indexOf(names[index - 1]) : -1))) fail("metadata.field-order", "metadata fields are out of order", 4, { path: relative });
  const fields = Object.fromEntries(metadata.values); const ordinal = idOrdinal(fields.ID, DOC_ID, "record.document-id", relative);
  const kinds = ["map", "brief", "register", "evidence", "decision", "guide", "index"]; if (!kinds.includes(fields.Kind)) fail("document.kind", "document kind is invalid", 4, { path: relative });
  const statuses = fields.Kind === "decision" ? ["Proposed", "Accepted", "Rejected", "Superseded"] : ["Draft", "Active", "Superseded", "Retired"];
  if (!statuses.includes(fields.Status)) fail("document.status", "document status is invalid", 4, { path: relative });
  if (!validDate(fields.Updated)) fail("record.date", "updated date is invalid", 4, { path: relative });
  const decisionNeedsDate = fields.Kind === "decision" && ["Accepted", "Rejected", "Superseded"].includes(fields.Status);
  if (decisionNeedsDate && !fields["Decision-Date"]) fail("decision.date-required", "decision date is required", 4, { path: relative });
  if (!decisionNeedsDate && fields["Decision-Date"]) fail("decision.date-forbidden", "decision date is forbidden", 4, { path: relative });
  if (fields["Decision-Date"] && !validDate(fields["Decision-Date"])) fail("record.date", "decision date is invalid", 4, { path: relative });
  const parseIds = (name) => fields[name] ? fields[name].split(", ").map(item => { idOrdinal(item, DOC_ID, "record.document-id", relative); return item; }) : [];
  const supersedes = parseIds("Supersedes"), supersededBy = parseIds("Superseded-By");
  for (const items of [supersedes, supersededBy]) if (new Set(items).size !== items.length || items.some((item,index)=>index && idOrdinal(items[index-1],DOC_ID,"record.document-id",relative)>idOrdinal(item,DOC_ID,"record.document-id",relative))) fail("supersession.order", "supersession IDs must be unique and ordered", 4, { path: relative });
  if (fields.Status === "Superseded" && !supersededBy.length) fail("document.status", "superseded document requires successor", 4, { path: relative });
  let cursor = metadata.end + 1; const relationships = [];
  if (lines[cursor] === "" && lines[cursor + 1] === "<!-- wayfinder:relationships -->") {
    cursor += 2; const parsed = parseFieldBlock(lines, cursor, "<!-- /wayfinder:relationships -->", relative, "relationship"); cursor = parsed.end + 1;
    for (const [relation, value] of parsed.values) { if (!["Governed-By", "Supported-By"].includes(relation)) fail("relationship.field", "relationship kind is invalid", 4, { path: relative }); relationships.push({ relation, ...parseLink(value, "relationship.link", relative) }); }
    const keys = relationships.map(item => `${item.relation}:${item.id}`); if (new Set(keys).size !== keys.length) fail("relationship.duplicate-edge", "relationship edge is duplicated", 4, { path: relative });
    const sorted = [...relationships].sort((a,b)=>["Governed-By","Supported-By"].indexOf(a.relation)-["Governed-By","Supported-By"].indexOf(b.relation)||idOrdinal(a.id,DOC_ID,"record.document-id",relative)-idOrdinal(b.id,DOC_ID,"record.document-id",relative));
    if (canonicalJson(relationships)!==canonicalJson(sorted)) fail("relationship.order","relationships are out of order",4,{path:relative});
  }
  if (lines[cursor] !== "") fail("metadata.location", "metadata must be followed by one blank line", 4, { path: relative }); cursor += 1;
  const body = lines.slice(cursor).join("\n"); const h2 = body.split("\n").filter(line=>/^## /.test(line)).map(line=>line.slice(3));
  const profiles = { decision:["Context","Options considered","Decision","Rationale","Consequences","References","Supersession"], evidence:["Question and scope","Method","Findings","Applicability and limitations","Evidence, inference, and hypothesis","Implications","Unknowns","Next validation","Sources"] };
  if (profiles[fields.Kind] && canonicalJson(h2)!==canonicalJson(profiles[fields.Kind])) fail(`${fields.Kind}.sections`, `${fields.Kind} sections differ`, 4, { path: relative });
  const questions=[]; const questionRegex=/<!-- wayfinder:question -->\n([\s\S]*?)\n<!-- \/wayfinder:question -->/g; for(const match of body.matchAll(questionRegex))questions.push(parseQuestionBlock(match[1],relative));
  if (fields.Kind !== "register" && questions.length) fail("question.owner-kind", "questions require a register", 4, { path: relative });
  const sources=[]; const sourceRegex=/<!-- wayfinder:source -->\n([\s\S]*?)\n<!-- \/wayfinder:source -->/g; for(const match of body.matchAll(sourceRegex))sources.push(parseSourceBlock(match[1],relative));
  if (fields.Kind !== "evidence" && sources.length) fail("source.owner-kind", "sources require evidence", 4, { path: relative });
  const sourceKeys=sources.map(item=>item.key); if(new Set(sourceKeys).size!==sourceKeys.length)fail("source.duplicate-key","source keys must be unique",4,{path:relative});
  const citations=[...body.matchAll(/\[(src-[0-9]{2,})\]\(#\1\)/g)].map(m=>m[1]); for(const key of citations)if(!sourceKeys.includes(key))fail("source.citation-missing","citation target is missing",4,{path:relative,actual:key});
  for(const line of body.split("\n").filter(line=>line.startsWith("- **Material claim:**")))if(!/\[src-[0-9]{2,}\]\(#src-[0-9]{2,}\)/.test(line))fail("source.material-claim","material claim requires a citation",4,{path:relative});
  const warnings=sources.filter(source=>!citations.includes(source.key)).map(source=>({code:"source.unused",message:"source is not cited",path:relative,actual:source.key}));
  const generated=[...body.matchAll(/<!-- wayfinder:generated name="([a-z0-9]+(?:-[a-z0-9]+)*)" generator="([^"]+)" input-sha256="([0-9a-f]{64})" -->\n([\s\S]*?)<!-- \/wayfinder:generated -->/g)].map(match=>({name:match[1],generator:match[2],inputSha256:match[3],content:match[4].endsWith("\n")?match[4].slice(0,-1):match[4],start:match.index,end:match.index+match[0].length}));
  if (body.includes("<!-- wayfinder:generated") && !generated.length) fail("generated.marker", "generated marker is invalid", 4, { path: relative });
  if (generated.length && !["map","index"].includes(fields.Kind)) fail("generated.owner-kind", "generated region owner kind is invalid", 4, { path: relative });
  if(new Set(generated.map(item=>item.name)).size!==generated.length)fail("generated.duplicate-name","generated names must be unique",4,{path:relative});
  if(generated.some(item=>item.generator!=="document-index-v1"))fail("generated.marker","generated generator is invalid",4,{path:relative});
  return { path:relative,title:title[1],id:fields.ID,ordinal,kind:fields.Kind,status:fields.Status,updated:fields.Updated,summary:fields.Summary,decisionDate:fields["Decision-Date"]??null,supersedes,supersededBy,relationships,questions,sources,warnings,generated,text };
}

function membership(manifest, relative) {
  if (!relative.includes("/")) return { module:null, subject:null };
  const modules=manifest.modules.filter(item=>within(relative,item.root)); if(modules.length!==1)fail("record.module-containment","nested authored document must belong to exactly one module",4,{path:relative});
  const module=modules[0]; let subject=null;
  for(const item of module.subjects){ if(item.kind==="document"&&keyText(item.entrypoint)===keyText(relative))subject=`${module.id}/${item.id}`; else if(item.kind==="collection"&&within(relative,item.root))subject=`${module.id}/${item.id}`; }
  return {module:module.id,subject};
}

function enumerateAuthored(recordRoot, manifest) {
  const artifactKeys=new Set(manifest.generatedArtifacts.map(item=>keyText(item.path))); const documents=[];
  function walk(directory, prefix="") { for(const name of fs.readdirSync(directory).sort(utf8Compare)){ const target=path.join(directory,name); const relative=prefix?`${prefix}/${name}`:name; const kind=lstatKind(target); if(kind==="symlink")fail("path.symlink","record contains symbolic path",4,{path:relative}); if(kind==="directory")walk(target,relative); else if(kind==="regular-file"&&relative.toLowerCase().endsWith(".md")&&!artifactKeys.has(keyText(relative)))documents.push(parseDocument(readAuthored(target,relative),relative,path.dirname(recordRoot))); } }
  walk(recordRoot); return documents;
}

function recordModel(workspace,{checkGenerated=true,checkLocalSources=true}={}) {
  const manifestPath=manifestAt(workspace); if(!manifestPath)fail("discover.manifest-not-found","workspace has no manifest",3,{path:workspace}); const manifest=loadLiveManifest(workspace,manifestPath); const recordRoot=manifest.recordRoot==="."?workspace:path.join(workspace,...manifest.recordRoot.split("/"));
  const documents=enumerateAuthored(recordRoot,manifest); const byId=new Map(),byPath=new Map(),ordinals=new Set(); const questions=[]; const qIds=new Set(),qOrdinals=new Set(); const warnings=[];
  for(const doc of documents){if(byId.has(doc.id))fail("record.duplicate-document-id","document ID is duplicated",4,{path:doc.path});if(ordinals.has(doc.ordinal))fail("record.duplicate-document-ordinal","document ordinal is duplicated",4,{path:doc.path});byId.set(doc.id,doc);byPath.set(keyText(doc.path),doc);ordinals.add(doc.ordinal);Object.assign(doc,membership(manifest,doc.path));warnings.push(...doc.warnings);for(const q of doc.questions){if(qIds.has(q.id)||qOrdinals.has(q.ordinal))fail("record.duplicate-question-id","question ID or ordinal is duplicated",4,{path:doc.path});qIds.add(q.id);qOrdinals.add(q.ordinal);q.path=doc.path;questions.push(q);}}
  const entry=byPath.get(keyText(manifest.entrypoint)); if(!entry||entry.kind!=="map")fail("record.entrypoint-kind","record entrypoint must be a map",4,{path:manifest.entrypoint});
  for(const doc of documents){for(const relation of doc.relationships){const target=byId.get(relation.id);const resolved=byPath.get(keyText(normalizeLink(doc.path,relation.destination)));if(!target||target!==resolved)fail("relationship.target","relationship ID and path do not bind",4,{path:doc.path});if(relation.relation==="Governed-By"&&!(target.kind==="decision"&&target.status==="Accepted"))fail("relationship.target-kind-status","governance target must be an accepted decision",4,{path:doc.path});if(relation.relation==="Supported-By"&&!(target.kind==="evidence"&&target.status==="Active"))fail("relationship.target-kind-status","support target must be active evidence",4,{path:doc.path});}
    for(const [kind,ids] of [["supersedes",doc.supersedes],["supersededBy",doc.supersededBy]])for(const id of ids){if(id===doc.id)fail("supersession.self-edge","document may not supersede itself",4,{path:doc.path});const target=byId.get(id);if(!target)fail("supersession.target-missing","supersession target is missing",4,{path:doc.path});if((doc.kind==="decision")!==(target.kind==="decision"))fail("supersession.kind","supersession families differ",4,{path:doc.path});const inverse=kind==="supersedes"?target.supersededBy:target.supersedes;if(!inverse.includes(doc.id))fail("supersession.reciprocal","supersession edge is not reciprocal",4,{path:doc.path});}}
  const visiting=new Set(),visited=new Set();function visit(doc){if(visiting.has(doc.id))fail("supersession.cycle","supersession graph contains a cycle",4,{path:doc.path});if(visited.has(doc.id))return;visiting.add(doc.id);for(const id of doc.supersedes)visit(byId.get(id));visiting.delete(doc.id);visited.add(doc.id);}documents.forEach(visit);
  for(const q of questions){for(const link of [...q.applies,...q.addressed,...q.resolved]){const target=byId.get(link.id),resolved=byPath.get(keyText(normalizeLink(q.path,link.destination)));if(!target||target!==resolved)fail("question.target","question link does not bind",4,{path:q.path});}for(const link of q.addressed){const target=byId.get(link.id);if(target.kind!=="evidence")fail("question.target-kind","Addressed-By must target evidence",4,{path:q.path});}for(const link of q.resolved){const target=byId.get(link.id);if(!((target.kind==="decision"&&target.status==="Accepted")||(["evidence","brief"].includes(target.kind)&&target.status==="Active")))fail("question.target-kind-status","Resolved-By target is invalid",4,{path:q.path});}}
  if(checkLocalSources)for(const doc of documents)for(const source of doc.sources)if(!source.original.startsWith("https://")){const relative=sourcePath(source.original,"source.Original",4);inspectContained(workspace,relative,{requireKind:"regular-file",exitClass:4});}
  const model={manifest,recordRoot,documents,questions,warnings};
  if(checkGenerated)verifyGenerated(model); return model;
}

function catalogProjection(model){
  const documents=[...model.documents].sort((a,b)=>a.ordinal-b.ordinal).map(doc=>({id:doc.id,path:doc.path,title:doc.title,kind:doc.kind,status:doc.status,updated:doc.updated,summary:doc.summary,module:doc.module,subject:doc.subject,supersedes:doc.supersedes,supersededBy:doc.supersededBy,governedBy:doc.relationships.filter(x=>x.relation==="Governed-By").map(x=>x.id),supportedBy:doc.relationships.filter(x=>x.relation==="Supported-By").map(x=>x.id)}));
  const questions=[...model.questions].sort((a,b)=>a.ordinal-b.ordinal).map(q=>({id:q.id,path:q.path,anchor:q.id,title:q.title,state:q.state,raised:q.raised,appliesTo:q.applies.map(x=>x.id),addressedBy:q.addressed.map(x=>x.id),resolvedBy:q.resolved.map(x=>x.id),resumption:q.resumption}));
  const inputSha256=sha256(Buffer.from(canonicalJson({manifest:model.manifest,documents,questions}))); return {format:"wayfinder-document-catalog",schemaVersion:1,generator:"document-catalog-v1",inputSha256,documents,questions};
}
function catalogBytes(model){return Buffer.from(`${JSON.stringify(catalogProjection(model),null,2)}\n`);}
function regionMembers(model,owner){if(owner.path===model.manifest.entrypoint)return model.manifest.modules.map(item=>model.documents.find(doc=>keyText(doc.path)===keyText(item.entrypoint))).filter(Boolean);const module=model.manifest.modules.find(item=>keyText(item.entrypoint)===keyText(owner.path));if(module)return model.documents.filter(doc=>doc.module===module.id&&doc.id!==owner.id);for(const item of model.manifest.modules)for(const subject of item.subjects)if(subject.kind==="collection"&&keyText(subject.entrypoint)===keyText(owner.path))return model.documents.filter(doc=>doc.subject===`${item.id}/${subject.id}`&&doc.id!==owner.id);return [];}
function regionBlock(model,owner,region){const members=regionMembers(model,owner).sort((a,b)=>a.ordinal-b.ordinal);const rows=members.map(doc=>({id:doc.id,path:path.posix.relative(path.posix.dirname(owner.path),doc.path)||path.posix.basename(doc.path),title:doc.title,kind:doc.kind,status:doc.status,summary:doc.summary}));const digest=sha256(Buffer.from(canonicalJson(rows)));const body=[`<!-- wayfinder:generated name="${region.name}" generator="document-index-v1" input-sha256="${digest}" -->`,`| ID | Title | Kind | Status | Summary |`,`| --- | --- | --- | --- | --- |`,...rows.map(row=>`| [${row.id}](${row.path}) | ${row.title} | ${row.kind} | ${row.status} | ${row.summary} |`),"<!-- /wayfinder:generated -->"].join("\n");return body;}
function replaceRegions(model,doc){let text=doc.text;for(const region of [...doc.generated].sort((a,b)=>b.start-a.start)){const block=regionBlock(model,doc,region);const full=/<!-- wayfinder:generated name="[^"]+" generator="[^"]+" input-sha256="[0-9a-f]{64}" -->\n[\s\S]*?<!-- \/wayfinder:generated -->/g;let count=0;text=text.replace(full,match=>{const name=/name="([^"]+)"/.exec(match)[1];if(name===region.name&&count++===0)return block;return match;});}return Buffer.from(text);}
function verifyGenerated(model){for(const doc of model.documents){if(doc.text.includes("<!-- wayfinder:generated")&&doc.generated.length===0)fail("generated.marker","generated marker is invalid",4,{path:doc.path});for(const region of doc.generated){if(region.content.includes("<!-- wayfinder:generated"))fail("generated.nested","generated regions may not nest",4,{path:doc.path});const expected=regionBlock(model,doc,region);const actual=doc.text.slice(doc.text.indexOf(`<!-- wayfinder:generated name="${region.name}"`),doc.text.indexOf("<!-- /wayfinder:generated -->",doc.text.indexOf(`<!-- wayfinder:generated name="${region.name}"`))+"<!-- /wayfinder:generated -->".length);if(actual!==expected)fail("generated.stale","generated region is stale",4,{path:doc.path});}}
  for(const artifact of model.manifest.generatedArtifacts){const target=path.join(model.recordRoot,...artifact.path.split("/"));if(!fs.readFileSync(target).equals(catalogBytes(model)))fail("generated.catalog-stale","generated catalog is stale",4,{path:artifact.path});}}

function commandValidate(options){const workspace=physicalDirectory(options["workspace-root"],"--workspace-root");const model=recordModel(workspace);return {documents:model.documents.length,questions:model.questions.length,warnings:model.warnings};}

function requireString(value, field, { nullable=false }={}) { if(nullable&&value===null)return null;if(typeof value!=="string"||!value)fail("json.type","expected nonempty string",2,{field});return value; }
function validateRenderDocument(value,index){
  const field=`/documents/${index}`,doc=objectValue(value,field,2);const names=["output","title","id","kind","status","updated","summary","decisionDate","supersedes","supersededBy","relationships","sections","questions","sources"];closed(doc,names,field,2);
  portablePath(doc.output,`${field}/output`,{exitClass:2});for(const name of ["title","id","kind","status","updated","summary"])requireString(doc[name],`${field}/${name}`);idOrdinal(doc.id,DOC_ID,"record.document-id",doc.output);if(!["map","brief","register","evidence","decision","guide","index"].includes(doc.kind))fail("document.kind","document kind is invalid",2,{field:`${field}/kind`});
  const status=doc.kind==="decision"?["Proposed","Accepted","Rejected","Superseded"]:["Draft","Active","Superseded","Retired"];if(!status.includes(doc.status))fail("document.status","document status is invalid",2,{field:`${field}/status`});if(!validDate(doc.updated))fail("record.date","date is invalid",2,{field:`${field}/updated`});if(doc.decisionDate!==null&&!validDate(doc.decisionDate))fail("record.date","decision date is invalid",2,{field:`${field}/decisionDate`});
  const needs=doc.kind==="decision"&&doc.status!=="Proposed";if(needs&&doc.decisionDate===null)fail("decision.date-required","decision date is required",2,{field});if(!needs&&doc.decisionDate!==null)fail("decision.date-forbidden","decision date is forbidden",2,{field});
  for(const name of ["supersedes","supersededBy"]){const items=arrayValue(doc[name],`${field}/${name}`,2);items.forEach((id,i)=>{if(typeof id!=="string"||!DOC_ID.test(id))fail("record.document-id","document ID is invalid",2,{field:`${field}/${name}/${i}`});});}
  const relationships=arrayValue(doc.relationships,`${field}/relationships`,2);relationships.forEach((item,i)=>{const f=`${field}/relationships/${i}`,x=objectValue(item,f,2);closed(x,["relation","targetId","targetPath"],f,2);if(!["Governed-By","Supported-By"].includes(x.relation)||!DOC_ID.test(x.targetId))fail("relationship.link","relationship is invalid",2,{field:f});requireString(x.targetPath,`${f}/targetPath`);normalizeLink(doc.output,x.targetPath);});
  const sections=arrayValue(doc.sections,`${field}/sections`,2);sections.forEach((item,i)=>{const f=`${field}/sections/${i}`,x=objectValue(item,f,2);closed(x,["heading","content"],f,2);requireString(x.heading,`${f}/heading`);requireString(x.content,`${f}/content`);});
  const questions=arrayValue(doc.questions,`${field}/questions`,2);questions.forEach((q,i)=>validateQuestionSpec(q,`${field}/questions/${i}`));
  const sources=arrayValue(doc.sources,`${field}/sources`,2);sources.forEach((s,i)=>validateSourceSpec(s,`${field}/sources/${i}`));return doc;
}
function validateQuestionSpec(q,field){q=objectValue(q,field,2);const names=["id","title","state","raised","scope","appliesTo","addressedBy","resolvedBy","resolutionDate","sections"];closed(q,names,field,2);if(!QUESTION_ID.test(q.id))fail("record.question-id","question ID invalid",2,{field:`${field}/id`});requireString(q.title,`${field}/title`);if(!["Open","Investigating","Deferred","Resolved","Retired"].includes(q.state)||!validDate(q.raised))fail("question.state","question state or date invalid",2,{field});if(q.scope!==null&&q.scope!=="Record-Wide")fail("question.scope","question scope invalid",2,{field:`${field}/scope`});for(const name of ["appliesTo","addressedBy","resolvedBy"]){arrayValue(q[name],`${field}/${name}`,2).forEach((x,i)=>{x=objectValue(x,`${field}/${name}/${i}`,2);closed(x,["targetId","targetPath"],`${field}/${name}/${i}`,2);if(!DOC_ID.test(x.targetId))fail("record.document-id","target ID invalid",2,{field:`${field}/${name}/${i}/targetId`});requireString(x.targetPath,`${field}/${name}/${i}/targetPath`);});}if(q.resolutionDate!==null&&!validDate(q.resolutionDate))fail("record.date","resolution date invalid",2,{field:`${field}/resolutionDate`});arrayValue(q.sections,`${field}/sections`,2).forEach((x,i)=>{x=objectValue(x,`${field}/sections/${i}`,2);closed(x,["heading","content"],`${field}/sections/${i}`,2);requireString(x.heading,`${field}/sections/${i}/heading`);requireString(x.content,`${field}/sections/${i}/content`);});}
function validateSourceSpec(s,field){s=objectValue(s,field,2);const names=["key","title","citation","original","published","accessed","applicability","usedFor","limitations"];closed(s,names,field,2);for(const name of ["key","title","citation","original","accessed","usedFor","limitations"])if(typeof s[name]!=="string"||!s[name])fail("render.source","source field invalid",2,{field:`${field}/${name}`});if(!SOURCE_ID.test(s.key))fail("render.source","source key invalid",2,{field:`${field}/key`});if(s.published!==null&&!validDate(s.published)||!validDate(s.accessed)||!["Direct","Adjacent","General"].includes(s.applicability))fail("render.source","source field invalid",2,{field});}
function metadataText(doc){const lines=["<!-- wayfinder:metadata -->",`- **ID:** ${doc.id}`,`- **Kind:** ${doc.kind}`,`- **Status:** ${doc.status}`,`- **Updated:** ${doc.updated}`,`- **Summary:** ${doc.summary}`];if(doc.decisionDate!==null)lines.push(`- **Decision-Date:** ${doc.decisionDate}`);if(doc.supersedes.length)lines.push(`- **Supersedes:** ${doc.supersedes.join(", ")}`);if(doc.supersededBy.length)lines.push(`- **Superseded-By:** ${doc.supersededBy.join(", ")}`);lines.push("<!-- /wayfinder:metadata -->");return lines.join("\n");}
function relationshipText(doc){if(!doc.relationships.length)return "";const values=["<!-- wayfinder:relationships -->",...doc.relationships.map(x=>`- **${x.relation}:** [${x.targetId}](${x.targetPath})`),"<!-- /wayfinder:relationships -->",""];return `${values.join("\n")}\n`;}
function questionText(q){const lines=["<!-- wayfinder:question -->",`<a id="${q.id}"></a>`,`### ${q.title}`,`- **ID:** ${q.id}`,`- **State:** ${q.state}`,`- **Raised:** ${q.raised}`];if(q.scope!==null)lines.push(`- **Scope:** ${q.scope}`);for(const x of q.appliesTo)lines.push(`- **Applies-To:** [${x.targetId}](${x.targetPath})`);for(const x of q.addressedBy)lines.push(`- **Addressed-By:** [${x.targetId}](${x.targetPath})`);for(const x of q.resolvedBy)lines.push(`- **Resolved-By:** [${x.targetId}](${x.targetPath})`);if(q.resolutionDate!==null)lines.push(`- **Resolution-Date:** ${q.resolutionDate}`);lines.push("");for(const section of q.sections)lines.push(`#### ${section.heading}`,"",section.content,"");if(lines.at(-1)==="")lines.pop();lines.push("<!-- /wayfinder:question -->");return lines.join("\n");}
function sourceText(s){const lines=["<!-- wayfinder:source -->",`<a id="${s.key}"></a>`,`### ${s.key} — ${s.title}`,`- **Citation:** ${s.citation}`,`- **Original:** ${s.original}`];if(s.published!==null)lines.push(`- **Published:** ${s.published}`);lines.push(`- **Accessed:** ${s.accessed}`,`- **Applicability:** ${s.applicability}`,"","#### Used for","",s.usedFor,"","#### Limitations","",s.limitations,"<!-- /wayfinder:source -->");return lines.join("\n");}
function contentText(doc){const parts=[];for(const section of doc.sections)parts.push(`## ${section.heading}\n\n${section.content}`);for(const q of doc.questions)parts.push(questionText(q));for(const s of doc.sources)parts.push(sourceText(s));return parts.join("\n\n");}
function renderDocument(pkgRoot,doc){const relative=`assets/contract-v1/templates/${doc.kind}.md`;const raw=fs.readFileSync(path.join(pkgRoot,...relative.split("/")));let template=new TextDecoder("utf-8",{fatal:true}).decode(raw);const slots=[...template.matchAll(/\{\{([A-Z_]+)\}\}/g)].map(m=>m[1]);const expected=["TITLE","METADATA_BLOCK","RELATIONSHIP_BLOCK","CONTENT"];if(slots.length!==4||new Set(slots).size!==4||expected.some(slot=>!slots.includes(slot)))fail("template.slots","template slots differ",2,{path:relative,expected,actual:slots});for(const value of [doc.title,metadataText(doc),relationshipText(doc),contentText(doc)])if(/\{\{[A-Z_]+\}\}/.test(value))fail("template.recursive-slot","render value contains reserved slot",2,{path:doc.output});const values={TITLE:doc.title,METADATA_BLOCK:metadataText(doc),RELATIONSHIP_BLOCK:relationshipText(doc),CONTENT:contentText(doc)};template=template.replace(/\{\{([A-Z_]+)\}\}/g,(_,name)=>values[name]);return Buffer.from(template);}
function validateGenerationRequest(value){const request=objectValue(value,"/",2);if(request.format!=="wayfinder-generation-request")fail("generate.format","generation request format invalid",2,{field:"/format"});if(request.schemaVersion!==1)fail("generate.unsupported-version","generation request version invalid",2,{field:"/schemaVersion"});if(!["allocate","render","catalog","regions"].includes(request.action))fail("generate.action","generation action invalid",2,{field:"/action"});const fields={allocate:["format","schemaVersion","action","documents","questions"],render:["format","schemaVersion","action","documents"],catalog:["format","schemaVersion","action"],regions:["format","schemaVersion","action","paths"]}[request.action];closed(request,fields,"/",2);return request;}
function atomicReplace(target,raw){const temp=path.join(path.dirname(target),`.${path.basename(target)}.${process.pid}.${crypto.randomBytes(8).toString("hex")}.tmp`);fs.writeFileSync(temp,raw,{flag:"wx"});fs.renameSync(temp,target);}
function commandGenerate(options){const workspace=physicalDirectory(options["workspace-root"],"--workspace-root");const [,value]=strictInputFile(options.request,"--request",2);const request=validateGenerationRequest(value);
  if(request.action==="render"){
    if(options["output-root"]===undefined)fail("command.option","--output-root is required for render",2,{field:"--output-root"});const output=physicalDirectory(options["output-root"],"--output-root");const docs=request.documents.map(validateRenderDocument);const paths=docs.map(doc=>keyText(doc.output));if(new Set(paths).size!==paths.length)fail("render.duplicate-output","render outputs must be unique",2,{field:"/documents"});const pkgRoot=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../..");const rendered=docs.map(doc=>({doc,raw:renderDocument(pkgRoot,doc)}));for(const {doc,raw} of rendered){const target=path.join(output,...doc.output.split("/"));let current=output;for(const segment of doc.output.split("/").slice(0,-1)){current=path.join(current,segment);if(lstatKind(current)==="symlink")fail("path.symlink","output path contains symbolic component",3,{path:doc.output});}if(lstatKind(target)!=="missing")fail("generate.output-exists","render target exists",3,{path:doc.output});parseDocument(new TextDecoder().decode(raw),doc.output,workspace);}for(const {doc,raw} of rendered){const target=path.join(output,...doc.output.split("/"));fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,raw,{flag:"wx"});}return {written:docs.map(doc=>doc.output)};
  }
  if(options["output-root"]!==undefined)fail("command.option","--output-root is accepted only for render",2,{field:"--output-root"});const model=recordModel(workspace,{checkGenerated:false});
  if(request.action==="allocate"){const allocate=(items,prefix,start)=>arrayValue(items,`/${prefix}`,2).map((item,index)=>{item=objectValue(item,`/${prefix}/${index}`,2);closed(item,["title","mnemonic"],`/${prefix}/${index}`,2);requireString(item.title,`/${prefix}/${index}/title`);let mnemonic=item.mnemonic;if(mnemonic===null){mnemonic=(item.title.match(/[A-Za-z0-9]+/g)??[]).map(x=>x.toLowerCase()).join("-").slice(0,48).replace(/-+$/g,"");if(!mnemonic)fail("allocation.mnemonic-required","explicit mnemonic is required",2,{field:`/${prefix}/${index}/mnemonic`});}else if(typeof mnemonic!=="string"||!SLUG.test(mnemonic)||mnemonic.length>48)fail("allocation.mnemonic","mnemonic is invalid",2,{field:`/${prefix}/${index}/mnemonic`});return {id:`${prefix==="documents"?"wf":"wfq"}-${String(start+index).padStart(4,"0")}-${mnemonic}`,candidate:true};});const maxDoc=Math.max(0,...model.documents.map(x=>x.ordinal)),maxQ=Math.max(0,...model.questions.map(x=>x.ordinal));return {documents:allocate(request.documents,"documents",maxDoc+1),questions:allocate(request.questions,"questions",maxQ+1)};}
  if(request.action==="catalog"){const written=[];for(const artifact of model.manifest.generatedArtifacts){const target=path.join(model.recordRoot,...artifact.path.split("/"));atomicReplace(target,catalogBytes(model));written.push(artifact.path);}return {written};}
  const paths=arrayValue(request.paths,"/paths",2).map((x,i)=>portablePath(x,`/paths/${i}`,{exitClass:2}));if(new Set(paths.map(keyText)).size!==paths.length)fail("generate.region-path","region paths must be unique",2,{field:"/paths"});const docs=[];for(const relative of paths){const doc=model.documents.find(x=>keyText(x.path)===keyText(relative));if(!doc||!doc.generated.length)fail("generate.region-path","path is not a declared generated-region owner",2,{path:relative});docs.push(doc);}for(const doc of docs)atomicReplace(path.join(model.recordRoot,...doc.path.split("/")),replaceRegions(model,doc));return {written:paths};
}

function proposalArray(value,field,validator){const items=arrayValue(value,field,2);items.forEach((item,index)=>validator(item,`${field}/${index}`));return items;}
function closedStringsObject(value,fields,field){value=objectValue(value,field,2);closed(value,fields,field,2);for(const name of fields)requireString(value[name],`${field}/${name}`);return value;}
function validateInitializeProposal(value){
  const p=objectValue(value,"/",2),fields=["format","schemaVersion","mode","profile","effectiveDate","manifest","documents","concerns","epistemicStates","omittedModules","authorityBoundary","interviewResume","materialInferences","sourceInventory","intakeLedger","materialSourcePaths","semanticReadiness"];closed(p,fields,"/",2);literal(p.format,"wayfinder-initialize-proposal","/format","proposal.format",2);literal(p.schemaVersion,1,"/schemaVersion","proposal.unsupported-version",2);if(!["fresh","source-assisted"].includes(p.mode))fail("proposal.mode","proposal mode invalid",2,{field:"/mode"});if(!validDate(p.effectiveDate))fail("record.date","effective date invalid",2,{field:"/effectiveDate"});
  const profile=objectValue(p.profile,"/profile",2);closed(profile,["id","confirmed"],"/profile",2);if(!["foundation","evidence-led","software-product"].includes(profile.id)||profile.confirmed!==true)fail("proposal.profile","profile must be registered and confirmed",2,{field:"/profile"});
  try{validateManifest(p.manifest,"/virtual",{live:false});}catch(error){if(error instanceof WFError&&error.code==="path.traversal")fail("path.traversal",error.message,2,error.details);if(error instanceof WFError&&error.code==="manifest.artifact-entrypoint-conflict")fail("initialize.target-collision","planned targets collide",2,error.details);throw error;}const docs=arrayValue(p.documents,"/documents",2).map(validateRenderDocument);if(!docs.length)fail("proposal.documents","proposal requires documents",2,{field:"/documents"});
  const ids=new Set(),ordinals=[];const questions=[];for(const doc of docs){if(ids.has(doc.id))fail("proposal.document-id-collision","proposal document IDs collide",2,{field:"/documents"});ids.add(doc.id);ordinals.push(Number(DOC_ID.exec(doc.id)[1]));questions.push(...doc.questions);}if(ordinals.some((n,i)=>n!==i+1))fail("proposal.document-id-order","proposal document ordinals must be consecutive",2,{actual:ordinals});const qOrd=questions.map(q=>Number(QUESTION_ID.exec(q.id)[1]));if(qOrd.some((n,i)=>n!==i+1))fail("proposal.question-id-order","proposal question ordinals must be consecutive",2,{actual:qOrd});
  const allIds=new Set([...ids,...questions.map(q=>q.id)]),concernIds=new Set();proposalArray(p.concerns,"/concerns",(item,field)=>{item=closedStringsObject(item,["id","statement","homeId"],field);if(concernIds.has(item.id))fail("proposal.concern-id","concern IDs must be unique",2,{field:`${field}/id`});concernIds.add(item.id);if(!allIds.has(item.homeId))fail("proposal.concern-home","concern home does not exist",2,{field:`${field}/homeId`});});if(!p.concerns.length)fail("proposal.concern-home","at least one concern is required",2);
  proposalArray(p.epistemicStates,"/epistemicStates",(item,field)=>{item=objectValue(item,field,2);closed(item,["state","statement","targetId"],field,2);if(!["Hypothesis","Assumption","Open question","Deferred","Not applicable","Not yet elicited"].includes(item.state)||typeof item.statement!=="string"||!item.statement||!allIds.has(item.targetId))fail("proposal.epistemic","epistemic declaration invalid",2,{field});});
  const omissions=new Set();proposalArray(p.omittedModules,"/omittedModules",(item,field)=>{item=closedStringsObject(item,["id","reason"],field);if(!STANDARD_MODULES.includes(item.id)||omissions.has(item.id))fail("proposal.omitted-module-completeness","module omission invalid",2,{field});omissions.add(item.id);});const enabled=new Set(p.manifest.modules.map(x=>x.id));for(const id of STANDARD_MODULES)if(id!=="decisions"&&!enabled.has(id)&&!omissions.has(id))fail("proposal.omitted-module-completeness","every disabled standard module needs a reason",2,{actual:id});
  const authority=objectValue(p.authorityBoundary,"/authorityBoundary",2);closed(authority,["statement","coauthoritativePaths","competingCurrentAuthority"],"/authorityBoundary",2);requireString(authority.statement,"/authorityBoundary/statement");proposalArray(authority.coauthoritativePaths,"/authorityBoundary/coauthoritativePaths",(x,f)=>sourcePath(x,f));const competing=arrayValue(authority.competingCurrentAuthority,"/authorityBoundary/competingCurrentAuthority",2);if(competing.some(x=>typeof x!=="string"||!x))fail("json.type","competing authority entries invalid",2);if(competing.length)fail("proposal.competing-authority","competing current authority blocks planning",3,{actual:competing});
  const resume=objectValue(p.interviewResume,"/interviewResume",2);closed(resume,["summary","nextWorkflow","recommendedFocusIds"],"/interviewResume",2);requireString(resume.summary,"/interviewResume/summary");literal(resume.nextWorkflow,"interview","/interviewResume/nextWorkflow","proposal.interview-resume",2);const focus=uniqueStrings(resume.recommendedFocusIds,"/interviewResume/recommendedFocusIds",null,"proposal.interview-resume");if(!focus.length||focus.some(id=>!allIds.has(id)))fail("proposal.interview-resume","interview focus must exist",2);
  proposalArray(p.materialInferences,"/materialInferences",(item,field)=>{item=objectValue(item,field,2);closed(item,["statement","basis","confirmed"],field,2);requireString(item.statement,`${field}/statement`);requireString(item.basis,`${field}/basis`);if(item.confirmed!==true)fail("proposal.inference-unconfirmed","material inference is not confirmed",3,{field});});
  const binding=(item,field)=>{item=objectValue(item,field,2);closed(item,["path","sha256"],field,2);sourcePath(item.path,`${field}/path`);if(typeof item.sha256!=="string"||!HEX.test(item.sha256))fail("json.type","binding digest invalid",2,{field:`${field}/sha256`});return item;};if(p.sourceInventory!==null)binding(p.sourceInventory,"/sourceInventory");if(p.intakeLedger!==null)binding(p.intakeLedger,"/intakeLedger");if(p.mode==="fresh"&&(p.sourceInventory!==null||p.intakeLedger!==null||p.materialSourcePaths.length))fail("proposal.source-binding","fresh proposal forbids source bindings",2);if(p.mode==="source-assisted"&&(p.sourceInventory===null||p.intakeLedger===null))fail("proposal.source-binding","source-assisted proposal requires bindings",2);
  proposalArray(p.materialSourcePaths,"/materialSourcePaths",(x,f)=>sourcePath(x,f));if(new Set(p.materialSourcePaths).size!==p.materialSourcePaths.length)fail("proposal.source-binding","material source paths must be unique",2);
  const readiness=objectValue(p.semanticReadiness,"/semanticReadiness",2),readinessFields=["identityAndIntent","outcomes","boundaries","people","currentKnowledge","consequentialUnknowns","structure","publicationBasis"];closed(readiness,readinessFields,"/semanticReadiness",2);for(const name of readinessFields)if(!["supported","explicit-unresolved"].includes(readiness[name]))fail("json.type","readiness state invalid",2,{field:`/semanticReadiness/${name}`});if(Object.values(readiness).includes("explicit-unresolved")&&!questions.length)fail("proposal.semantic-readiness","unresolved readiness requires a durable question",3);
  const placeholder=/^(?:TBD|TODO|unknown|placeholder)$/i;for(const doc of docs)for(const section of doc.sections)if(placeholder.test(section.content.trim()))fail("proposal.placeholder","placeholder content is forbidden",2,{path:doc.output});const map=docs.find(doc=>doc.output===p.manifest.entrypoint);if(!map||map.kind!=="map"||!map.sections.some(x=>x.heading==="Authority boundary"))fail("proposal.knowledge-map","knowledge map is incomplete",3,{path:p.manifest.entrypoint});
  for(const module of p.manifest.modules.filter(x=>x.id.startsWith("local-"))){const owner=docs.find(doc=>keyText(doc.output)===keyText(module.entrypoint));const required=["Purpose","Authority boundary","Audience","Relationship to standard modules"];if(!owner||required.some(name=>!owner.sections.some(x=>x.heading===name)))fail("proposal.local-module-boundary","local module boundary is incomplete",3,{actual:module.id});}
  return p;
}
function resolveBaseline(workspace,baseline){if(baseline.kind==="snapshot"){const target=path.join(workspace,...baseline.path.split("/"));if(lstatKind(target)!=="regular-file"||sha256(fs.readFileSync(target))!==baseline.sha256)fail("initialize.baseline-unresolved","snapshot baseline cannot be verified",3,{path:baseline.path});return {kind:"snapshot",path:baseline.path,sha256:baseline.sha256};}const parts=baseline.ref.slice(5).split("/");let target=path.join(workspace,".git","refs",...parts);let commit=null;if(lstatKind(target)==="regular-file")commit=fs.readFileSync(target,"ascii").trim();else{const packed=path.join(workspace,".git","packed-refs");if(lstatKind(packed)==="regular-file")for(const line of fs.readFileSync(packed,"ascii").split("\n")){const [hash,ref]=line.split(" ");if(ref===baseline.ref)commit=hash;}}if(!/^(?:[0-9a-f]{40}|[0-9a-f]{64})$/.test(commit??""))fail("initialize.baseline-unresolved","git baseline cannot be resolved locally",3,{actual:baseline.ref});return {kind:"git-ref",ref:baseline.ref,commit};}
function virtualPayloads(manifest,documents){const temporary=fs.realpathSync.native(fs.mkdtempSync(path.join(os.tmpdir(),"wayfinder-node-plan-")));try{fs.mkdirSync(path.join(temporary,".wayfinder"),{recursive:true});fs.writeFileSync(path.join(temporary,".wayfinder","manifest.json"),`${JSON.stringify(manifest,null,2)}\n`);const root=manifest.recordRoot==="."?temporary:path.join(temporary,...manifest.recordRoot.split("/"));fs.mkdirSync(root,{recursive:true});for(const module of manifest.modules)fs.mkdirSync(path.join(root,...module.root.split("/")),{recursive:true});for(const doc of documents){const target=path.join(root,...doc.output.split("/"));fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,renderDocument(path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../.."),doc));}for(const artifact of manifest.generatedArtifacts){const target=path.join(root,...artifact.path.split("/"));fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,"{}\n");}if(manifest.canonicalBaseline.kind==="snapshot"){const target=path.join(temporary,...manifest.canonicalBaseline.path.split("/"));fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,"{}\n");}
    let model=recordModel(temporary,{checkGenerated:false,checkLocalSources:false});for(const doc of model.documents.filter(x=>x.generated.length))fs.writeFileSync(path.join(root,...doc.path.split("/")),replaceRegions(model,doc));model=recordModel(temporary,{checkGenerated:false,checkLocalSources:false});const catalog=catalogBytes(model);for(const artifact of manifest.generatedArtifacts)fs.writeFileSync(path.join(root,...artifact.path.split("/")),catalog);model=recordModel(temporary,{checkLocalSources:false});const bytes=new Map();for(const doc of model.documents)bytes.set(doc.path,fs.readFileSync(path.join(root,...doc.path.split("/"))));for(const artifact of manifest.generatedArtifacts)bytes.set(artifact.path,fs.readFileSync(path.join(root,...artifact.path.split("/"))));return {model,bytes,catalog};}finally{fs.rmSync(temporary,{recursive:true,force:true});}}
function previewBytes(plan,planDigest,operationId,payloadBytes){const lines=["# Wayfinder initialization review","",`- **Plan digest:** \`sha256:${planDigest}\``,`- **Operation ID:** \`${operationId}\``,`- **Mode:** \`${plan.mode}\``,`- **Profile:** \`${plan.review.profile.id}\` (confirmed)`,`- **Workspace:** \`${plan.workspace.workspaceRoot}\``,`- **Record root:** \`${plan.manifest.recordRoot}\``,"","## Exact target tree",""];for(const target of plan.review.targetTree)lines.push(`- \`${target}\``);lines.push("","## Concern-to-home map","");for(const item of plan.review.concernHomes)lines.push(`- \`${item.id}\` → \`${item.homeId}\` — ${item.statement}`);lines.push("","## Explicit unresolved and epistemic states","");if(plan.review.epistemicStates.length)for(const item of plan.review.epistemicStates)lines.push(`- **${item.state}:** ${item.statement} (\`${item.targetId}\`)`);else lines.push("- None declared.");lines.push("","## Omitted standard modules","");if(plan.review.omittedModules.length)for(const item of plan.review.omittedModules)lines.push(`- \`${item.id}\` — ${item.reason}`);else lines.push("- None.");lines.push("","## Authority boundary","",plan.review.authorityBoundary.statement,"","## Material agent inferences","");if(plan.review.materialInferences.length)for(const item of plan.review.materialInferences)lines.push(`- ${item.statement} — ${item.basis}`);else lines.push("- None declared.");lines.push("","## Preconditions","");for(const target of plan.preconditions.targetsAbsent)lines.push(`- \`${target}\` is absent.`);lines.push("","## Ordered future operation","");plan.operations.forEach((item,index)=>lines.push(`${index+1}. \`${item.action}\` \`${item.path}\``));lines.push("","## Exact authored document payloads","");for(const item of plan.payloads.filter(x=>x.role==="authored-document")){lines.push(`### \`${item.targetPath}\` — \`${item.documentId}\``,"","```markdown",new TextDecoder().decode(payloadBytes.get(item.bundlePath)).replace(/\n$/,""),"```","");}lines.push("## Interview resumption","",plan.review.interviewResume.summary,"",`Recommended focus: ${plan.review.interviewResume.recommendedFocusIds.map(x=>`\`${x}\``).join(", ")}`,"");return Buffer.from(lines.join("\n"));}
function commandInitializePlan(options){if(process.env.WAYFINDER_TEST_MODE==="1"&&process.env.WAYFINDER_TEST_RAISE==="1")throw new Error("injected");const workspace=physicalDirectory(options["workspace-root"],"--workspace-root");const [proposalRaw,proposalValue]=strictInputFile(options.proposal,"--proposal",2);const proposal=validateInitializeProposal(proposalValue);const bundle=options["bundle-root"];if(typeof bundle!=="string"||!bundle)fail("command.option","--bundle-root is required",2,{field:"--bundle-root"});const bundleAbs=path.resolve(bundle);let parent=path.dirname(bundleAbs);if(lstatKind(bundleAbs)!=="missing")fail(lstatKind(bundleAbs)==="symlink"?"initialize.bundle-symlink":"initialize.bundle-exists","bundle already exists",3,{path:bundle});while(lstatKind(parent)==="missing")parent=path.dirname(parent);if(lstatKind(parent)==="symlink")fail("initialize.bundle-symlink","bundle parent path is symbolic",3,{path:bundle});const physicalBundle=path.join(fs.realpathSync.native(parent),path.relative(parent,bundleAbs));if(physicalBundle===workspace||physicalBundle.startsWith(`${workspace}${path.sep}`))fail("initialize.bundle-location","bundle must be outside workspace",2,{path:bundle});
  const manifestTarget=path.join(workspace,".wayfinder","manifest.json");if(lstatKind(manifestTarget)!=="missing")fail("initialize.manifest-exists","manifest already exists",3,{path:manifestTarget});const operationsRoot=path.join(workspace,".wayfinder","operations");if(lstatKind(operationsRoot)==="directory"&&fs.readdirSync(operationsRoot).length)fail("initialize.recovery-required","prior operation state requires recovery",5,{path:operationsRoot});const recordRoot=proposal.manifest.recordRoot==="."?workspace:path.join(workspace,...proposal.manifest.recordRoot.split("/"));const targetRel=proposal.documents.map(x=>proposal.manifest.recordRoot==="."?x.output:`${proposal.manifest.recordRoot}/${x.output}`);for(const artifact of proposal.manifest.generatedArtifacts)targetRel.push(proposal.manifest.recordRoot==="."?artifact.path:`${proposal.manifest.recordRoot}/${artifact.path}`);if(new Set([...targetRel.map(keyText),keyText(".wayfinder/manifest.json")]).size!==targetRel.length+1)fail("initialize.target-collision","planned targets collide",2);for(const relative of targetRel){const target=path.join(workspace,...relative.split("/"));let current=workspace;for(const segment of relative.split("/")){current=path.join(current,segment);if(lstatKind(current)==="symlink")fail("path.symlink","target contains symbolic link",3,{path:relative});}if(lstatKind(target)!=="missing")fail("initialize.target-exists","planned target exists",3,{path:relative});}for(const module of proposal.manifest.modules){const relative=proposal.manifest.recordRoot==="."?module.root:`${proposal.manifest.recordRoot}/${module.root}`,target=path.join(workspace,...relative.split("/"));if(lstatKind(target)!=="missing")fail("initialize.module-root-exists","module root exists",3,{path:relative});}
  const baseline=resolveBaseline(workspace,proposal.manifest.canonicalBaseline);let sourceBindings={inventory:null,intake:null,materialSourcePaths:[...proposal.materialSourcePaths]},inventoryAttachment=null,intakeAttachment=null;
  if(proposal.mode==="source-assisted"){const [invRaw,inv]=strictInputFile(path.join(workspace,...proposal.sourceInventory.path.split("/")),proposal.sourceInventory.path,2);const invCanonical=canonicalJson(inv),invDigest=sha256(Buffer.from(invCanonical));if(invDigest!==proposal.sourceInventory.sha256)fail("initialize.inventory-digest","inventory binding digest differs",3,{expected:proposal.sourceInventory.sha256,actual:invDigest});const rebuilt=buildInventory(workspace,validateInventoryRequest({format:"wayfinder-source-inventory-request",schemaVersion:1,selections:inv.selections.map(x=>x.path),targetRoots:inv.targetRoots,limits:inv.limits}));if(canonicalJson(rebuilt)!==canonicalJson(inv))fail("initialize.inventory-stale","source inventory is stale",3);const [ledgerRaw,ledger]=strictInputFile(path.join(workspace,...proposal.intakeLedger.path.split("/")),proposal.intakeLedger.path,2);const ledgerDigest=sha256(Buffer.from(canonicalJson(ledger)));if(ledgerDigest!==proposal.intakeLedger.sha256)fail("initialize.intake-digest","intake binding digest differs",3,{expected:proposal.intakeLedger.sha256,actual:ledgerDigest});validateIntake(ledger,inv,invDigest,workspace);const ledgerPaths=new Set(ledger.sources.map(x=>x.path));if(proposal.materialSourcePaths.some(x=>!ledgerPaths.has(x)))fail("initialize.material-source-disposition","material source lacks disposition",3);inventoryAttachment=Buffer.from(`${JSON.stringify(inv,null,2)}\n`);intakeAttachment=Buffer.from(`${JSON.stringify(ledger,null,2)}\n`);sourceBindings={inventory:{path:proposal.sourceInventory.path,sha256:invDigest,bundlePath:"inventory.json"},intake:{path:proposal.intakeLedger.path,sha256:ledgerDigest,bundlePath:"intake.json"},materialSourcePaths:[...proposal.materialSourcePaths]};}
  const virtual=virtualPayloads(proposal.manifest,proposal.documents);const pkg=verifyPackage();const payloads=[],payloadBytes=new Map();let ordinal=1;for(const doc of proposal.documents){const raw=virtual.bytes.get(doc.output),bundlePath=`payload/${String(ordinal++).padStart(4,"0")}`,targetPath=proposal.manifest.recordRoot==="."?doc.output:`${proposal.manifest.recordRoot}/${doc.output}`,templatePath=`assets/contract-v1/templates/${doc.kind}.md`;payloadBytes.set(bundlePath,raw);payloads.push({bundlePath,targetPath,role:"authored-document",documentId:doc.id,byteLength:raw.length,sha256:sha256(raw),producer:{id:`template-${doc.kind}-v1`,sha256:sha256(fs.readFileSync(path.join(pkg.skillRoot,...templatePath.split("/"))))}});}for(const artifact of proposal.manifest.generatedArtifacts){const raw=virtual.bytes.get(artifact.path),bundlePath=`payload/${String(ordinal++).padStart(4,"0")}`,targetPath=proposal.manifest.recordRoot==="."?artifact.path:`${proposal.manifest.recordRoot}/${artifact.path}`;payloadBytes.set(bundlePath,raw);payloads.push({bundlePath,targetPath,role:"generated-artifact",documentId:null,byteLength:raw.length,sha256:sha256(raw),producer:{id:artifact.generator,sha256:pkg.contractDigest}});}const manifestRaw=Buffer.from(`${JSON.stringify(proposal.manifest,null,2)}\n`),manifestBundle=`payload/${String(ordinal++).padStart(4,"0")}`;payloadBytes.set(manifestBundle,manifestRaw);payloads.push({bundlePath:manifestBundle,targetPath:".wayfinder/manifest.json",role:"manifest",documentId:null,byteLength:manifestRaw.length,sha256:sha256(manifestRaw),producer:{id:"manifest-schema-v1",sha256:sha256(fs.readFileSync(path.join(pkg.skillRoot,"assets/contract-v1/schemas/manifest.schema.json")))}});
  const directories=new Set([".wayfinder",...(proposal.manifest.recordRoot==="."?[]:[proposal.manifest.recordRoot])]);for(const item of payloads.filter(x=>x.targetPath!==".wayfinder/manifest.json")){let current=path.posix.dirname(item.targetPath);while(current!=="."&&current!==""){directories.add(current);current=path.posix.dirname(current);}}const dirOrder=[...directories].sort((a,b)=>a.split("/").length-b.split("/").length||utf8Compare(a,b));const operations=[...dirOrder.map(value=>({action:"create-directory",path:value})),...payloads.filter(x=>x.role!=="manifest").map(x=>({action:"create-file",path:x.targetPath,payload:x.bundlePath,sha256:x.sha256})),{action:"publish-manifest",path:".wayfinder/manifest.json",payload:manifestBundle,sha256:sha256(manifestRaw)}];const targetTree=payloads.map(x=>x.targetPath).sort(utf8Compare);const targetsAbsent=[".wayfinder/manifest.json",...proposal.documents.map(x=>proposal.manifest.recordRoot==="."?x.output:`${proposal.manifest.recordRoot}/${x.output}`),...proposal.manifest.generatedArtifacts.map(x=>proposal.manifest.recordRoot==="."?x.path:`${proposal.manifest.recordRoot}/${x.path}`)];const normativeDigest=sha256(fs.readFileSync(path.join(pkg.skillRoot,"references/contracts/v1.md")));for(const item of payloads)if(item.role==="generated-artifact")item.producer.sha256=normativeDigest;const plan={format:"wayfinder-initialize-plan",schemaVersion:1,contractVersion:1,contractSha256:pkg.contractDigest,proposalSha256:sha256(Buffer.from(canonicalJson(proposal))),mode:proposal.mode,effectiveDate:proposal.effectiveDate,workspace:{workspaceRoot:workspace,recordRoot},manifest:proposal.manifest,sourceBindings,preconditions:{manifestAbsent:true,targetsAbsent,moduleRootsAbsent:proposal.manifest.modules.map(x=>proposal.manifest.recordRoot==="."?x.root:`${proposal.manifest.recordRoot}/${x.root}`),bundleAbsent:true,canonicalBaseline:baseline},review:{profile:proposal.profile,concernHomes:proposal.concerns,epistemicStates:proposal.epistemicStates,omittedModules:proposal.omittedModules,authorityBoundary:proposal.authorityBoundary,materialInferences:proposal.materialInferences,interviewResume:proposal.interviewResume,semanticReadiness:proposal.semanticReadiness,targetTree},validation:{documents:virtual.model.documents.length,questions:virtual.model.questions.length,warnings:virtual.model.warnings,catalogSha256:sha256(virtual.catalog)},payloads,operations};const planRaw=Buffer.from(canonicalJson(plan)),planDigest=sha256(planRaw);let operationId=`wfinit-${planDigest.slice(0,24)}`;if(process.env.WAYFINDER_TEST_MODE==="1"&&process.env.WAYFINDER_TEST_OPERATION_ID!==undefined){if(!/^wfinit-test-[a-z0-9]+(?:-[a-z0-9]+)*$/.test(process.env.WAYFINDER_TEST_OPERATION_ID))fail("initialize.operation-id","test operation ID invalid",2);operationId=process.env.WAYFINDER_TEST_OPERATION_ID;}const preview=previewBytes(plan,planDigest,operationId,payloadBytes);fs.mkdirSync(bundleAbs,{recursive:false});try{fs.mkdirSync(path.join(bundleAbs,"payload"));for(const [relative,raw] of payloadBytes)fs.writeFileSync(path.join(bundleAbs,...relative.split("/")),raw,{flag:"wx"});if(inventoryAttachment)fs.writeFileSync(path.join(bundleAbs,"inventory.json"),inventoryAttachment,{flag:"wx"});if(intakeAttachment)fs.writeFileSync(path.join(bundleAbs,"intake.json"),intakeAttachment,{flag:"wx"});fs.writeFileSync(path.join(bundleAbs,"plan.json"),planRaw,{flag:"wx"});fs.writeFileSync(path.join(bundleAbs,"preview.md"),preview,{flag:"wx"});}catch(error){fs.rmSync(bundleAbs,{recursive:true,force:true});throw error;}return {planSha256:planDigest,operationId,bundleRoot:bundleAbs,payloads:payloads.length};}

const PLAN_FIELDS=["format","schemaVersion","contractVersion","contractSha256","proposalSha256","mode","effectiveDate","workspace","manifest","sourceBindings","preconditions","review","validation","payloads","operations"];
function validatePlan(value){const plan=objectValue(value,"/",2);closed(plan,PLAN_FIELDS,"/",2);literal(plan.format,"wayfinder-initialize-plan","/format","apply.plan-format",2);literal(plan.schemaVersion,1,"/schemaVersion","apply.plan-version",2);literal(plan.contractVersion,1,"/contractVersion","apply.plan-version",2);for(const name of ["contractSha256","proposalSha256"])if(typeof plan[name]!=="string"||!HEX.test(plan[name]))fail("json.type","plan digest field invalid",2,{field:`/${name}`});if(!["fresh","source-assisted"].includes(plan.mode)||!validDate(plan.effectiveDate))fail("json.type","plan mode or date invalid",2);const ws=objectValue(plan.workspace,"/workspace",2);closed(ws,["workspaceRoot","recordRoot"],"/workspace",2);requireString(ws.workspaceRoot,"/workspace/workspaceRoot");requireString(ws.recordRoot,"/workspace/recordRoot");validateManifest(plan.manifest,"/virtual",{live:false});arrayValue(plan.payloads,"/payloads",2);arrayValue(plan.operations,"/operations",2);return plan;}
function listTreeFiles(root){const values=[];function walk(current,prefix=""){for(const name of fs.readdirSync(current).sort(utf8Compare)){const target=path.join(current,name),relative=prefix?`${prefix}/${name}`:name,kind=lstatKind(target);if(kind==="symlink")fail("initialize.bundle-members","bundle contains a symbolic link",3,{path:relative});if(kind==="directory")walk(target,relative);else if(kind==="regular-file")values.push(relative);else fail("initialize.bundle-members","bundle contains unsupported file",3,{path:relative});}}walk(root);return values;}
function verifyBundle(bundle,plan){const expected=new Set(["plan.json","preview.md",...plan.payloads.map(x=>x.bundlePath)]);if(plan.mode==="source-assisted"){expected.add("inventory.json");expected.add("intake.json");}const actual=listTreeFiles(bundle);if(actual.length!==expected.size||actual.some(x=>!expected.has(x)))fail("initialize.bundle-members","bundle membership differs from plan",3,{expected:[...expected].sort(utf8Compare),actual});for(const item of plan.payloads){const target=path.join(bundle,...item.bundlePath.split("/"));if(lstatKind(target)!=="regular-file")fail("initialize.bundle-members","payload is missing",3,{path:item.bundlePath});const raw=fs.readFileSync(target);if(raw.length!==item.byteLength||sha256(raw)!==item.sha256)fail("apply.payload-digest","payload digest differs",3,{path:item.bundlePath});}return true;}
function verifyApplyPreconditions(workspace,plan,{afterState=false}={}){if(plan.workspace.workspaceRoot!==workspace||plan.workspace.recordRoot!==(plan.manifest.recordRoot==="."?workspace:path.join(workspace,...plan.manifest.recordRoot.split("/"))))fail("apply.workspace-binding","plan belongs to another workspace",3);const baseline=resolveBaseline(workspace,plan.manifest.canonicalBaseline);if(canonicalJson(baseline)!==canonicalJson(plan.preconditions.canonicalBaseline))fail("apply.baseline-stale","canonical baseline changed",3);if(!afterState){if(lstatKind(path.join(workspace,".wayfinder","manifest.json"))!=="missing")fail("apply.manifest-exists","manifest appeared",3);for(const item of plan.payloads.filter(x=>x.role!=="manifest"))if(lstatKind(path.join(workspace,...item.targetPath.split("/")))!=="missing")fail("apply.target-exists","planned target appeared",3,{path:item.targetPath});}if(plan.mode==="source-assisted"){const inv=JSON.parse(fs.readFileSync(path.join(workspace,...plan.sourceBindings.inventory.path.split("/")),"utf8"));const rebuilt=buildInventory(workspace,validateInventoryRequest({format:"wayfinder-source-inventory-request",schemaVersion:1,selections:inv.selections.map(x=>x.path),targetRoots:inv.targetRoots,limits:inv.limits}));if(canonicalJson(rebuilt)!==canonicalJson(inv))fail("apply.inventory-stale","source inventory is stale",3);}return baseline;}
function controlledTimestamp(){if(process.env.WAYFINDER_TEST_MODE==="1"&&process.env.WAYFINDER_TEST_CLOCK)return process.env.WAYFINDER_TEST_CLOCK;return new Date(Math.floor(Date.now()/1000)*1000).toISOString().replace(".000Z","Z");}
function inject(boundary){if(process.env.WAYFINDER_TEST_MODE==="1"&&process.env.WAYFINDER_TEST_FAILURE_BOUNDARY===boundary)fail("initialize.interrupted","maintainer failure boundary reached",5,{actual:boundary});}
function appendEvent(state,type,data={}){const basis={format:"wayfinder-initialization-event",schemaVersion:1,operationId:state.operationId,sequence:state.events.length+1,timestamp:controlledTimestamp(),type,previousEventSha256:state.events.at(-1)?.eventSha256??null,data};const event={...basis,eventSha256:sha256(Buffer.from(canonicalJson(basis)))};fs.appendFileSync(state.journal,`${canonicalJson(event)}\n`);state.events.push(event);return event;}
function readJournal(operationRoot,operationId){const journal=path.join(operationRoot,"events.jsonl");let raw;try{raw=fs.readFileSync(journal);}catch{return {valid:false,reason:"missing"};}if(!raw.length||raw[raw.length-1]!==0x0a)return{valid:false,reason:"truncated"};const events=[];let previous=null;try{for(const [index,line] of raw.toString("utf8").trimEnd().split("\n").entries()){const value=strictJsonBytes(Buffer.from(line),"events.jsonl",{exitClass:5});const fields=["format","schemaVersion","operationId","sequence","timestamp","type","previousEventSha256","data","eventSha256"];closed(value,fields,"/",5);const basis={format:value.format,schemaVersion:value.schemaVersion,operationId:value.operationId,sequence:value.sequence,timestamp:value.timestamp,type:value.type,previousEventSha256:value.previousEventSha256,data:value.data};if(value.format!=="wayfinder-initialization-event"||value.schemaVersion!==1||value.operationId!==operationId||value.sequence!==index+1||value.previousEventSha256!==previous||sha256(Buffer.from(canonicalJson(basis)))!==value.eventSha256||line!==canonicalJson(value))return{valid:false,reason:"chain"};events.push(value);previous=value.eventSha256;}}catch{return{valid:false,reason:"parse"};}if(events[0]?.type!=="operation-recorded")return{valid:false,reason:"first"};let stage=false,publishing=false,started=new Set(),staged=0;const targets=events[0].data.targets??[];for(const event of events){if(event.type==="staging-started")stage=true;if(event.type==="payload-staged"){if(!stage||event.data.path!==targets[staged]?.path)return{valid:false,reason:"order"};staged+=1;}if(event.type==="publication-started")publishing=true;if(event.type==="file-create-started"){if(!publishing||started.has(event.data.path))return{valid:false,reason:"order"};started.add(event.data.path);}if(event.type==="file-created"&&!started.has(event.data.path))return{valid:false,reason:"order"};}return{valid:true,events,journal};}
function writeExclusive(target,raw){fs.mkdirSync(path.dirname(target),{recursive:true});const fd=fs.openSync(target,"wx",0o600);try{fs.writeFileSync(fd,raw);fs.fsyncSync(fd);}finally{fs.closeSync(fd);}if(!fs.readFileSync(target).equals(raw))throw new Error("write verification failed");}
function importBundle(source,destination){fs.mkdirSync(destination,{recursive:true,mode:0o700});for(const relative of listTreeFiles(source)){const target=path.join(destination,...relative.split("/"));fs.mkdirSync(path.dirname(target),{recursive:true,mode:0o700});writeExclusive(target,fs.readFileSync(path.join(source,...relative.split("/"))));}}
function loadLock(lockPath){try{const raw=fs.readFileSync(lockPath);const value=strictJsonBytes(raw,"initialize.lock",{exitClass:5});closed(value,["format","schemaVersion","operationId","planSha256","owner"],"/",5);const owner=objectValue(value.owner,"/owner",5);closed(owner,["host","pid","token"],"/owner",5);return value;}catch{return null;}}
function processAlive(pid){if(!Number.isInteger(pid)||pid<1)return true;try{process.kill(pid,0);return true;}catch(error){return error.code!=="ESRCH";}}
function receiptFor(state,plan,baseline,journalHead){let counts={incorporate:0,reference:0,"preserve-out-of-scope":0,unresolved:0};if(plan.mode==="source-assisted"){const ledger=JSON.parse(fs.readFileSync(path.join(state.bundle,"intake.json"),"utf8"));for(const item of ledger.sources)counts[item.disposition]+=1;}const manifest=plan.payloads.find(x=>x.role==="manifest");return{format:"wayfinder-initialization-receipt",schemaVersion:1,operationId:state.operationId,completedAt:controlledTimestamp(),mode:plan.mode,planSha256:state.planSha256,contractVersion:1,contractSha256:plan.contractSha256,adapter:{id:ADAPTER_ID,sha256:verifyPackage().adapterDigest},canonicalBaseline:baseline,manifestSha256:manifest.sha256,targetSetSha256:sha256(Buffer.from(canonicalJson(plan.payloads.map(x=>({path:x.targetPath,sha256:x.sha256}))))),intake:{ledgerDigest:plan.sourceBindings.intake?.sha256??null,incorporate:counts.incorporate,reference:counts.reference,preserveOutOfScope:counts["preserve-out-of-scope"],unresolved:counts.unresolved},validation:{validatorVersion:1,errors:0,warnings:plan.validation.warnings.length,resultSha256:sha256(Buffer.from(canonicalJson(plan.validation)))},operationalIntegrity:{status:"passed",targetCount:plan.payloads.length,manifestPublishedLast:true},semanticReadiness:{status:"passed",predicates:plan.review.semanticReadiness,authorityConfirmed:true},entrypoint:path.join(plan.workspace.recordRoot,...plan.manifest.entrypoint.split("/")),openQuestionIds:plan.review.interviewResume.recommendedFocusIds.filter(x=>x.startsWith("wfq-")),nextWorkflow:"interview",recommendedFocusIds:plan.review.interviewResume.recommendedFocusIds,journalHeadSha256:journalHead};}
function completionData(state,plan,receipt,head){const manifest=plan.payloads.find(x=>x.role==="manifest");return{status:"completed",operationId:state.operationId,planSha256:state.planSha256,manifest:{path:manifest.targetPath,sha256:manifest.sha256},receipt:{path:`.wayfinder/operations/${state.operationId}/receipt.json`,sha256:sha256(Buffer.from(canonicalJson(receipt)))},journalHeadSha256:head,validation:plan.validation,handoff:{nextWorkflow:"interview",recommendedFocusIds:plan.review.interviewResume.recommendedFocusIds}};}
function continueApply(state,plan,baseline){if(!state.events.some(x=>x.type==="staging-started")){appendEvent(state,"staging-started",{});inject("after-staging-started");}const staging=path.join(state.operationRoot,"staging");fs.mkdirSync(staging,{recursive:true,mode:0o700});for(const [index,item] of plan.payloads.entries()){if(!state.events.some(x=>x.type==="payload-staged"&&x.data.path===item.targetPath)){const raw=fs.readFileSync(path.join(state.bundle,...item.bundlePath.split("/")));const target=path.join(staging,...item.bundlePath.split("/"));fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,raw);appendEvent(state,"payload-staged",{path:item.targetPath,sha256:item.sha256});inject(`after-stage-${String(index+1).padStart(4,"0")}`);}}if(!state.events.some(x=>x.type==="staging-complete")){appendEvent(state,"staging-complete",{});inject("after-staging-complete");}if(!state.events.some(x=>x.type==="preconditions-rechecked")){verifyApplyPreconditions(state.workspace,plan);appendEvent(state,"preconditions-rechecked",{});inject("after-preconditions-rechecked");}if(!state.events.some(x=>x.type==="publication-started")){appendEvent(state,"publication-started",{});inject("after-publication-started");}
  const dirOps=plan.operations.filter(x=>x.action==="create-directory");for(const [index,op] of dirOps.entries()){const target=path.join(state.workspace,...op.path.split("/"));if(op.path===".wayfinder"&&lstatKind(target)==="directory")continue;if(!state.events.some(x=>x.type==="directory-created"&&x.data.path===op.path)){if(lstatKind(target)==="missing")fs.mkdirSync(target);else if(lstatKind(target)!=="directory")fail("initialize.recovery-required","directory target is occupied",5,{path:op.path});appendEvent(state,"directory-created",{path:op.path});inject(`after-directory-${String(index+1).padStart(4,"0")}`);}}
  const fileOps=plan.operations.filter(x=>x.action==="create-file");for(const [index,op] of fileOps.entries()){const item=plan.payloads.find(x=>x.bundlePath===op.payload),target=path.join(state.workspace,...op.path.split("/")),raw=fs.readFileSync(path.join(state.bundle,...op.payload.split("/")));if(state.events.some(x=>x.type==="file-created"&&x.data.path===op.path)){if(lstatKind(target)!=="regular-file"||sha256(fs.readFileSync(target))!==op.sha256)fail("initialize.recovery-required","created file changed",5,{path:op.path});continue;}inject(`before-file-${String(index+1).padStart(4,"0")}`);if(!state.events.some(x=>x.type==="file-create-started"&&x.data.path===op.path))appendEvent(state,"file-create-started",{path:op.path,sha256:op.sha256});if(lstatKind(target)!=="missing")fail("initialize.recovery-required","target appeared during publication",5,{path:op.path});writeExclusive(target,raw);appendEvent(state,"file-created",{path:op.path,sha256:item.sha256});inject(`after-file-${String(index+1).padStart(4,"0")}`);}
  const manifestOp=plan.operations.at(-1),manifestTarget=path.join(state.workspace,".wayfinder","manifest.json"),manifestRaw=fs.readFileSync(path.join(state.bundle,...manifestOp.payload.split("/")));if(!state.events.some(x=>x.type==="manifest-published")){inject("before-manifest-publication");appendEvent(state,"manifest-publish-started",{path:manifestOp.path,sha256:manifestOp.sha256});if(lstatKind(manifestTarget)!=="missing")fail("initialize.recovery-required","manifest appeared during publication",5,{path:manifestOp.path});writeExclusive(manifestTarget,manifestRaw);appendEvent(state,"manifest-published",{path:manifestOp.path,sha256:manifestOp.sha256});inject("after-manifest-publication");}
  if(!state.events.some(x=>x.type==="live-validation-started")){appendEvent(state,"live-validation-started",{});inject("after-live-validation-started");}for(const item of plan.payloads){const target=path.join(state.workspace,...item.targetPath.split("/"));if(lstatKind(target)!=="regular-file"||sha256(fs.readFileSync(target))!==item.sha256)fail("initialize.recovery-required","live target validation failed",5,{path:item.targetPath});}recordModel(state.workspace);if(!state.events.some(x=>x.type==="live-validation-complete")){appendEvent(state,"live-validation-complete",{documents:plan.validation.documents,questions:plan.validation.questions});inject("after-live-validation-complete");}
  const receiptPath=path.join(state.operationRoot,"receipt.json");let receipt;if(!state.events.some(x=>x.type==="receipt-written")){receipt=receiptFor(state,plan,baseline,state.events.at(-1).eventSha256);const raw=Buffer.from(canonicalJson(receipt));writeExclusive(receiptPath,raw);appendEvent(state,"receipt-written",{sha256:sha256(raw)});inject("after-receipt-written");}else receipt=strictJsonBytes(fs.readFileSync(receiptPath),"receipt.json",{exitClass:5});if(!state.events.some(x=>x.type==="complete"))appendEvent(state,"complete",{receiptSha256:sha256(Buffer.from(canonicalJson(receipt)))});inject("after-complete");fs.rmSync(staging,{recursive:true,force:true});try{fs.unlinkSync(state.lockPath);}catch{}return completionData(state,plan,receipt,state.events.at(-1).eventSha256);}
function commandInitializeApply(options){if(process.env.WAYFINDER_TEST_MODE==="1"&&process.env.WAYFINDER_TEST_RAISE==="1")throw new Error("injected");const workspace=physicalDirectory(options["workspace-root"],"--workspace-root");const bundle=physicalDirectory(options["bundle-root"],"--bundle-root");if(typeof options["plan-sha256"]!=="string"||!HEX.test(options["plan-sha256"]))fail("apply.plan-digest","plan digest option invalid",3);if(options["confirmation-token"]!==`wayfinder-confirm-sha256:${options["plan-sha256"]}`)fail("apply.confirmation-token","confirmation token does not match plan option",2);const [planRaw,planValue]=strictInputFile(path.join(bundle,"plan.json"),"plan.json",2);if(sha256(planRaw)!==options["plan-sha256"])fail("apply.plan-digest","plan bytes do not match confirmed digest",3);if(canonicalJson(planValue)!==planRaw.toString("utf8"))fail("apply.plan-canonical","plan is not canonical",2);const plan=validatePlan(planValue),pkg=verifyPackage();if(plan.contractSha256!==pkg.contractDigest)fail("apply.contract-digest","plan contract differs from executing contract",3);verifyBundle(bundle,plan);const baseline=verifyApplyPreconditions(workspace,plan);const operationId=`wfinit-${options["plan-sha256"].slice(0,24)}`,control=path.join(workspace,".wayfinder"),lockPath=path.join(control,"initialize.lock");fs.mkdirSync(control,{recursive:true});if(lstatKind(lockPath)!=="missing")fail("lock.contention","initialize lock already exists",5,{path:lockPath});const lock={format:"wayfinder-initialization-lock",schemaVersion:1,operationId,planSha256:options["plan-sha256"],owner:{host:os.hostname(),pid:process.pid,token:crypto.randomBytes(24).toString("hex")}};writeExclusive(lockPath,Buffer.from(canonicalJson(lock)));inject("after-lock-acquired");const operationRoot=path.join(control,"operations",operationId),imported=path.join(operationRoot,"bundle");fs.mkdirSync(operationRoot,{recursive:true,mode:0o700});importBundle(bundle,imported);const state={workspace,bundle:imported,operationId,planSha256:options["plan-sha256"],operationRoot,lockPath,journal:path.join(operationRoot,"events.jsonl"),events:[]};appendEvent(state,"operation-recorded",{planSha256:state.planSha256,targets:plan.payloads.map(x=>({path:x.targetPath,sha256:x.sha256})),controlRootCreated:true});inject("after-bundle-imported");return continueApply(state,plan,baseline);}
function classifyOperation(workspace,operationId){const operationRoot=path.join(workspace,".wayfinder","operations",operationId),lockPath=path.join(workspace,".wayfinder","initialize.lock");if(lstatKind(operationRoot)!=="directory")return{status:lstatKind(lockPath)==="regular-file"?"blocked":"manual-recovery",operationRoot,lockPath};const journal=readJournal(operationRoot,operationId);if(!journal.valid)return{status:journal.reason==="missing"?"blocked":"manual-recovery",operationRoot,lockPath,journal,reason:journal.reason};let plan,planSha256,bundle=path.join(operationRoot,"bundle");try{const raw=fs.readFileSync(path.join(bundle,"plan.json"));planSha256=sha256(raw);plan=validatePlan(strictJsonBytes(raw,"plan.json",{exitClass:5}));verifyBundle(bundle,plan);}catch{return{status:"manual-recovery",operationRoot,lockPath,journal};}const created=new Map();for(const event of journal.events)if(["file-created","manifest-published"].includes(event.type))created.set(event.data.path,event.data.sha256);for(const event of journal.events)if(event.type==="path-removed")created.delete(event.data.path);for(const [relative,digest] of created){const target=path.join(workspace,...relative.split("/"));if(lstatKind(target)!=="regular-file"||sha256(fs.readFileSync(target))!==digest)return{status:"manual-recovery",operationRoot,lockPath,journal,plan,bundle,planSha256};}for(const item of plan.payloads)if(!created.has(item.targetPath)&&!journal.events.some(x=>x.type==="path-removed"&&x.data.path===item.targetPath)&&lstatKind(path.join(workspace,...item.targetPath.split("/")))!=="missing")return{status:"manual-recovery",operationRoot,lockPath,journal,plan,bundle,planSha256};const last=journal.events.at(-1);if(last.type==="complete"){const receipt=path.join(operationRoot,"receipt.json");if(lstatKind(receipt)!=="regular-file")return{status:"manual-recovery",operationRoot,lockPath,journal,plan,bundle,planSha256};try{const raw=fs.readFileSync(receipt),value=strictJsonBytes(raw,"receipt.json",{exitClass:5});const event=journal.events.find(x=>x.type==="receipt-written");if(raw.toString("utf8")!==canonicalJson(value)||!event||sha256(raw)!==event.data.sha256)return{status:"manual-recovery",operationRoot,lockPath,journal,plan,bundle,planSha256};return{status:"completed",operationRoot,lockPath,journal,plan,bundle,planSha256,receipt:value};}catch{return{status:"manual-recovery",operationRoot,lockPath,journal,plan,bundle,planSha256};}}if(last.type==="rollback-complete")return{status:"rolled-back",operationRoot,lockPath,journal,plan,bundle,planSha256};return{status:"resumable",recoveryAction:journal.events.some(x=>x.type==="rollback-started")?"rollback":"resume",operationRoot,lockPath,journal,plan,bundle,planSha256};}
function reclaimLock(info,operationId){if(lstatKind(info.lockPath)==="missing")return;const lock=loadLock(info.lockPath);if(!lock)fail("lock.manual-recovery","initialize lock is malformed",5,{path:info.lockPath});if(lock.operationId!==operationId||lock.planSha256!==info.planSha256||lock.owner.host!==os.hostname())fail("lock.contention","initialize lock belongs to another owner",5,{path:info.lockPath});if(processAlive(lock.owner.pid))fail("lock.contention","initialize lock owner is still live",5,{path:info.lockPath});fs.unlinkSync(info.lockPath);}
function rollbackOperation(workspace,operationId,info){if(info.status==="blocked"&&!info.journal?.valid){const lock=loadLock(info.lockPath);if(lock&&lock.operationId===operationId&&lock.owner.host===os.hostname()&&!processAlive(lock.owner.pid))fs.unlinkSync(info.lockPath);return{status:"rolled-back",operationId,recoveryAction:"rollback"};}if(!info.journal?.valid)return{status:"manual-recovery",operationId,recoveryAction:"manual"};reclaimLock(info,operationId);const state={workspace,bundle:info.bundle,operationId,planSha256:info.planSha256,operationRoot:info.operationRoot,lockPath:info.lockPath,journal:info.journal.journal,events:[...info.journal.events]};if(!state.events.some(x=>x.type==="rollback-started"))appendEvent(state,"rollback-started",{});inject("after-rollback-started");let removal=0,blocked=false;const created=[];for(const event of state.events)if(["file-created","manifest-published"].includes(event.type))created.push({path:event.data.path,sha256:event.data.sha256});for(const item of created.reverse()){if(state.events.some(x=>x.type==="path-removed"&&x.data.path===item.path))continue;const target=path.join(workspace,...item.path.split("/"));if(lstatKind(target)==="regular-file"&&sha256(fs.readFileSync(target))===item.sha256){fs.unlinkSync(target);appendEvent(state,"path-removed",{path:item.path,kind:"file"});removal+=1;inject(`after-rollback-file-${String(removal).padStart(4,"0")}`);}else if(lstatKind(target)!=="missing")blocked=true;}const dirs=info.plan.operations.filter(x=>x.action==="create-directory"&&x.path!==".wayfinder").map(x=>x.path).reverse();let dirCount=0;for(const relative of dirs){if(state.events.some(x=>x.type==="path-removed"&&x.data.path===relative))continue;const target=path.join(workspace,...relative.split("/"));if(lstatKind(target)==="directory"&&fs.readdirSync(target).length===0){fs.rmdirSync(target);appendEvent(state,"path-removed",{path:relative,kind:"directory"});dirCount+=1;inject(`after-rollback-directory-${String(dirCount).padStart(4,"0")}`);}else if(lstatKind(target)!=="missing")blocked=true;}if(blocked){appendEvent(state,"rollback-blocked",{});return{status:"manual-recovery",operationId,recoveryAction:"manual"};}appendEvent(state,"rollback-complete",{});try{fs.unlinkSync(info.lockPath);}catch{}return{status:"rolled-back",operationId,recoveryAction:"rollback"};}
function commandInitializeRecover(options){const workspace=physicalDirectory(options["workspace-root"],"--workspace-root");const operationId=options["operation-id"];if(typeof operationId!=="string"||!/^wfinit-(?:[0-9a-f]{24}|test-[a-z0-9]+(?:-[a-z0-9]+)*)$/.test(operationId))fail("recover.operation-id","operation ID is invalid",2);if(!["inspect","resume","rollback"].includes(options.action))fail("recover.action","recovery action invalid",2);const info=classifyOperation(workspace,operationId);if(options.action==="inspect")return{status:info.status,operationId,...(info.recoveryAction?{recoveryAction:info.recoveryAction}:{})};if(options.action==="rollback")return rollbackOperation(workspace,operationId,info);if(info.status==="completed")return completionData({operationId,planSha256:info.planSha256},info.plan,info.receipt,info.journal.events.at(-1).eventSha256);if(info.status!=="resumable"||info.recoveryAction!=="resume")fail("recover.manual-recovery","operation cannot resume automatically",5);reclaimLock(info,operationId);const lock={format:"wayfinder-initialization-lock",schemaVersion:1,operationId,planSha256:info.planSha256,owner:{host:os.hostname(),pid:process.pid,token:crypto.randomBytes(24).toString("hex")}};writeExclusive(info.lockPath,Buffer.from(canonicalJson(lock)));const state={workspace,bundle:info.bundle,operationId,planSha256:info.planSha256,operationRoot:info.operationRoot,lockPath:info.lockPath,journal:info.journal.journal,events:[...info.journal.events]};const baseline=verifyApplyPreconditions(workspace,info.plan,{afterState:true});const data=continueApply(state,info.plan,baseline);data.status="completed";return data;}

function resultEnvelope(ok, command, code, data, diagnostics) { return { format: "wayfinder-command-result", schemaVersion: 1, ok, command, code, data, diagnostics }; }
function emit(value) { process.stdout.write(`${JSON.stringify(value)}\n`); }

function parseCommand(argv) {
  if (!argv.length) fail("command.missing", "a command is required", 2);
  const command = argv[0]; if (!COMMANDS.includes(command)) fail("command.unknown", "command is not registered", 2, { actual: command });
  const allowed = {
    probe: [], discover: ["workspace-root", "start"], inventory: ["workspace-root", "request", "ledger"],
    "initialize-plan": ["workspace-root", "proposal", "bundle-root"], "initialize-apply": ["workspace-root", "bundle-root", "plan-sha256", "confirmation-token"],
    "initialize-recover": ["workspace-root", "operation-id", "action"], validate: ["workspace-root"], generate: ["workspace-root", "request", "output-root"],
  }[command];
  const options = {};
  for (let i = 1; i < argv.length; i += 2) {
    const token = argv[i]; if (!token?.startsWith("--") || i + 1 >= argv.length) fail("command.option", "options require --name value pairs", 2, { actual: token });
    const name = token.slice(2); if (!allowed.includes(name) || Object.hasOwn(options, name)) fail("command.option", "option is unknown or duplicated", 2, { actual: token }); options[name] = argv[i + 1];
  }
  if (command === "discover" && options["workspace-root"] !== undefined && options.start !== undefined) fail("command.option", "discover accepts either workspace root or start", 2);
  return { command, options };
}

function main(argv) {
  let command = COMMANDS.includes(argv[0]) ? argv[0] : "unknown";
  try {
    const parsed = parseCommand(argv); command = parsed.command;
    if (process.env.WAYFINDER_TEST_MODE === "1" && process.env.WAYFINDER_TEST_RAISE === "1") throw new Error("injected");
    let data;
    if (command === "probe") data = commandProbe();
    else if (command === "discover") data = commandDiscover(parsed.options);
    else if (command === "inventory") data = commandInventory(parsed.options);
    else if (command === "validate") data = commandValidate(parsed.options);
    else if (command === "generate") data = commandGenerate(parsed.options);
    else if (command === "initialize-plan") data = commandInitializePlan(parsed.options);
    else if (command === "initialize-apply") data = commandInitializeApply(parsed.options);
    else if (command === "initialize-recover") data = commandInitializeRecover(parsed.options);
    else fail("command.unimplemented", "command implementation is incomplete", 70);
    emit(resultEnvelope(true, command, "ok", data, [])); return 0;
  } catch (error) {
    const issue = error instanceof WFError ? error : new WFError("internal.unexpected", "unexpected internal failure", 70, { actual: String(error?.message ?? error) });
    process.stderr.write(`${command}: ${issue.code}: ${issue.message}\n`); emit(resultEnvelope(false, command, issue.code, {}, [issue.diagnostic()])); return issue.exitClass;
  }
}

process.exitCode = main(process.argv.slice(2));
