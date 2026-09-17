# AGENTS.md

## Purpose

This repository uses an explicit handoff policy for OpenCode Go work. Before giving the user any ready-to-run OpenCode task, the architect must choose:

1. the primary execution agent;
2. an optional subagent;
3. the OpenCode Go neural model;
4. any escalation / independent-review model.

These are separate routing decisions.

The policy applies to ARMST / Arma Reforger / Enfusion work, repository maintenance, audit work, migrations, validation, and supporting research.

The objective is **not to choose the strongest or most expensive model by default**. The objective is to choose the **least expensive model that is sufficiently reliable for the task**, while escalating when the expected cost of an error is higher than the savings from a cheaper model.

---

## 1. Primary agent selection

Choose exactly one primary OpenCode agent for every task.

- `Build` — use when the task may modify files, run implementation commands, perform migrations, tests, builds, repository changes, Git operations, or other writes.
- `Plan` — use when the task is analysis, architecture, verification planning, review, or other read-only work where no files should be changed.

Do not use `Build` for a task whose contract is strictly read-only.

## 2. Subagent selection

Subagents are optional and do not replace the primary `Build` / `Plan` choice.

- `@general` — isolated complex multi-step subtask with a narrow boundary.
- `@explore` — read-only investigation of local code, resources, inheritance, references, repository structure, or filesystem evidence.
- `@scout` — research of external documentation, APIs, upstream sources, dependencies, provider documentation, or public specifications.

If no subagent is needed, state `none` explicitly.

---

## 3. OpenCode Go model-selection principle

The neural model is a separate decision from the primary agent and subagent.

Before execution, run `/models` and confirm that the recommended model is currently available through the user's OpenCode Go subscription.

The OpenCode Go catalog, prices, usage allowances, and provider behavior are dynamic. Do not assume that a model remains available permanently. `/models` and current OpenCode Go provider documentation are the runtime source of truth.

### Optimization objective

Choose the model that minimizes the expected total cost of the task, not merely token price.

Consider:

- subscription / usage cost;
- expected retry count;
- context size required;
- tool-use reliability required;
- instruction-following precision;
- amount of architecture reasoning required;
- destructiveness / reversibility of the operation;
- probability and cost of a wrong decision;
- whether another model or the architect will review the result before mutation.

A cheap model that produces evidence reliably can be optimal even if it is not the strongest reasoner.

A more expensive model becomes optimal when a wrong architectural decision would cost more than the model-price difference.

### Core routing pattern

For ARMST work, prefer this pipeline when practical:

`cheap evidence collection -> architecture decision -> bounded execution -> cheap independent validation`

Do not use an expensive reasoning model merely to perform grep, GUID enumeration, file inventory, or other deterministic evidence collection.

Do not use a cheap evidence model as the sole decision-maker for ambiguous identity-sensitive or destructive architecture changes.

### Evidence-first escalation rule

Do **not** start with `GPT 5.6 Luna` merely because a task mentions GUIDs, inheritance, ResourceDB, provenance, or identity ambiguity.

If the current stage is still primarily mechanical evidence collection — for example exact GUID/path lookup, loaded-package enumeration, reference search, owner counting, parent-chain extraction, ResourceDB text lookup, or deterministic preflight/postcheck — start with `DeepSeek V4 Flash` (or the cheapest currently available equivalent that is sufficiently reliable).

Escalate to `GPT 5.6 Luna` only after evidence collection when one or more of the following is actually present:

- multiple plausible identity owners remain;
- filesystem, `.meta`, ResourceDB, package, or inheritance evidence conflicts;
- the same evidence supports more than one reasonable architecture interpretation;
- the cause of a runtime identity mismatch cannot be classified mechanically;
- a mutation decision depends on distinguishing cause from correlation;
- a destructive or identity-sensitive action would otherwise require guessing.

A read-only provenance audit should therefore normally be split into stages:

`Flash evidence pass -> architect review -> Luna only if ambiguity remains`

Do not recommend Luna "just in case" for a search/provenance task that can first be reduced to exact facts cheaply.

---

## 4. Model task classes

Model names below are routing examples based on the current OpenCode Go catalog. Runtime availability must always be checked with `/models`.

### A. Evidence / exploration tier

Preferred starting point:

`DeepSeek V4 Flash`

Use for work dominated by:

- broad filesystem / repository search;
- GUID occurrence scans;
- reference enumeration;
- prefab/resource inventory;
- read-only cluster preflight;
- duplicate candidate enumeration;
- deterministic static checks;
- filling a tightly specified evidence report;
- post-change verification against explicit invariants.

Why this tier is preferred:

- evidence collection is usually high-volume and mechanically checkable;
- OpenCode Go usage is cost-based, so cheaper models preserve much more subscription capacity;
- errors can usually be caught by exact checks or a later architecture gate.

Other currently available Flash / low-cost models may be substituted when they fit the task and `/models` confirms availability.

Output from this tier is **evidence**, not automatic architecture approval.

