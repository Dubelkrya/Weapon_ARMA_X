# AGENTS.md

## Purpose

This repository uses an explicit handoff policy for OpenCode Go work. Before giving the user any ready-to-run OpenCode task, the architect must choose both the execution agent and the neural model. These are separate routing decisions.

The policy applies to ARMST / Arma Reforger / Enfusion work, repository maintenance, audit work, migrations, validation, and supporting research.

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

## 3. OpenCode Go neural-model selection

The neural model is a separate decision from the primary agent and subagent.

Before execution, the operator must run `/models` in OpenCode and confirm that the recommended model is currently available through the user's OpenCode Go subscription.

The OpenCode Go catalog is dynamic. Do not assume that a model remains available permanently, and do not fail a task only because the originally recommended model is unavailable. Select the nearest suitable available model and record the actual model used.

Current OpenCode documentation lists models such as GPT 5.6 Luna, Kimi K3, Kimi K2.7 Code, GLM-5.3 / GLM-5.3-Flash, MiniMax M3, Qwen3.8 Max / Flash, DeepSeek V4 Pro / Flash, and others. `/models` is the runtime source of truth.

### Project default

Default recommendation for architecture-sensitive ARMST work:

`GPT 5.6 Luna`

Use it by default when the task combines strict scope control, repository/tool use, resource-identity reasoning, GUID/reference work, inheritance analysis, validation, and implementation.

This is a project routing default, not a claim that it is objectively the best model for every task.

### Code-heavy implementation alternative

`Kimi K2.7 Code`

Consider it for tasks dominated by code generation or mechanical implementation, such as scripts, scanners, parsers, repetitive source edits, and refactors where the architecture decision has already been made and tightly specified.

Do not choose it automatically for identity-sensitive ARMST migration merely because the task contains code.

### High-volume read-only alternatives

Examples include currently available Flash-class models such as:

- `GLM-5.3-Flash`
- `DeepSeek V4.1 Flash`
- `DeepSeek V4 Flash`
- `Qwen3.8 Flash`

Consider these for broad inventory/search passes, large read-only classification jobs, evidence collection, and repeated low-risk checks.

Their output is evidence input. It does not replace an architectural decision or evidence gate.

### Independent reasoning / review alternatives

When the architecture is ambiguous or a destructive operation is proposed, consider a second capable model that is different from the executor, depending on current `/models` availability. Candidates may include models such as:

- `Kimi K3`
- `Grok 4.6`
- `Qwen3.8 Max`
- `DeepSeek V4 Pro`
- `GLM-5.3`

Do not select a model solely because its name contains `Max`, `Pro`, or similar branding.

## 4. Risk-based routing

### LOW risk

Examples:

- read-only lookup;
- exact GUID/reference search;
- simple static verification;
- proven orphan check;
- narrow, reversible file cleanup.

Typical routing:

- primary agent: `Plan` for read-only, `Build` for writes;
- model: `GPT 5.6 Luna` by default;
- a Flash-class model may be used for large read-only batches;
- independent reviewer: normally none.

### MEDIUM risk

Examples:

- local prefab rename;
- GUID-preserving ARMST naming migration;
- proven reference rerouting;
- inheritance-sensitive local edit;
- change affecting several known local dependents.

Typical routing:

- primary agent: `Build`;
- model: `GPT 5.6 Luna` by default;
- optional independent review by another capable Go model.

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

1. `Plan` pass.
2. Evidence report.
3. Architect review/approval.
4. `Build` pass with tightly bounded scope.
5. Post-change validation.
6. Independent review with a different capable model when practical.

The executor must not silently broaden or reinterpret the approved Plan scope.

## 5. Required handoff format

Before every ready-to-run OpenCode task, the architect must give the user this routing header before the copy-paste prompt:

```text
OpenCode primary agent: <Build | Plan>
OpenCode subagent: <none | @general | @explore | @scout>
OpenCode Go model: <recommended model>
Why this agent: <short reason>
Why this model: <short reason>
Risk: <LOW | MEDIUM | HIGH>
Independent reviewer: <none | model>
```

Only after this header should the ready-to-run agent prompt be provided.

If execution requires two stages, provide both routes explicitly, for example:

```text
Stage 1:
OpenCode primary agent: Plan
OpenCode subagent: @explore
OpenCode Go model: GPT 5.6 Luna
Risk: HIGH

Stage 2, only after architect approval:
OpenCode primary agent: Build
OpenCode subagent: none
OpenCode Go model: GPT 5.6 Luna
Independent reviewer: <different available model>
```

## 6. Runtime model-availability rule

At the beginning of an OpenCode Go execution:

1. Run `/models`.
2. Confirm the recommended model is available through OpenCode Go.
3. If unavailable, choose the nearest model for the same task class.
4. Record the actual model used in the final report.
5. Do not change task scope merely because a different model is used.

OpenCode documentation, not hard-coded repository text, is authoritative for the provider's current catalog. This file defines project routing policy only.

## 7. ARMST architecture gates override model choice

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

## 8. Final agent report

Every task report must state at least:

```text
PRIMARY_AGENT_USED:
SUBAGENT_USED:
MODEL_RECOMMENDED:
MODEL_ACTUALLY_USED:
RISK:
SCOPE_CHANGED_FROM_PROMPT: YES / NO
FILES_CHANGED:
VALIDATION_STATUS:
GIT_STATUS:
```

For architecture-sensitive migration, also report the identity/reference/inheritance fields required by the task-specific prompt.

## 9. Architect responsibility

The architect is responsible for deciding:

- whether the work is Plan or Build;
- whether a subagent is useful;
- which current OpenCode Go model best matches the task class;
- whether independent review is required;
- whether evidence is sufficient to permit mutation;
- whether a reported PASS is architecturally acceptable.

The executing agent is responsible for staying inside the approved scope and reporting uncertainty instead of inventing evidence.
