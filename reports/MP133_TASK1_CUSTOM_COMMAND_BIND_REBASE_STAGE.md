# MP-133 Task #1 — Custom-command bind: rebase stage (Phase 1J rebase)

Status: **CUSTOM_COMMAND_BIND_REBASE_STAGE_READY_OWNER_REVIEW**
Date: 2026-10-08
Task: Issue #34 comment `6046797975` (REBASE 1J STAGE FROM CURRENT LIVE OWNER AGR).
Repo / branch / HEAD: `Dubelkrya/Weapon_ARMA_X` @ `t4b/installed-mag-probe` @ `9a2b8b7dc9164dc025d386c7c5e186dd53b06b72`.
Mode: **SOURCE / STATIC ONLY.** Staged scratch under git-ignored `artifacts/`; nothing installed; no Workbench/runtime; no `git add -f`. Current live AGR is treated as authoritative owner state; the old AGR is not restored.

---

## 1. Fresh live hashes (authoritative owner state)

| Live path | SHA-256 | blob | mtime |
|---|---|---|---|
| `ARMSTMP133T4B_InstalledMagProbe/Assets/MP133_AstraShellGraph_test/MP133_Astra2.agr` | `C55D757EB85A7454DCAE27567CA96980441560805DC0B268B15DBC64ECAF97FF` | `acdb211` | 2026-10-07 23:58:40 |
| `ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c` | `54404F6B32D9599E4A4F34D3A3519FC5FC2596FDC476AD7FFA94A0F4BD960202` | `dfbadb3` | — |

The live AGR was saved by the owner at 23:58:40 (AGR/AGF/AST/ASI share that timestamp).

## 2. Owner AGR delta vs the old baseline (`8E8BAB37…`)

The current live AGR differs from the pre-1J baseline by exactly one additive block:

```diff
diff --git a/.../labs/.../MP133_Astra2.agr b/.../ARMSTMP133T4B_InstalledMagProbe/.../MP133_Astra2.agr
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

`CMD_ASTRA_TransportProbe` count in the live AGR = **1** (no duplicate). ⇒ `OWNER_UI_CHANGE_SAVED_TO_AGR = YES`.

## 3. `Synchronized` serialization evidence

The live AGR `Commands { ... }` block (L73-82) is:

```
  Commands {
   AnimSrcGCTCmd CMD_Weapon_Reload {
   }
   AnimSrcGCTCmd CMD_Weapon_Action_Interrupt {
   }
   AnimSrcGCTCmd CMD_Weapon_Inspection {
   }
   AnimSrcGCTCmd CMD_ASTRA_TransportProbe {
   }
  }
```

- A full scan of the live AGR for any `Sync` token returns **zero** matches.
- All four commands — including `CMD_ASTRA_TransportProbe` — are serialized as **empty `{ }` blocks**, identical in shape to the pre-existing commands.
- Owner UI evidence shows the custom command with `Synchronized = ON`, but the disk serialization contains **no `Synchronized` token** for any command. Per the task, checkbox state is not inferred from an empty block: `Synchronized` is **not present in the AGR text**; whether it is stored elsewhere or is effective-only is **UNRESOLVED**. The staged file preserves the owner's exact bytes (no normalization, no added `Synchronized`).

## 4. Rebase decision

- The live AGR already contains exactly one `CMD_ASTRA_TransportProbe` ⇒ **the AGR is owner-complete and does NOT need staging.** It is not restored, not overwritten, not normalized.
- The live CustomR controller (`54404F6B…`) is still the Phase-1G bytes and does **not** yet contain the reviewed 1J CMDBIND diagnostic ⇒ the rebased candidate consists of **only** the CustomR diagnostic delta.

Staged (git-ignored): `artifacts/astra-rebuild/stageCustomCommandBindRebase/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c`
= current live CustomR + the same read-only CMDBIND logic reviewed in Phase 1J.
SHA-256 = `9ADD4AD9979382AC6B42F88209A47A11A29EB6038BE832F13D3B3EF4AA628249` (blob `59be53d`).

No AGR file is staged.

## 5. Proofs

| Check | Result |
|---|---|
| `CMD_ASTRA_TransportProbe` declarations total (live AGR) | 1 |
| Duplicate command declaration | NO |
| Staged AGR change | NONE (owner-complete) |
| `CMD_ASTRA_TransportProbe` in staged CustomR | 2 occurrences = 2 `BindCommand` calls (registration only; no declaration) |
| `CallCommand` / `CallCommand4I` / `PreAnim_CallCommand` in delta | 0 / 0 / 0 |
| `SetAtt*` / `SetBoolVariable` / `SetVariable` in delta | 0 / 0 / 0 |
| `SetAmmoCount` / `SetReloadWeapon` / `TryUseItem*` in delta | 0 / 0 / 0 |
| `BindCommand` in delta | 4 call sites (registration/controls only) |
| AGF/ASI/AST/TXA/ANM/prefab/input change | NONE |
| Braces/parens (staged CustomR) | 58/58, 369/369 |

Effective injection settings (unchanged, no prefab edit): `BindWithInjection ON`, `AutoCommandBind ON`, `AutoVariablesBind OFF`, `AnimVariablesToBind=[WeaponInspectionState]`; `AnimCommandsToBind` not observed (UNRESOLVED).

## 6. Complete current-live → rebased-stage diff (CustomR only)

```diff
diff --git "a/ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c" "b/artifacts/astra-rebuild/stageCustomCommandBindRebase/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c"
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

## 7. No-functional-change statement

No functional file changed by the agent. Live AGR and live CustomR are byte-identical to their pre-task hashes; the staged candidate lives only in git-ignored scratch. `.meta`/GUID, AGF/AST/ASI/TXA/ANM, prefab, input/config/keyBinding, G3B2, production Weapons/Core are untouched. Only this report (and an optional plan update) are committed.

## 8. Required final fields

```
CUSTOM_COMMAND_BIND_REBASE_STAGE_READY_OWNER_REVIEW
HEAD = 9a2b8b7dc9164dc025d386c7c5e186dd53b06b72
OWNER_UI_CHANGE_SAVED_TO_AGR = YES
LIVE_AGR_SHA256 = C55D757EB85A7454DCAE27567CA96980441560805DC0B268B15DBC64ECAF97FF
LIVE_CUSTOMR_SHA256 = 54404F6B32D9599E4A4F34D3A3519FC5FC2596FDC476AD7FFA94A0F4BD960202
STAGED_FILES = artifacts/astra-rebuild/stageCustomCommandBindRebase/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c
STAGED_SHA256 = 9ADD4AD9979382AC6B42F88209A47A11A29EB6038BE832F13D3B3EF4AA628249
CUSTOM_COMMAND_DECLARATIONS_TOTAL = 1
DUPLICATE_COMMAND_DECLARATION = NO
CALLCOMMAND_CALLS = 0
ITEM_USE_CALLS = 0
GAMEPLAY_WRITERS_ADDED = 0
LIVE_CHANGED_BY_AGENT = NO
WORKBENCH_LAUNCHED_BY_AGENT = NO
RUNTIME_TEST = NO
```

STOP before install.