### B. Architecture / identity-sensitive reasoning tier

Preferred project choice:

`GPT 5.6 Luna`

Use when the task requires one or more of:

- deciding local-vs-vanilla resource identity;
- reasoning about GUID ownership;
- interpreting conflicting provenance evidence;
- inheritance-layer placement decisions;
- deciding whether a shadow should be localized, removed, or reviewed;
- resolving ambiguous dependency intent;
- integrating many evidence sources into one migration decision;
- tightly scoped execution where instruction compliance and tool use matter more than raw throughput.

Luna is **not the universal default**. It is the default architecture-sensitive choice when cheaper evidence models are no longer sufficient.

### C. Long-context / alternative executor tier

Candidate:

`DeepSeek V4 Pro`

Consider when:

- the task needs a large retained context;
- the Plan is already approved and execution is bounded;
- an alternative executor is useful;
- the current Go economics make it more efficient than another reasoning model.

Do not select it only because it is named `Pro`.

### D. Code-heavy implementation tier

Candidate:

`Kimi K2.7 Code`

Consider for tasks dominated by code implementation rather than architecture judgment, for example:

- scanners;
- parsers;
- migration utilities;
- repository scripts;
- mechanical refactors;
- repetitive source edits after architecture has already been specified.

Do not automatically use a code-specialized model for Enfusion GUID/resource-identity migration merely because files are being edited.

### E. Escalation / second-opinion tier

Depending on current `/models` availability, candidates can include models such as:

- `Kimi K3`;
- `Grok 4.6`;
- `Qwen3.8 Max`;
- `GLM-5.3`;
- another strong model sufficiently independent from the executor.

Use these selectively for:

- conflicting evidence;
- HIGH-risk destructive decisions;
- unresolved identity ambiguity;
- disagreement between Plan and Build evidence;
- `REVIEW_REQUIRED` cases where a second independent interpretation is valuable.

Do not spend high-cost models on routine evidence collection.

Do not select a model solely because its name contains `Max`, `Pro`, or similar branding.

---

## 5. Risk and model cost are separate dimensions

Task risk and model price are not the same thing.

A LOW-risk GUID search can use a cheap model even though GUIDs are involved.

A HIGH-risk deletion should not be delegated to a cheap model as the sole architecture decision-maker merely because the actual filesystem commands are simple.

### LOW risk

Examples:

- read-only lookup;
- exact GUID/reference search;
- simple static verification;
- proven orphan check;
- deterministic post-change validation;
- narrow reversible cleanup whose preconditions have already been architecturally approved.

Typical routing:

- read-only evidence: `Plan` + `@explore` + `DeepSeek V4 Flash`;
- tightly bounded write after approval: `Build` + a sufficiently reliable executor;
- independent reviewer: normally none unless evidence is inconsistent.

Escalate from the evidence tier when:

- references cannot be classified;
- parent identity is unresolved;
- source evidence conflicts;
- the proposed action becomes destructive and necessity is not proved.

### MEDIUM risk

Examples:

- local prefab rename;
- GUID-preserving ARMST naming migration;
- proven reference rerouting;
- inheritance-sensitive local edit;
- change affecting several known local dependents.

Typical routing:

1. cheap evidence pass when useful;
2. architecture decision with `GPT 5.6 Luna` when identity/inheritance reasoning is material;
3. `Build` using Luna, DeepSeek V4 Pro, Kimi K2.7 Code, or another current model selected for the actual execution workload;
4. cheap static post-check when validation is deterministic.

### HIGH risk

Examples:

- `VANILLA_SHADOW` localization;
- GUID ownership change;
- shared base migration;
- destructive removal with uncertain dependencies;
- multi-family magazine/ammo changes;
- ambiguous local-vs-vanilla identity;
- migration with conflicting evidence.

Required workflow unless explicitly waived by the architect:

1. Evidence collection (`Plan`, usually cheap evidence model).
2. Architecture reasoning / decision (reasoning-tier model where needed).
3. Architect review/approval.
4. `Build` with tightly bounded scope and an executor suited to the implementation.
5. Deterministic post-change validation (often cheap evidence model).
6. Independent second-model review when uncertainty or blast radius justifies it.

The executor must not silently broaden or reinterpret the approved Plan scope.

---

## 6. Model escalation rules

Start with the cheapest model that is reasonably expected to complete the current stage correctly.

Escalate when one or more of the following occurs:

- `UNKNOWN_REFS > 0`;
- resource identity cannot be proved;
- multiple GUID owners exist unexpectedly;
- parent or inheritance provenance is unresolved;
- localization necessity is ambiguous;
- a destructive action lacks complete dependency evidence;
- two authoritative sources conflict;
- the model begins guessing values or provenance;
- repeated retries erase the expected cost advantage;
- context/tool limitations prevent reliable completion.

Escalation does not authorize a wider task scope.

If a cheaper model returns `REVIEW_REQUIRED`, that is a successful safe outcome, not a failure that must be forced into a decision.

