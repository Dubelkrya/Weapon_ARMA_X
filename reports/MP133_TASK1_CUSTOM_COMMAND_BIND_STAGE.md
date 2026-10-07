# MP-133 Task #1 — Injected-only custom-command bind probe (Phase 1J, stage only)

Status: **CUSTOM_COMMAND_BIND_STAGE_READY_OWNER_REVIEW**
Date: 2026-10-07
Task: Issue #34 comment `6046517253` (INJECTED_ONLY_CUSTOM_COMMAND_BIND_STAGE).
Repo / branch / HEAD: `Dubelkrya/Weapon_ARMA_X` @ `t4b/installed-mag-probe` @ `fcb38ce6066114ba72bc824ca1d0e3ebb9d080d5`.
Mode: **SOURCE / STATIC ONLY.** Staged scratch under git-ignored `artifacts/`; nothing installed; no Workbench/runtime; no `git add -f`. Functional baseline = CURRENT INSTALLED live resources (not older tracked labs).

---

## 1. Live functional baseline (source of the staged candidates)

| Live path | SHA-256 | blob |
|---|---|---|
| `ARMSTMP133T4B_InstalledMagProbe/Assets/MP133_AstraShellGraph_test/MP133_Astra2.agr` | `8E8BAB3771E0691F5A116AB917A1F506E407245C6CC7E5C8B1DF1ECFCB730FF2` | `fffcefa` |
| `ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c` | `54404F6B32D9599E4A4F34D3A3519FC5FC2596FDC476AD7FFA94A0F4BD960202` | `dfbadb3` |

(The live AstraV2 component — `241E6EC1…` — is NOT part of this phase and is untouched; its read-only PATT probe is preserved.)

## 2. Staged output

Root: `artifacts/astra-rebuild/stageCustomCommandBind/` (git-ignored; not committed).

| Staged path | SHA-256 | blob |
|---|---|---|
| `Assets/MP133_AstraShellGraph_test/MP133_Astra2.agr` | `C55D757EB85A7454DCAE27567CA96980441560805DC0B268B15DBC64ECAF97FF` | `acdb211` |
| `Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c` | `9ADD4AD9979382AC6B42F88209A47A11A29EB6038BE832F13D3B3EF4AA628249` | `59be53d` |

Brace/paren: AGR delta is a 2-line block; CustomR `{ }` 58/58, `( )` 369/369.

## 3. Why each functional file is necessary

- **Astra AGR** — the only place to declare the inert command name so that the injected graph's control template (shared by W and P instances) contains `CMD_ASTRA_TransportProbe`. Declaration only; no AGF consumer.
- **CustomR controller** — the only current live lifecycle point that has (a) the proven character getter chain (`SCR_CharacterControllerComponent.GetAnimationComponent()`), (b) the equipped AstraV2 weapon component, and (c) a guaranteed **post-injection** one-shot transition (`weapon_gate_pass`: local player + current weapon is the T4B probe). No new polling/timers/input.

## 4. Exact command declaration delta (AGR)

Added inside the existing `Commands { ... }` control-template block:
```
   AnimSrcGCTCmd CMD_ASTRA_TransportProbe {
   }
```
No AGF transition, no AGC consumer, no ASI/AST/TXA/ANM change, no root/Core declaration.

## 5. Exact diagnostic trigger / lifecycle point

