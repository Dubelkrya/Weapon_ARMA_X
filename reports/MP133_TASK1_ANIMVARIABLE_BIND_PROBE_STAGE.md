# MP-133 Task #1 — AnimVariable bind probe (Phase 1I, stage only)

Status: **ANIMVARIABLE_BIND_PROBE_STAGE_READY_OWNER_REVIEW**
Date: 2026-10-07
Task: Issue #34 comment `6044652747` (Phase 1I — prefab variable-bind probe, stage only).
Repo / branch / HEAD: `Dubelkrya/Weapon_ARMA_X` @ `t4b/installed-mag-probe` @ `b127eaec4b8c640c71e30dc44922c7697e19a29e`.
Mode: **SOURCE / STATIC ONLY.** Staged scratch under git-ignored `artifacts/`; nothing installed; no Workbench/runtime; no `git add -f`.

---

## 1. Baseline (target source prefab)

| File | SHA-256 | blob |
|---|---|---|
| `labs/ARMSTMP133T4B_InstalledMagProbe/Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et` | `F4A856D8452136C13033B893A1F72E72C1D0D99AF204E782726A66853BCC43F4` | `56ce7f1` |

Live copy of the same prefab is byte-identical (`F4A856D8…`). Labs has no `.meta`; the live `.meta` (GUID identity) is NOT part of this phase.

## 2. Staged output

Root: `artifacts/astra-rebuild/stageAnimVariableBind/Prefabs/Test/` (git-ignored; not committed).

| Staged file | STAGED_SHA256 | staged blob |
|---|---|---|
| `ARMST_T4B_AstraRebuild_TestWeapon.et` | `9960A92E9A31C9F2DDC69164F8D68ED673FE5481792E30E365DFE44DFE531AF1` | `dd549db` |

Brace balance `{ }` 19/19; size 1110 B (base 970 B). Delta = +6 lines (one additive array).

## 3. Exact intended change

Added only inside the existing `ARMST_T4B_AstraV2_WeaponAnimationComponent "{60B4EA76EB15F6E0}"` block, after `BindWithInjection 1`:
```
     AnimVariablesToBind +{
      "ASTRA_ShellRequest"
      "ASTRA_ShellEligible"
      "ASTRA_ShellRepeat"
      "ASTRA_ShellStop"
     }
```
`+{` keeps any inherited/effective entries (e.g. `WeaponInspectionState`) intact; nothing is replaced.

## 4. Validation (preservation proofs)

| Check | Result |
|---|---|
| `WeaponInspectionState` present / replaced | 0 (not serialized — default preserved) |
| `AutoVariablesBind` / `AutoCommandBind` changed | 0 / 0 |
| `ASTRA_FireStop` added | 0 |
| `AnimGraph` occurrences (W + injection) | 2 (unchanged) |
| `AnimInstance` occurrences (W + P) | 2 (unchanged) |
| `BindingName "Weapon"` | 1 (unchanged) |
| `BindWithInjection 1` | 1 (unchanged) |
| Tube3 `MagazineTemplate` | 1 (unchanged) |
| object IDs / GUIDs / `.meta` | untouched (only the `.et` staged; no `.meta`) |
| braces | 19/19 |

Everything else is byte-for-byte identical to the baseline prefab.

## 5. Unchanged / boundaries

No functional file changed. Live addon, committed labs prefab, `.et.meta`, GUIDs, AGR/AGF/AST/ASI/TXA/ANM, scripts, input/config/keyBinding, G3B2, production Weapons/Core, `resourceDatabase.rdb` are byte-identical. Only this report (and an optional plan update) are committed.

---

## 6. COMPLETE unified diff (baseline labs prefab → staged)

```diff
diff --git "a/labs/ARMSTMP133T4B_InstalledMagProbe/Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et" "b/artifacts/astra-rebuild/stageAnimVariableBind/Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et"
index 56ce7f1..dd549db 100644
@@ -18,6 +18,12 @@ GenericEntity : "{63FF6FDCA4E7E735}Prefabs/Weapons/Russian/Shotgun/armst_Shotgun
       BindingName "Weapon"
      }
      BindWithInjection 1
+     AnimVariablesToBind +{
+      "ASTRA_ShellRequest"
+      "ASTRA_ShellEligible"
+      "ASTRA_ShellRepeat"
+      "ASTRA_ShellStop"
+     }
     }
    }
   }
```

## 7. Future runtime success criterion (NOT AUTHORIZED HERE)

After separate review/install/compile GO, one qualified shell-R:
- PASS: `W family = YES`, `P family = YES`, `sawP=true`, P markers observed, no gameplay mutation.
- FAIL: `W family = YES`, `P family = NO` → W→P propagation through this explicit variable-binding direction disproven; a different bridge is required.

Inspection A/B, G3B2 and graph edits remain HOLD.

## 8. Required final fields

```
ANIMVARIABLE_BIND_PROBE_STAGE_READY_OWNER_REVIEW
HEAD = b127eaec4b8c640c71e30dc44922c7697e19a29e
BASE_PREFAB_SHA256 = F4A856D8452136C13033B893A1F72E72C1D0D99AF204E782726A66853BCC43F4
STAGED_PREFAB_SHA256 = 9960A92E9A31C9F2DDC69164F8D68ED673FE5481792E30E365DFE44DFE531AF1
STAGED_FILE = artifacts/astra-rebuild/stageAnimVariableBind/Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et
DIFF_LINES = 17
FUNCTIONAL_FILES_CHANGED = NO
LIVE_CHANGED = NO
PREFAB_COMMITTED_CHANGED = NO
GRAPH_CHANGED = NO
SCRIPT_CHANGED = NO
INPUT_CONFIG_CHANGED = NO
META_CHANGED = NO
GUID_CHANGED = NO
G3B2_CHANGED = NO
WORKBENCH_LAUNCHED = NO
RUNTIME_TEST = NO
```

STOP before installation.