---

## 7. Required handoff format

Before every ready-to-run OpenCode task, the architect must give the user the routing header **before** the copy-paste prompt:

```text
OpenCode primary agent: <Build | Plan>
OpenCode subagent: <none | @general | @explore | @scout>
OpenCode Go model: <recommended model>
Why this agent: <short reason>
Why this model: <cost/risk/task-fit reason>
Risk: <LOW | MEDIUM | HIGH>
Escalation model: <none | model>
Escalate when: <conditions>
Independent reviewer: <none | model>
```

`Why this model` must explain why the recommendation is **optimal / sufficient for this stage**, not why it is supposedly the globally best model.

If execution requires multiple stages, provide the route for every stage explicitly.

Example:

```text
Stage 1 — evidence:
OpenCode primary agent: Plan
OpenCode subagent: @explore
OpenCode Go model: DeepSeek V4 Flash
Why this model: high-volume read-only deterministic evidence collection; cheaper model preserves Go allowance.
Risk: LOW
Escalation model: GPT 5.6 Luna
Escalate when: unknown refs, conflicting identity, unresolved parent, destructive conclusion without proof
Independent reviewer: none

Stage 2 — architecture decision, only if escalation is needed:
OpenCode primary agent: Plan
OpenCode subagent: none
OpenCode Go model: GPT 5.6 Luna
Why this model: identity/inheritance reasoning is now the dominant risk, so the added model cost is justified.
Risk: MEDIUM/HIGH
Independent reviewer: <none or different available model>

Stage 3 — Build, only after architect approval:
OpenCode primary agent: Build
OpenCode subagent: none
OpenCode Go model: <task-optimal executor>
Why this model: <implementation-specific reason>
Risk: <approved risk>
Independent reviewer: <if required>
```

---

## 8. Runtime model-availability and economics rule

At the beginning of an OpenCode Go execution:

1. Run `/models`.
2. Confirm the recommended model is available through OpenCode Go.
3. If unavailable, choose the nearest model for the same task class.
4. If current OpenCode Go pricing / usage economics materially changed, choose the currently optimal equivalent rather than blindly preserving an old model name.
5. Record the actual model used in the final report.
6. Do not change task scope merely because a different model is used.

Do not hard-code request-count estimates or prices into architecture decisions as permanent facts. Current provider documentation is authoritative for those values.

The repository policy defines **routing logic**; OpenCode defines the current catalog and economics.

---

## 9. ARMST architecture gates override model choice

A stronger or more expensive model is never permission to skip evidence.

For ARMST / Enfusion migration, regardless of model:

- filename is not identity evidence;
- vanilla equivalence must be proved from GUID/resource identity or other approved evidence;
- GUID ownership must be checked explicitly;
- local resource GUID, vanilla GUID, imported/materialized metadata identity, and instance IDs must not be conflated;
- backups (`*.bak`) are not live resources and must be excluded from collision/reference scans;
- true vanilla references must remain on vanilla identity;
- global GUID replacement is forbidden;
- parent/inheritance must remain unchanged unless the approved task explicitly changes it;
- semantic gameplay changes are forbidden during identity-only migration;
- uncertainty produces `REVIEW_REQUIRED` rather than a guess.

### VANILLA_SHADOW necessity gate

Before `LOCALIZE_FROM_VANILLA_NEW_GUID`, prove that an ARMST-local resource is actually required.

At minimum evaluate:

- ARMST-local dependents;
- runtime reference count;
- children count;
- dependency/base role;
- `is_needed_by_armst` evidence from the migration plan.

If runtime refs = 0, children = 0, there is no dependency/base role, and `is_needed_by_armst = NO`, evaluate `REMOVE_UNUSED_DUPLICATE` before creating a new ARMST identity.

Do not create a runtime-orphan ARMST resource merely to replace an unused local vanilla shadow.

---

## 10. Final agent report

Every task report must state at least:

```text
PRIMARY_AGENT_USED:
SUBAGENT_USED:
MODEL_RECOMMENDED:
MODEL_ACTUALLY_USED:
ESCALATION_MODEL_USED:
RISK:
SCOPE_CHANGED_FROM_PROMPT: YES / NO
FILES_CHANGED:
VALIDATION_STATUS:
GIT_STATUS:
```

For architecture-sensitive migration, also report the identity/reference/inheritance fields required by the task-specific prompt.

---

## 11. Architect responsibility

The architect is responsible for deciding:

- whether the work is Plan or Build;
- whether a subagent is useful;
- what the current stage of work actually requires: evidence, decision, execution, or validation;
- which currently available OpenCode Go model is the least expensive model sufficiently reliable for that stage;
- when the expected cost of error justifies escalation;
- whether independent review is required;
- whether evidence is sufficient to permit mutation;
- whether a reported PASS is architecturally acceptable.

The executing agent is responsible for staying inside the approved scope, recording the actual model used, and reporting uncertainty instead of inventing evidence.
