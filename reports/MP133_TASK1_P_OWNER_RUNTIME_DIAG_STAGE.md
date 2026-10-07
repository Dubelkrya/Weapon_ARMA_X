# MP-133 Task #1 — P-owner runtime diagnostic (Phase 1G, stage only)

Status: **P_OWNER_DIAG_STAGE_READY_OWNER_REVIEW**
Date: 2026-10-07
Task: Issue #34 comment `6044071573` (Phase 1G — AnimationControllerComponent owner diagnostic, stage only).
Repo / branch / HEAD: `Dubelkrya/Weapon_ARMA_X` @ `t4b/installed-mag-probe` @ `d20cbcc8337b50d99ea4025f9185b3601199f51b`.
Mode: **SOURCE / STATIC ONLY.** Staged scratch under git-ignored `artifacts/`; nothing installed; no Workbench/runtime; no force-add.

---

## 1. Source baseline (base = installed PACT probe)

| File | SHA-256 | blob |
|---|---|---|
| live lab `ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c` | `2568DA60441BE34D6E0E96613393B4099A07B70875EC5AAB2CE10E8C8289D3E6` | `f661cd9` |

Base verified equal to the installed Phase-1E R1 bytes. `AstraV2` is untouched and NOT part of this phase.

## 2. Staged output

Root: `artifacts/astra-rebuild/stageT4BPOwnerDiag/Scripts/Game/ARMST_T4B/` (git-ignored; not committed).

| Staged file | STAGED_SHA256 | staged blob | delta |
|---|---|---|---|
| `ARMST_T4B_CustomRInputProbe.c` | `54404F6B32D9599E4A4F34D3A3519FC5FC2596FDC476AD7FFA94A0F4BD960202` | `dfbadb3` | +41 / -0 |

Brace/paren: `{ }` 56/56, `( )` 336/336.

## 3. Source evidence for `AnimationControllerComponent`

- `EnfusionScriptAPI/html/interfaceAnimationControllerComponent.html`: class `AnimationControllerComponent`; exposes `proto external int BindAttachment(string attachmentName)` (inherited from `BaseAnimationControllerComponent`).
- `EnfusionScriptAPI/html/interfaceBaseAnimationControllerComponent.html`: `int BindAttachment(string)`, plus `BindAttBoolVariable` / `SetAttBoolVariable` / `GetAttBoolVariable` / `BindAttCommand` / `CallAttCommand` (all unused in this phase).
- `EnfusionScriptAPI/html/interfaceCharacterAnimGraphComponent.html`: `CharacterAnimGraphComponent : BaseAnimationControllerComponent` (also `BindAttachment`).
- `ArmaReforgerScriptAPIPublic/html/interfaceCharacterAnimationComponent.html`: game character animation (BaseAnimPhysComponent) — used only as a presence probe.
- `EnfusionScriptAPI/html/interfaceIEntity.html`: `proto external Managed FindComponent(TypeName)`.
- Core precedent for the exact pattern: `ARMST-PLATFORM---Core/Scripts/Game/MUTANTS/ARMST_MUTANTS_ANIM_COMPONENT.c:31` and `.../AGENT/Components/ARMST_MUTANT_MOVEMENT_COMPONENT.c:143` →
  `AnimationControllerComponent.Cast(owner.FindComponent(AnimationControllerComponent))`.

## 4. Exact log schema

```
[ARMST-T4B-POWNER] phase=owner ok=true|false side=CL|SV
[ARMST-T4B-POWNER] phase=find animController=YES|NO charAnimGraph=YES|NO charAnim=YES|NO
[ARMST-T4B-POWNER] phase=bindAtt owner=animationController binding=Weapon id=<int> valid=YES|NO
[ARMST-T4B-POWNER] phase=bindAtt owner=characterAnimGraph binding=Weapon id=<int> valid=YES|NO   (emitted only if charAnimGraph was found)
```
`phase=owner ok=false reason=no-controlled` if the controlled entity is unavailable.

Interpretation:
- `animController=YES` and `id>=0` → `AnimationControllerComponent` is the script-visible "Weapon" attachment owner → next step is an attachment-variable write probe on it.
- `animController=YES` and `id<0` → the component exists but does not own `"Weapon"`.
- `animController=NO` → owner is not reachable via this class; fall back to a broader (still read-only) enumeration / weapon-side candidate.

## 5. Behaviour

- Added `T4BRTryPOwner(ctrl, side)` and one call site in the non-rack shell branch, immediately after the existing `T4BRTryPact(ctrl, side);`.
- **Read-only:** `BindAttachment("Weapon")` is a lookup/bind diagnostic only; no variable writes, no commands, no graph mutation, no gameplay writers.
- WPROP and PACT code paths are unchanged; the rack path is untouched.

## 6. Forbidden-operation scan (1G delta additions only)

| Pattern | in added lines |
|---|---|
| `SetAttBoolVariable` / `SetBoolVariable` | 0 / 0 |
| `CallAttCommand` / `CallCommand` | 0 / 0 |
| `SetAmmoCount` / `SetReloadWeapon` / `ReloadWeapon(` | 0 / 0 / 0 |
| `BindAttachment` | 2 (permitted lookup) |

(The full staged file still contains the previously reviewed PACT attachment writes; they are unchanged by this phase and are inert on this fixture because the PACT owner — `CharacterAnimGraphComponent` — is runtime-unavailable. The 1G delta itself adds no writes.)

