# Wayfinder public repository and cross-client plugin structure

- **Status:** Accepted repository-migration design; implementation in progress
- **Last updated:** 2026-09-14
- **Audience:** Wayfinder owner and maintainers
- **Research question:** How should Wayfinder and Wayfinder Maintainer move into a public GitHub repository that supports Codex, Claude, and GitHub Copilot, while preserving the frozen version-1 candidate, enabling the remaining certification matrix in GitHub Actions, and avoiding divergent copies of the skills?
- **Current candidate:** `v1-candidate-revision-8`, frozen semantic contract, unactivated release
- **Scope:** Repository topology, plugin packaging, cross-client compatibility, CI and evidence architecture, public-repository governance, and a safe migration sequence
- **Out of scope of the research itself:** Changing governed semantics or adapter bytes, completing certification, submitting a public directory listing, or activating Wayfinder. The repository migration was subsequently authorized on 2026-09-14.

## Executive conclusion

Use **one public marketplace/source repository containing two separately installable plugin packages**:

1. `wayfinder`, the end-user runtime plugin; and
2. `wayfinder-maintainer`, an opt-in contributor/maintainer plugin.

Make the root `plugin.json` inside each package the canonical packaging manifest and target the published **Agent Plugins 1.0** specification. Keep each skill's files in the portable fixed location `skills/<skill-name>/`. Add a small `.claude-plugin/plugin.json` compatibility projection inside each package because Claude's current plugin documentation still uses that manifest. Do not create Codex-, Claude-, and Copilot-specific copies of either skill.

The repository root should be a source and marketplace container, not itself a plugin. This separates the user-facing runtime from the high-authority maintainer workflow, lets public users install only `wayfinder`, and keeps both packages in one review and certification boundary. A single Claude-compatible `.claude-plugin/marketplace.json` can be the initial repository catalog because current OpenAI workspace import and GitHub Copilot CLI documentation both accept that location and format. The main catalog should initially list only the runtime plugin. The maintainer package can remain publicly inspectable and directly usable by contributors without being promoted as an ordinary user install until its cross-client invocation policy is deliberately settled.

GitHub Actions can run the complete eight-entry candidate-revision-8 matrix from the owner's Mac without local Windows or Linux virtual machines. Use explicit hosted-runner labels, exact runtime patch versions, runtime and executable probes, an actual filesystem case-sensitivity probe, `strategy.fail-fast: false`, and one uniquely named evidence artifact per matrix entry. Ordinary Actions artifacts are useful for review but expire and can be deleted. After explicit owner approval, publish the complete evidence set as assets on a GitHub **immutable release**, which locks the tag and assets and automatically creates a release attestation. Certification evidence and plugin releases should use separate tag namespaces so a passing matrix cannot accidentally activate or publish Wayfinder.

This is a packaging and delivery recommendation, not an activation recommendation. The frozen contract, release file, three adapters, accepted historical evidence, and accepted parity evidence should enter the new repository byte-for-byte. The repository move should be its own bounded tranche before hosted certification.

## Why this direction is now practical

The cross-client ecosystem has converged enough to avoid three distributions:

- The [Agent Plugins 1.0 specification](https://agent-plugins.org/specification) defines a portable package with root `plugin.json`, skills under immediate children of `skills/`, optional root `mcp.json`, and client-specific extension namespaces. It also requires all package-supplied paths to remain inside the plugin root.
- [OpenAI recommends the portable root manifest for new plugin packages](https://developers.openai.com/plugins/build/plugins), automatically discovers `skills/`, and keeps OpenAI-specific skill metadata in `agents/openai.yaml`.
- [GitHub Copilot supports Agent Plugins 1.0 directly](https://docs.github.com/en/copilot/concepts/agents/about-plugins), including root `plugin.json`, fixed `skills/`, and optional Copilot-specific content under `com.github.copilot/`.
- [Claude's current plugin format](https://code.claude.com/docs/en/plugins) still documents `.claude-plugin/plugin.json`, but it uses the same root `skills/<name>/SKILL.md` layout. A compatibility manifest is therefore enough; the skill content does not need to be copied.
- All three clients use Agent Skills-style `SKILL.md` packages. The [Agent Skills specification](https://agentskills.io/specification) standardizes the skill directory, required frontmatter, and optional `scripts/`, `references/`, and `assets/` content already used by Wayfinder.

The important limitation is that portable packaging is not the same as identical host behavior. Invocation controls, installation commands, marketplace metadata, UI presentation, permissions, and validation remain client-specific. Cross-client support therefore means one portable source plus tested compatibility metadata—not a claim that every host treats every optional field identically.

## Current source state and migration implications

The pre-research source inventory on 2026-09-14 contained 95 files: approximately 840 KB under `wayfinder` and 1.2 MB under `wayfinder-maintainer`. The runtime skill contains the three standard-library adapters, contract assets, schemas, templates, conformance fixtures, and runtime references. The maintainer skill contains the design record, 18 accepted initialization research records, tooling, conformance harness, historical evidence, parity evidence, and the first macOS matrix entry. This draft adds one maintainer-owned research file.

Both directories are currently untracked in the MyPond repository. `git ls-files` returns zero files and `git log --all -- skills/wayfinder skills/wayfinder-maintainer` returns no history. Consequently, there is no meaningful Git subtree history to extract. The correct provenance operation is an initial import of the exact working-tree bytes, accompanied by a migration manifest that records their source location, import timestamp, and digests. Fabricating history or importing unrelated MyPond history would reduce clarity.

The currently accepted governed digests still match:

| Artifact | SHA-256 |
| --- | --- |
| Contract | `75a0fe4ac106ffb6ad496a38d65addf004f03f128c18fd512232c4631315955b` |
| Release registry | `677fa5af49c11532d49875bd8d1138a36903668449188e6358f2d0a5947f2284` |
| Python adapter | `d0ce8b8e21606bd026ff82b93945cbef3225387b0c47702b688d285c966679d4` |
| Node.js adapter | `fcd01cfd47c98488eb2e85055924630642ee4093c02272bb67ba961d4e084125` |
| PowerShell adapter | `9b64624f0c837db6082ce241a3f17f3d05614490e4e721d757588c8fefbe0bce` |

Moving a file changes its repository path but need not change its bytes. Historical evidence should remain byte-identical even when it mentions the old `skills/...` paths; those paths describe the environment in which that evidence was created. New evidence should use the new topology. The maintainer tool should gain an explicit repository or runtime-plugin root instead of rewriting accepted evidence or assuming the old MyPond-relative location.

## Alternatives considered

### A. One root plugin containing both skills

This is closest to today's sibling-directory layout and requires the fewest path changes. It is not the best public product boundary. Every runtime install would also install a high-authority maintainer workflow, enlarge the package with certification history, and expose a skill ordinary users do not need. OpenAI already marks the maintainer as explicit-only in `agents/openai.yaml`, but that file does not govern every client.

Claude and Copilot both document a top-level `disable-model-invocation` skill field. The portable Agent Skills specification does not currently include that field in its closed set, while OpenAI uses `agents/openai.yaml` for the same policy. Adding the field without testing could trade one compatibility problem for another. Packaging separation removes the need to solve that mismatch for runtime users.

### B. Two plugin packages in one marketplace repository — recommended

This keeps one governance and CI repository while giving runtime and maintenance different installation, release, and visibility policies. Each package owns one canonical skill tree. The maintainer can target an explicitly supplied checkout or runtime-plugin root, so it does not need a copied runtime package. Repository contributors can work with both sibling packages, while end users install only the runtime plugin.

The tradeoff is a small amount of packaging metadata in each package and one maintainer-tool path migration. That is preferable to duplicated source or a permanently coupled user package.

### C. A separate repository or copied tree for each client

Reject this. Three repositories or generated checked-in copies would create synchronization and review hazards around already digest-sensitive artifacts. The clients now share enough standards that this complexity has no compensating benefit.

### D. A runtime plugin plus an unpackaged maintainer directory

This would keep the user package clean, but it would make maintainer onboarding and cross-client testing less consistent. Making the maintainer a valid, separately installable plugin package is inexpensive and gives contributors the same directory contract as users, even if it is not initially listed in the main marketplace.

## Recommended repository topology

```text
wayfinder/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── LICENSE
├── NOTICE                         # only if required by the chosen license/content
├── CONTRIBUTING.md
├── SECURITY.md
├── SUPPORT.md
├── CHANGELOG.md
├── .gitattributes
├── .gitignore
├── .claude-plugin/
│   └── marketplace.json          # shared initial catalog; runtime listed first
├── .github/
│   ├── CODEOWNERS
│   ├── dependabot.yml
│   ├── ISSUE_TEMPLATE/
│   ├── pull_request_template.md
│   └── workflows/
│       ├── validate.yml
│       ├── conformance.yml
│       ├── certify.yml
│       └── publish-evidence.yml
├── docs/
│   ├── architecture.md
│   ├── certification.md
│   ├── compatibility.md
│   ├── governance.md
│   └── migration-provenance.md
└── plugins/
    ├── wayfinder/
    │   ├── plugin.json            # canonical Agent Plugins 1.0 manifest
    │   ├── .claude-plugin/
    │   │   └── plugin.json        # generated/validated Claude compatibility view
    │   └── skills/
    │       └── wayfinder/
    │           ├── SKILL.md
    │           ├── agents/openai.yaml
    │           ├── assets/contract-v1/
    │           ├── references/
    │           └── scripts/adapters/
    └── wayfinder-maintainer/
        ├── plugin.json            # canonical Agent Plugins 1.0 manifest
        ├── .claude-plugin/
        │   └── plugin.json        # generated/validated Claude compatibility view
        └── skills/
            └── wayfinder-maintainer/
                ├── SKILL.md
                ├── agents/openai.yaml
                ├── certification/v1/
                ├── references/
                └── scripts/
```

### Topology rules

- Treat `plugins/*/skills/*` as the only skill-content sources. Do not mirror them into `.agents/skills`, `.claude/skills`, or `.github/skills`.
- Keep each root portable `plugin.json` authoritative for name, version, description, author, repository, and license. Generate or validate the Claude compatibility manifest from it and fail CI on drift.
- Keep the runtime plugin free of maintainer evidence and maintainer-only code.
- Keep historical evidence beside the maintainer skill so it remains inspectable but is not downloaded with the runtime plugin.
- Do not add `mcp.json`, hooks, custom agents, or client-specific rules merely to make the tree look complete. Wayfinder currently needs local deterministic scripts, not a network service.
- Do not use symlinks as a deduplication strategy. Portable-plugin containment permits only links that resolve inside a plugin root, and Windows checkout behavior adds avoidable uncertainty.
- Do not use Git LFS for the current approximately 2 MB corpus. Plain Git keeps evidence reviewable, diffable, and content-addressed.

The root `CLAUDE.md` should contain only `@AGENTS.md` plus genuinely Claude-specific contributor guidance. Claude's [project-memory documentation](https://code.claude.com/docs/en/memory) explicitly recommends this bridge when a repository already uses `AGENTS.md`. GitHub recommends root `AGENTS.md` for standing rules shared across agents, with `.github/copilot-instructions.md` reserved for Copilot-only rules. Avoid creating the latter unless a real Copilot-specific need appears.

## Plugin and release identities

Keep four identities separate:

1. **Contract version:** Wayfinder semantic contract `v1`.
2. **Candidate revision:** currently `v1-candidate-revision-8`.
3. **Plugin package version:** a SemVer used by plugin clients and caches.
4. **Certification evidence release:** an immutable publication of reports for one candidate and source commit.

The Agent Plugins specification recommends Semantic Versioning for plugin versions. If the repository becomes public before activation, a package version such as `1.0.0-rc.8` accurately signals a pre-release, but choosing it is a packaging decision that should be approved. It must not silently rewrite the governed release registry or imply activation. Use different tag prefixes, for example:

- `plugin-v1.0.0-rc.8` for an installable pre-release package, if one is intentionally published;
- `evidence-v1-candidate-revision-8-matrix-1` for the immutable certification evidence set.

Do not publish the runtime marketplace entry or mark a plugin release as latest merely because the matrix passes. Activation remains its own explicit decision.

## GitHub Actions certification architecture

### 1. Pull-request validation

`validate.yml` should be read-only and deterministic. It should:

- run the maintainer doctor;
- verify frozen contract, release, adapter, historical-evidence, and parity-evidence digests;
- validate the two portable manifests against the checked-in Agent Plugins 1.0 schema or an independently pinned validator;
- validate both Agent Skills packages;
- run Claude's strict plugin validator when the pinned CLI supports it;
- verify that the Claude manifests and marketplace catalog agree with canonical metadata;
- run the local conformance/parity checks appropriate to the changed paths; and
- prove that generated compatibility files are current without rewriting the checkout.

Do not install package dependencies just to run Wayfinder tests. The adapters and harness are already standard-library implementations. If CI needs client CLIs for packaging smoke tests, pin those tools separately and keep those tests distinct from contract conformance.

### 2. The eight-entry conformance matrix

`certify.yml` should use an explicit `matrix.include` list, not a Cartesian product, so the only jobs are the eight accepted entries:

| Entry | Hosted runner | Runtime setup |
| --- | --- | --- |
| CPython 3.14.7 on macOS | fixed GA macOS label, architecture stated | `actions/setup-python` with exact `3.14.7` and architecture |
| CPython 3.14.7 on Linux | fixed GA Ubuntu label | same exact version |
| CPython 3.14.7 on Windows | fixed GA Windows label | same exact version |
| Node.js 24.21.0 on macOS | same fixed macOS label | `actions/setup-node` with exact `24.21.0` |
| Node.js 24.21.0 on Linux | same fixed Ubuntu label | same exact version |
| Node.js 24.21.0 on Windows | same fixed Windows label | same exact version |
| PowerShell 7.6.6 on Windows | same fixed Windows label | verify preinstalled exact version or use the official release ZIP with published SHA-256 |
| PowerShell 7.6.6 on Linux | same fixed Ubuntu label | verify preinstalled exact version or use the official release tarball with published SHA-256 |

Use fixed labels such as `ubuntu-24.04`, `windows-2025`, and an explicitly selected macOS label rather than `*-latest`; GitHub notes that latest aliases migrate over time. The exact macOS label and architecture should be chosen only after confirming that the exact CPython and Node distributions are available on it. Current public standard-runner documentation offers x64 Linux and Windows plus both Intel and arm64 macOS choices, and states that standard runners are free and unlimited for public repositories.

`actions/setup-python` documents exact major/minor/patch selection, architecture selection, and the resolved interpreter path. `actions/setup-node` likewise supports exact patch versions and architecture selection. Do not accept a semver range or an already-installed executable merely because its major/minor line matches.

PowerShell 7.6.6 was released with upstream SHA-256 hashes. For x64, the official release identifies the Windows ZIP as `02FE458BE20493FBDF43F61EA20610B811EE6C738AB1676C61B9CFCD1A33C860` and the Linux tarball as `DDBC4A2D113BBD46D283CFEDCBCD117A70CAEFD7673F41F2B4E0000BADF103BC`. A future workflow may download and unpack those exact assets into the job's temporary tool directory, but doing so is an external-download decision and must be authorized for the migration/certification tranche. Do not rely on the runner's rolling PowerShell patch.

Each job must record and verify:

- source commit SHA, workflow run ID and attempt, runner image label and image version;
- runtime implementation and exact version;
- OS family and reported OS version;
- process and runtime architecture;
- locale, timezone, filesystem encoding, and unavailable observations;
- absolute executable path, resolved target, and executable-file SHA-256 where readable;
- actual filesystem case behavior using create/probe/cleanup operations in the job workspace;
- exact adapter path and adapter SHA-256;
- candidate, contract, release, fixture-index, expected-output, and result-set digests; and
- case total and outcome, requiring 305/305 for pass.

Set `strategy.fail-fast: false`. That preserves passing evidence when another environment fails or is unavailable. Upload from each job with `if: always()` and label the report from its actual result; never turn a setup failure into a passing or simulated entry. Artifact names should include the candidate, entry ID, source commit, workflow run ID, and run attempt so parallel or repeated runs cannot collide.

### 3. Aggregation and approval

An aggregator should run with `if: always()`, download all available per-entry artifacts, and validate each report and digest. It may produce a clearly labeled diagnostic inventory when entries are missing or failing, but it must create the maintainer-owned passing matrix report only when all eight reports exist, report 305/305, and agree on every required binding.

The workflow should then stop with reviewable Actions artifacts. `upload-artifact` v4 and later creates immutable artifact IDs, but Actions artifacts have retention limits and can be deleted with their workflow run. They are staging evidence, not the durable final record.

After the owner explicitly accepts the bounded tranche, a separate `publish-evidence.yml` workflow should:

1. take the approved workflow run and expected digests as explicit inputs;
2. re-download and re-verify every file;
3. create a draft evidence release bound to the exact source commit;
4. attach the eight reports, aggregate report, digest manifest, and provenance metadata; and
5. publish the draft only after all assets are attached.

Enable GitHub's immutable releases feature before this step. GitHub states that an immutable release locks its tag and assets and automatically creates a cryptographically verifiable release attestation. This is a stronger durable home for accepted evidence than an expiring workflow artifact, while the JSON and Markdown reports can also remain committed under the maintainer package in a later reviewed provenance commit if desired.

### 4. Workflow security

For a public repository:

- default `GITHUB_TOKEN` permissions to `contents: read` and grant narrower write permissions only in the separately approved publish workflow;
- pin every third-party and GitHub-authored action to a verified full commit SHA, which GitHub describes as the only immutable action reference;
- never execute untrusted pull-request code with repository secrets or a write token;
- avoid `pull_request_target` for conformance execution;
- protect `.github/workflows/`, portable manifests, frozen contract assets, adapters, accepted evidence, and `CODEOWNERS` itself with code-owner review;
- require pull requests and required checks on the default branch, block force pushes and deletions, and protect release tags;
- use Dependabot for pinned GitHub Actions updates, reviewing the resolved source before changing a SHA; and
- keep release publication manual and separate from test execution.

## Public repository governance

The initial repository should include a clear README, contribution and security processes, support boundaries, a changelog, and an explicit license. An Apache-2.0 license is a strong default for cross-vendor tooling because it is permissive and includes an express patent grant, but the copyright holder and license are owner decisions, not technical defaults that should be silently applied. MIT is simpler but lacks the same explicit patent language. Resolve this before making the repository public.

Use a default-branch ruleset requiring pull requests, the validation and conformance checks relevant to changed paths, stale-review dismissal, and no force pushes. Add `CODEOWNERS` coverage for workflows and frozen artifacts. GitHub supports code owners and repository rulesets on public repositories, including required reviews, signed commits, and required checks. Whether to require signed commits from all contributors is a community-friction decision; immutable evidence release tags matter more than forcing every contribution commit to be signed.

Use `.gitattributes` to preserve LF endings for governed text (`*.md`, `*.json`, `*.py`, `*.mjs`, `*.ps1`, `*.abnf`) on all platforms. Verify hashes before and after the initial add because Git's checkout normalization can otherwise obscure a newline change. Do not use automatic formatters on frozen assets or accepted evidence.

## Safe migration sequence

Treat migration and hosted certification as separate tranches.

### Tranche 1 — repository skeleton and byte-preserving import

1. Approve the repository owner/name, license, two-plugin topology, marketplace visibility, and initial plugin-version policy.
2. Run the maintainer doctor and verify all accepted digests in MyPond.
3. Create a content manifest of every source file and SHA-256 before copying.
4. Create the new repository skeleton without publishing or enabling Actions.
5. Copy the two skill trees into their new plugin roots without editing governed, adapter, package, historical-evidence, or parity-evidence bytes.
6. Add portable manifests, Claude compatibility manifests, contributor documents, and read-only validation workflows.
7. Adapt only maintainer-owned path discovery and orchestration to accept the repository/runtime-plugin root explicitly.
8. Re-run doctor, local parity, plugin validation, and the content manifest comparison.
9. Present the complete diff and digest report for approval before creating or pushing Git history.

Because the current trees are untracked, the first commit should state that it is an exact import from the MyPond working tree and point to `docs/migration-provenance.md`. Do not rewrite historical evidence to make it appear that it was generated in the new repository.

### Tranche 2 — GitHub repository controls and CI smoke validation

Create the public repository, push only the approved import, enable rulesets and immutable releases, then run packaging validation and non-certifying smoke tests. Confirm that Codex, Claude, and Copilot can each discover the runtime skill from their supported installation path. This is distribution compatibility evidence, not Wayfinder semantic certification.

### Tranche 3 — bounded certification matrix

Only after explicit authorization for hosted execution and runtime downloads, run the exact eight-entry matrix. Preserve every authentic per-entry report, aggregate only if all entries pass, and present the result for explicit acceptance. Do not run forward tests, independent evaluation, recovery expansion, full-family certification, plugin publication, or activation in this tranche.

### Later tranches

Plugin-directory submission, runtime guidance, isolated forward tests, full-family certification, and activation remain distinct decisions. A public repository and a green hosted matrix make them possible; neither authorizes them.

## Decisions needed before implementation

1. **Repository identity:** owner and public repository name. `wayfinder` is the clearest default if available.
2. **License and copyright holder:** Apache-2.0 is recommended, subject to owner approval.
3. **Package boundary:** approve two plugin subdirectories in one repository rather than one plugin containing both skills.
4. **Maintainer visibility:** recommended initial state is public source but absent from the main end-user marketplace catalog; contributors invoke or install it deliberately.
5. **Plugin prerelease version:** decide whether the unactivated package begins at `1.0.0-rc.8` or remains unpublished until activation.
6. **Hosted download authority:** authorize exact runtime downloads in GitHub Actions, including checksum-verified PowerShell release assets, separately from this research.
7. **Evidence permanence:** recommended durable record is both content-digest-bound reports and an immutable GitHub evidence release after explicit approval.

## Confidence and limitations

Confidence is high in the two-package repository topology and GitHub Actions evidence route because the relevant formats and runner capabilities are documented by their current primary sources. Confidence is moderate in using one `.claude-plugin/marketplace.json` as the only catalog forever: OpenAI and Copilot currently accept it, but vendor discovery conventions can evolve. Keep catalog generation isolated so a future native catalog can be added without moving skill content.

No client-install smoke test was performed in this research tranche. The installed Codex, Claude, and Copilot CLI versions and their exact validator behavior were not inspected or changed. The post-draft maintainer doctor used the existing CPython 3.14.7 interpreter and passed 28 of 29 checks; its sole failure was the adapter-probe group because no `pwsh` executable is installed or discoverable on this Mac. All package, historical-evidence, accepted-matrix-binding, parity-evidence, text-profile, and syntax checks passed. Exact availability of CPython 3.14.7 and Node.js 24.21.0 for the chosen hosted macOS architecture must still be demonstrated by the hosted workflow; documentation of version-selection syntax is not proof that every requested build is present. Runner images are updated weekly, so every report must capture the actual image version and must not infer environment facts from its YAML label.

The Apache-2.0 recommendation is an engineering and open-source-governance judgment, not legal advice. The owner should confirm authorship, third-party content, and notice obligations before publication.

## Primary sources

All sources were accessed on 2026-09-14.

| Source | Applicability | Limitation |
| --- | --- | --- |
| [Agent Plugins Specification 1.0.0](https://agent-plugins.org/specification) | Direct normative packaging, discovery, containment, extensions, and versioning rules | Does not define installation UX or client-specific invocation policy |
| [Agent Skills specification](https://agentskills.io/specification) | Direct normative skill directory and frontmatter rules | Client extensions and discovery locations vary |
| [OpenAI: Build an Agent Plugin](https://developers.openai.com/plugins/build/plugins) | Direct for Codex/ChatGPT portable package layout | OpenAI product behavior can evolve independently of the open specification |
| [OpenAI: Build skills](https://developers.openai.com/plugins/build/skills) | Direct for `SKILL.md`, resources, and `agents/openai.yaml` | OpenAI-specific invocation policy is not portable |
| [OpenAI: Plugin management](https://learn.chatgpt.com/docs/enterprise/plugin-management) | Direct for GitHub marketplace import and accepted Claude/portable package formats | Workspace administration behavior is not the same as every local CLI path |
| [OpenAI: Codex GitHub Action](https://learn.chatgpt.com/docs/github-action) | Direct evidence that Codex can run in Actions | The Wayfinder conformance suite does not need an AI action to test deterministic adapters |
| [Claude: Create plugins](https://code.claude.com/docs/en/plugins) | Direct for Claude package and skill layout | Documents Claude's native manifest, not Agent Plugins 1.0 conformance |
| [Claude: Plugin reference](https://code.claude.com/docs/en/plugins-reference) | Direct for validation, cache containment, and component locations | CLI versions may add behavior after the access date |
| [Claude: Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) | Direct for repository marketplace distribution | Marketplace installation copies packages, so out-of-root source references are unsuitable |
| [Claude: Project memory](https://code.claude.com/docs/en/memory) | Direct for the `CLAUDE.md` to `AGENTS.md` import bridge | Contributor instructions are separate from installed plugin behavior |
| [GitHub: About Copilot plugins](https://docs.github.com/en/copilot/concepts/agents/about-plugins) | Direct for Agent Plugins 1.0 support and Copilot extension namespaces | Some surfaces require paid Copilot access |
| [GitHub: Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference) | Direct for subdirectory installs and marketplace locations | CLI syntax may change; pin and smoke-test the supported release |
| [GitHub: Agent skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) | Direct for Copilot skill use and validation | Repository-local skill discovery differs from plugin installation |
| [GitHub: Hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners) | Direct for OS labels, architectures, and public-repository cost | Images and installed software are rolling; capture actual image metadata |
| [`actions/setup-python` advanced usage](https://github.com/actions/setup-python/blob/main/docs/advanced-usage.md) | Direct for exact Python patch and architecture selection | Availability of a particular build must be tested |
| [`actions/setup-node` documentation](https://github.com/actions/setup-node/blob/main/README.md) | Direct for exact Node version selection | Can fall back to network distribution downloads |
| [PowerShell 7.6.6 release hashes](https://github.com/PowerShell/PowerShell/discussions/27990) | Direct upstream artifact digests | The workflow must still verify the downloaded file and executable identity |
| [GitHub: Matrix workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) | Direct for `matrix.include` and `fail-fast` behavior | Does not define Wayfinder's aggregation semantics |
| [`actions/upload-artifact`](https://github.com/actions/upload-artifact) | Direct for unique immutable artifact IDs | Workflow artifacts can expire or be deleted |
| [GitHub: Immutable releases](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases) | Direct for locked tags/assets and automatic release attestations | Repository owners can still delete a release; policy and retained digests remain important |
| [GitHub Actions secure use](https://docs.github.com/en/actions/reference/security/secure-use) | Direct for least privilege, action SHA pinning, and workflow review | Security still depends on reviewing pinned action source and untrusted inputs |
| [GitHub: CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners) | Direct for protected-file review | Effective only when paired with required code-owner review |
| [GitHub: Repository rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) | Direct for PR, signature, force-push, deletion, and check controls | Exact available settings depend on repository/account context |
| [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) | Direct license terms, including patent grant | License selection and authorship review require owner judgment |
