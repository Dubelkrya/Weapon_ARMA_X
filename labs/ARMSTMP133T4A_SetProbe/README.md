# ARMSTMP133T4A_SetProbe — historical diagnostic snapshot (T4a)

This directory is a **published snapshot** of the local isolated lab
`...\addons\ARMSTMP133T4A_SetProbe`, published for review in the knowledge repo
(`Dubelkrya/Weapon_ARMA_X`, branch `t4b/installed-mag-probe`).

It is the **historical diagnostic** for the **disposable**-magazine `SetAmmoCount` API test
(T4a). It is **not** a gameplay feature and is **not** used by the current T4b lab.

## What this snapshot actually contains (truthful, matches the local files)

- `addon.gproj` — lab project `ARMSTMP133T4A_SetProbe`.
- `Scripts/Game/ARMST_T4A/ARMST_T4A_SetterProbe.c` — `ARMST_T4A_SetterProbe` (baseline
  component) + `ARMST_T4A_AddRoundUserAction` (`ScriptedUserAction`).
- `Prefabs/Test/ARMST_T4A_TestMagazine.et` — disposable test magazine carrying the probe and
  an `ActionsManagerComponent "{F092E6B0537754FD}"` with
  `additionalActions { ARMST_T4A_AddRoundUserAction "{6D80CBBC9F7E0524}" { UIInfo SCR_ActionUIInfo "{6A8708B05CF3E69E}" { } } }`.

**Important honesty note:** the published prefab is the **actual local version** (last saved by
the owner's Workbench — it also carries `coords 148.231 1.9 77.851`). In this snapshot the T4a
action has **no `ParentContextList`** and an **empty `UIInfo` `SCR_ActionUIInfo`**, and the
list is written as `additionalActions {` (no `+{`). An earlier, unverified draft that added
`additionalActions +{ … ParentContextList { "default" } UIInfo … Name … }` is **not** present
here; that context/name work was never verified in game. This README is corrected to match the
source exactly.

## Status / boundaries

- Same **MP-133 magazine direction** as T4b; this is a snapshot only. It is **not** merged from
  the `t4a/interaction-patch` branch, and the **local T4a lab is unchanged** by this publication.
- T4b (`labs/ARMSTMP133T4B_InstalledMagProbe`) is the active line of work.
- Local copy and this published copy are byte-identical (see `MANIFEST.sha256`).