## 7. Inspection A/B procedure (design only — owner executes; no input variant installed)

Goal: isolate ONLY the custom context.
- Same T4B weapon, same graph/ASI/inputs.
- **A** = current custom context active (`ARMST_MP133_ReloadContext`, live `Priority 20000`, owner-local `Flags 0xa 0`).
- **B** = same weapon with the custom context disabled (deactivate `ARMST_MP133_ReloadContext`) or an exact Overlay-only variant (`Flags 0x2 0`).
- Test weapon **inspect** with the user's actual configured inspect input (public references indicate Hold-R near 1.8; the exact packed 1.8.0.13 binding is UNRESOLVED locally — if the profile binding is unreadable, the owner reports the key used). Do **no** reload test in B.
- If inspect works in B but not in A → `INSPECTION_REGRESSION_INPUT_CONTEXT_PROVEN`.
- No graph work either way.

## 8. No-functional-change statement

Only the git-ignored staged scratch was created; live/labs functional files, AGR/AGF/AST/ASI/TXA/ANM, prefab, input/config/keyBindingMenu, `.meta`/GUID, G3B2, production Weapons/Core are byte-identical to HEAD. This report and the plan are the only tracked changes.

---

## 9. COMPLETE unified diff — `ARMST_T4B_CustomRInputProbe.c` (base = installed PACT → staged 1G)

```diff
diff --git "a/ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c" "b/artifacts/astra-rebuild/stageT4BPOwnerDiag/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c"
index f661cd9..dfbadb3 100644
@@ -303,6 +303,8 @@ modded class SCR_PlayerController
 		wcomp.T4BWPropRequest();
 
 		T4BRTryPact(ctrl, side);
+
+		T4BRTryPOwner(ctrl, side);
 	}
 
 	// O1 PHASE 1E PACT — attachment-aware P-side request probe. Animation-only.
@@ -455,6 +457,45 @@ modded class SCR_PlayerController
 			+ " active=" + m_bPactActive.ToString(), LogLevel.NORMAL);
 	}
 
+	// O1 PHASE 1G — READ-ONLY P-owner diagnostic. Enumerates candidate animation
+	// controller owners on the controlled character and, if found, performs a
+	// BindAttachment("Weapon") lookup only. No attachment-variable writes and no
+	// attachment/custom commands are issued; no graph mutation; no gameplay writes.
+	// Diagnostics print [ARMST-T4B-POWNER].
+	protected void T4BRTryPOwner(SCR_CharacterControllerComponent ctrl, string side)
+	{
+		IEntity controlled = null;
+		if (ctrl)
+			controlled = ctrl.GetOwner();
+		if (!controlled)
+		{
+			Print("[ARMST-T4B-POWNER] phase=owner ok=false reason=no-controlled side=" + side, LogLevel.NORMAL);
+			return;
+		}
+		Print("[ARMST-T4B-POWNER] phase=owner ok=true side=" + side, LogLevel.NORMAL);
+
+		AnimationControllerComponent acc = AnimationControllerComponent.Cast(controlled.FindComponent(AnimationControllerComponent));
+		CharacterAnimGraphComponent cagc = CharacterAnimGraphComponent.Cast(controlled.FindComponent(CharacterAnimGraphComponent));
+		CharacterAnimationComponent cac = CharacterAnimationComponent.Cast(controlled.FindComponent(CharacterAnimationComponent));
+
+		Print("[ARMST-T4B-POWNER] phase=find animController=" + (acc != null).ToString()
+			+ " charAnimGraph=" + (cagc != null).ToString()
+			+ " charAnim=" + (cac != null).ToString(), LogLevel.NORMAL);
+
+		int att = -1;
+		if (acc)
+			att = acc.BindAttachment("Weapon");
+		Print("[ARMST-T4B-POWNER] phase=bindAtt owner=animationController binding=Weapon id=" + att.ToString()
+			+ " valid=" + (att >= 0).ToString(), LogLevel.NORMAL);
+
+		if (cagc)
+		{
+			int att2 = cagc.BindAttachment("Weapon");
+			Print("[ARMST-T4B-POWNER] phase=bindAtt owner=characterAnimGraph binding=Weapon id=" + att2.ToString()
+				+ " valid=" + (att2 >= 0).ToString(), LogLevel.NORMAL);
+		}
+	}
+
 	// Custom action callback: logs physical R and dispatches the T4B rack request.
 	protected void T4BRInputDown(float value = 0.0, EActionTrigger reason = 0)
 	{
```

## 10. Required final fields

```
HEAD = d20cbcc8337b50d99ea4025f9185b3601199f51b
REPORT = reports/MP133_TASK1_P_OWNER_RUNTIME_DIAG_STAGE.md
STAGED_FILES = artifacts/astra-rebuild/stageT4BPOwnerDiag/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c (54404F6B32D9599E4A4F34D3A3519FC5FC2596FDC476AD7FFA94A0F4BD960202)
FUNCTIONAL_FILES_CHANGED = NO
GRAPH_CHANGED = NO
INPUT_CONFIG_CHANGED = NO
G3B2_CHANGED = NO
LIVE_CHANGED = NO
WORKBENCH_LAUNCHED = NO
RUNTIME_TEST = NO
```

Final status: **P_OWNER_DIAG_STAGE_READY_OWNER_REVIEW**. STOP (no install, no compile, no runtime).