`T4BRMaintainContext()` → immediately after the existing one-shot `[ARMST-T4B-RCTX] phase=weapon_gate_pass` (reached only when the local controlled entity's current weapon carries `ARMST_T4B_WeaponProbe` = the canonical T4B weapon = **post-injection**). One-shot via `m_bCmdBindLogged`; no per-frame logging, no timers, no input, no R press required.

Binds performed (registration/addressability only, never called):
- weapon side: `wcomp.BindCommand("CMD_ASTRA_TransportProbe")` on the equipped `ARMST_T4B_AstraV2_WeaponAnimationComponent`;
- character side: `charAnim.BindCommand("CMD_ASTRA_TransportProbe")`;
- positive control: `charAnim.BindCommand("CMD_Weapon_Reload")` (already-declared, never called);
- negative control: `charAnim.BindCommand("CMD_ASTRA_AbsentProbe_ZZZ")` (deliberately absent, never called).

Log schema:
```
[ARMST-T4B-CMDBIND] phase=post actorPresent=<0|1> weaponPresent=<0|1> customW=<int> customCharValid=<0|1|NA> rootCtlValid=<0|1|NA> absentValid=<0|1|NA>
```
(`customW` is an `int` from `BaseAnimationControllerComponent.BindCommand`; character-side results are `TAnimGraphCommand` from `BaseAnimPhysComponent.BindCommand` and are logged as validity booleans because `TAnimGraphCommand` has no `.ToString()` in this SDK — same constraint documented in Phase 2C.)

## 6. Proofs

- **Command calls = 0.** 1J delta additions contain `CallCommand` = 0, `CallCommand4I` = 0, `PreAnim_CallCommand` = 0.
- **Gameplay writers = 0.** 1J delta additions contain `SetAtt*` = 0, `SetBoolVariable` = 0, `SetVariable` = 0, `SetAmmoCount` = 0, `SetReloadWeapon` = 0, `TryUseItem*` = 0; no mag/chamber/ammo/entity writes. `BindCommand` = 4 call sites (registration only).
- No `AutoVariablesBind`/`AutoCommandBind`/prefab/input change; no `.meta`/GUID change.

## 7. Effective injection-setting evidence

Owner Workbench effective state (OWNER_WORKBENCH_EVIDENCE): `BindWithInjection = ON`, `AutoCommandBind = ON`, `AutoVariablesBind = OFF`, `AnimVariablesToBind = [WeaponInspectionState]`.
- `BindWithInjection` is serialized in the lab prefab (`1`).
- `AutoCommandBind` / `AutoVariablesBind` / `AnimVariablesToBind` are effective defaults (not serialized in T4B/production/base prefabs) — engine defaults.
- **`AnimCommandsToBind`**: not observed in the effective UI and not present in any local `.et` → its existence/effective value is **UNRESOLVED**; not fabricated, and no prefab setting was edited to force the experiment.

## 8. Expected interpretations (runtime, NOT authorized here)

| Observation | Interpretation |
|---|---|
| `customCharValid=1`, `rootCtlValid=1`, `absentValid=0` | custom command IS addressable on the character side after injection → dual/custom command route viable (next: separate consumer/emitter design) |
| `customW>=0`, `customCharValid=0` | command registered in the weapon graph only, not addressable from the character side → no dual route via this name |
| `customCharValid == absentValid` | the bind API does not meaningfully distinguish an existing name from an absent one → inconclusive |
| `rootCtlValid == customCharValid == absentValid` (all same) | inconclusive; the probe cannot certify registration |
| `rootCtlValid=0` | positive control failed → controls inconclusive regardless of custom results |
| no `phase=post` line | lifecycle point not reached (weapon not current / no local player) → no data |

**Pre-injection half:** a true pre-injection observation is not safely obtainable from this lifecycle point without invasive work; this stage provides **post-injection only** and the missing pre half is classified as a **limitation** (not faked).

## 9. No-functional-change statement

No functional file changed. Live addon, committed labs, `.et.meta`, GUIDs, AGR (live), AGF/AST/ASI/TXA/ANM, prefab, scripts, input/config/keyBinding, G3B2, production Weapons/Core, `resourceDatabase.rdb` are byte-identical. Only this report (and an optional plan update) are committed.

---

## 10. COMPLETE unified diff — AGR (live → staged)

```diff
diff --git "a/ARMSTMP133T4B_InstalledMagProbe/Assets/MP133_AstraShellGraph_test/MP133_Astra2.agr" "b/artifacts/astra-rebuild/stageCustomCommandBind/Assets/MP133_AstraShellGraph_test/MP133_Astra2.agr"
index fffcefa..acdb211 100644
@@ -77,6 +77,8 @@ AnimSrcGraph {
    }
    AnimSrcGCTCmd CMD_Weapon_Inspection {
    }
+   AnimSrcGCTCmd CMD_ASTRA_TransportProbe {
+   }
   }
   IkChains {
    AnimSrcGCTIkChain LeftArm {
```

## 11. COMPLETE unified diff — CustomR controller (live → staged)

```diff
diff --git "a/ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c" "b/artifacts/astra-rebuild/stageCustomCommandBind/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c"
index dfbadb3..59be53d 100644
@@ -73,6 +73,9 @@ modded class SCR_PlayerController
 	protected int m_iPactSession;
 	protected bool m_bPactActive;
 
+	// O1 PHASE 1J CMDBIND probe one-shot gate.
+	protected bool m_bCmdBindLogged;
+
 	override void OnUpdate(float timeSlice)
 	{
 		super.OnUpdate(timeSlice);
@@ -144,6 +147,8 @@ modded class SCR_PlayerController
 			Print("[ARMST-T4B-RCTX] phase=weapon_gate_pass", LogLevel.NORMAL);
 		}
 
+		T4BCmdBindProbe(ctrl, we);
+
 		InputManager im = GetGame().GetInputManager();
 		if (!im)
 			return;
@@ -496,6 +501,51 @@ modded class SCR_PlayerController
 		}
 	}
 
+	// O1 PHASE 1J - injected-only custom-command bind probe. REGISTRATION/ADDRESSABILITY
+	// ONLY: binds one inert command name on the character animation component and on the
+	// equipped AstraV2 weapon animation component, plus one known positive control
+	// (CMD_Weapon_Reload) and one deliberately absent negative control. No command calls,
+	// no setters, no WPROP request, no gameplay writes. Diagnostics print [ARMST-T4B-CMDBIND].
+	protected void T4BCmdBindProbe(SCR_CharacterControllerComponent ctrl, IEntity weaponEntity)
+	{
+		if (m_bCmdBindLogged)
+			return;
+		m_bCmdBindLogged = true;
+
+		CharacterAnimationComponent charAnim = null;
+		if (ctrl)
+			charAnim = ctrl.GetAnimationComponent();
+
+		ARMST_T4B_AstraV2_WeaponAnimationComponent wcomp = null;
+		if (weaponEntity)
+			wcomp = ARMST_T4B_AstraV2_WeaponAnimationComponent.Cast(weaponEntity.FindComponent(ARMST_T4B_AstraV2_WeaponAnimationComponent));
+
+		int customW = -99;
+		if (wcomp)
+			customW = wcomp.BindCommand("CMD_ASTRA_TransportProbe");
+
+		if (!charAnim)
+		{
+			Print("[ARMST-T4B-CMDBIND] phase=post actorPresent=" + (ctrl != null).ToString()
+				+ " weaponPresent=" + (wcomp != null).ToString()
+				+ " customW=" + customW.ToString()
+				+ " customCharValid=NA rootCtlValid=NA absentValid=NA", LogLevel.NORMAL);
+			return;
+		}
+
+		// Character side: BaseAnimPhysComponent.BindCommand -> TAnimGraphCommand.
+		TAnimGraphCommand customChar = charAnim.BindCommand("CMD_ASTRA_TransportProbe");
+		TAnimGraphCommand rootCtl = charAnim.BindCommand("CMD_Weapon_Reload");
+		TAnimGraphCommand absent = charAnim.BindCommand("CMD_ASTRA_AbsentProbe_ZZZ");
+
+		Print("[ARMST-T4B-CMDBIND] phase=post actorPresent=" + (ctrl != null).ToString()
+			+ " weaponPresent=" + (wcomp != null).ToString()
+			+ " customW=" + customW.ToString()
+			+ " customCharValid=" + (customChar >= 0).ToString()
+			+ " rootCtlValid=" + (rootCtl >= 0).ToString()
+			+ " absentValid=" + (absent >= 0).ToString(), LogLevel.NORMAL);
+	}
+
 	// Custom action callback: logs physical R and dispatches the T4B rack request.
 	protected void T4BRInputDown(float value = 0.0, EActionTrigger reason = 0)
 	{
```

## 12. Required final fields

```
CUSTOM_COMMAND_BIND_STAGE_READY_OWNER_REVIEW
HEAD = fcb38ce6066114ba72bc824ca1d0e3ebb9d080d5
LIVE_BASELINE_FILES = Assets/MP133_AstraShellGraph_test/MP133_Astra2.agr ; Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c
LIVE_BASELINE_SHA256 = 8E8BAB3771E0691F5A116AB917A1F506E407245C6CC7E5C8B1DF1ECFCB730FF2 ; 54404F6B32D9599E4A4F34D3A3519FC5FC2596FDC476AD7FFA94A0F4BD960202
STAGED_FILES = Assets/MP133_AstraShellGraph_test/MP133_Astra2.agr ; Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c
STAGED_SHA256 = C55D757EB85A7454DCAE27567CA96980441560805DC0B268B15DBC64ECAF97FF ; 9ADD4AD9979382AC6B42F88209A47A11A29EB6038BE832F13D3B3EF4AA628249
CUSTOM_COMMAND_DECLARATIONS_ADDED = 1
COMMAND_CONSUMERS_ADDED = 0
CALLCOMMAND_CALLS = 0
ITEM_USE_CALLS = 0
GAMEPLAY_WRITERS_ADDED = 0
GRAPH_AGF_CHANGED = NO
ASI_CHANGED = NO
AST_CHANGED = NO
TXA_CHANGED = NO
ANM_CHANGED = NO
PREFAB_CHANGED = NO
INPUT_CHANGED = NO
G3B2_CHANGED = NO
LIVE_CHANGED = NO
WORKBENCH_LAUNCHED = NO
RUNTIME_TEST = NO
```

STOP before install.
