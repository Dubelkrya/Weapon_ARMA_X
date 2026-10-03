# CI #29 — separate offline tests from local Weapons/lab integration tests (read-only diagnosis + proposed diff)

**Status:** `CI_ROOT_CAUSE_VERIFIED; DIFF VERIFIED IN ISOLATED COPY; NOT APPLIED`.
Read-only on the working repo. No gameplay/Core/lab/world/GUID/catalog changes; no
Workbench/game. Source: Issue #29 + comment 5968125229.

Working repo was **not modified** (diff applied only to an isolated copy under
`%TEMP%\opencode\mp133_ci_fix`).

---

## CI_ROOT_CAUSE_VERIFIED

1. `agent/scripts/scan_build.py` resolves the live addon **at module import**:
   lines 56–61 call `resolve_addon_root()` and `raise SystemExit(1)` on
   `AddonPathError`. On GitHub-hosted Ubuntu the Windows default addon path does not
   exist → **import-time `SystemExit`**.
   `agent/tests/test_base_game_snapshot_resolver.py` and `test_scanner_regressions.py`
   do `import scan_build` at module level → **2 import errors**; their 7 individual
   tests are never collected, even though all of them use `tempfile` fixtures.
2. `agent/tests/test_mp133_lab_validation.py` `setUp` calls `v.resolve_lab_root()` and
   `v.resolve_original_root()` → `LabValidationError` on hosted CI → **14 failures**
   (its 14 integration cases need the frozen lab + original Weapons addon).
3. The workflow step `python -m unittest discover -s agent/tests -p "test_*.py"` runs
   first and fails, so the later integrity/index/balance/data-quality steps never run.

Reproduced locally in the isolated copy with the addon forced unavailable:
`AddonPathError: an explicitly configured ARMST weapons addon root is invalid …` and
`LabValidationError: lab addon not found …` (same as CI logs).

Downstream scripts were checked: `check_repository_integrity.py`,
`check_data_quality.py`, `build_weapon_index.py`, `build_weapon_family_pages.py`,
`build_balance_pages.py` **do not import `scan_build`/`addon_path`** → once the unittest
stage passes they can run on hosted CI.

---

## Test classification (73 discovered locally)

| File | Class | Needs live addon? | Notes |
|---|---|---|---|
| `test_addon_path.py` | OFFLINE | no | fixtures + env manipulation; clears env in `setUp` |
| `test_balance_report_regressions.py` | OFFLINE | no | reads repo `catalog/` |
| `test_imported_vanilla_reference.py` | OFFLINE | no | `tempfile` fixtures |
| `test_mp133_lab_connect_anims.py` | OFFLINE | no | `tempfile` fixtures |
| `test_mp133_lab_r_gate_model.py` | OFFLINE | no | pure model |
| `test_base_game_snapshot_resolver.py` | OFFLINE (after fix) | no | `tempfile` fixtures; currently **import-fails** |
| `test_scanner_regressions.py` | OFFLINE (after fix) | no | `tempfile`/`parse_text`; currently **import-fails** |
| `test_mp133_lab_validation.py` | **LOCAL-ONLY** | yes (lab + original addon) | 14 integration cases; keep strict locally |

Counts: **73 total**; offline after the fix = **59**; local-gated = **14**.

---

## OFFLINE_TEST_PLAN

With the two-file diff applied, `python -m unittest discover -s agent/tests -p "test_*.py"`
yields **73 tests, 0 failures, 14 skipped, exit 0** when the addon is unavailable
(verified in the isolated copy). The 7 previously-import-error tests now run offline;
the 14 lab tests skip with a clear reason.

## LOCAL_INTEGRATION_PLAN

The lab validation tests stay in the same discovery pattern; locally (addon + lab
present, or with `ARMST_WEAPONS_ADDON_PATH` / `MP133_LAB_ADDON_PATH` /
`MP133_ORIGINAL_ADDON_PATH` set) they run strictly and are **not** skipped. No separate
workflow is required; no assertions are weakened. Documented local command (unchanged):
`python -m unittest discover -s agent/tests -p "test_*.py"` with the env vars set.

---

## PROPOSED_DIFF (exact; NOT applied)

### 1. `agent/scripts/scan_build.py` — lazy addon resolution (import-safe)

```diff
@@
-# Resolved, never assumed. A wrong or missing addon root is a hard error rather
-# than a silently empty catalog written into this repository.
-try:
-    MOD_ROOT = str(resolve_addon_root())
-except AddonPathError as exc:
-    print(f"ERROR: {exc}", file=sys.stderr)
-    raise SystemExit(1)
+# Resolved lazily, never at import time: importing this module (e.g. from an
+# offline unit test) must not require the live addon to be present. A wrong or
+# missing addon root is still a hard error when a scan actually runs.
+def resolve_mod_root() -> str:
+    try:
+        return str(resolve_addon_root())
+    except AddonPathError as exc:
+        print(f"ERROR: {exc}", file=sys.stderr)
+        raise SystemExit(1)
+
+MOD_ROOT = None
@@
 def main():
-    global BASE_GAME_SNAPSHOT
+    global BASE_GAME_SNAPSHOT, MOD_ROOT
 
+    MOD_ROOT = resolve_mod_root()
     print(f"MOD_ROOT   = {MOD_ROOT}")
```

`MOD_ROOT` is consumed only inside `main()` and the functions it calls
(`index_all_files(MOD_ROOT)`, `parse_text_resources(...)` via `parse_file(..., MOD_ROOT)`,
report writers). No test calls those paths, so lazy resolution is safe.

### 2. `agent/tests/test_mp133_lab_validation.py` — clear local-only skip

```diff
@@
     def setUp(self):
-        self.lab = v.resolve_lab_root()
-        self.orig = v.resolve_original_root()
+        try:
+            self.lab = v.resolve_lab_root()
+            self.orig = v.resolve_original_root()
+        except v.LabValidationError as exc:
+            self.skipTest(
+                "LOCAL_ONLY: live Weapons addon / frozen lab not available "
+                f"({exc}); set ARMST_WEAPONS_ADDON_PATH and "
+                "MP133_LAB_ADDON_PATH to run these integration tests"
+            )
```

No workflow change is required. (Optional later: split discovery into
`-p "test_*.py"` offline and an explicit local invocation; not needed for the fix.)

---

## EXPECTED_REMAINING_CHECKS (hosted CI, after the diff)

These should now execute (they do not import `scan_build`/`addon_path`):
`check_repository_integrity.py`; `build_weapon_index.py --check`;
`build_weapon_family_pages.py --check`; `build_balance_pages.py --check`;
`check_data_quality.py --markdown`. **They may still reveal unrelated defects** — not
promising CI PASS. Action-version warnings are out of scope.

## NOT_RUN / evidence

- Hosted GitHub CI: **NOT RUN by the agent** (cannot); the failure log is owner-provided.
- Working repo: **NOT modified** (diff tested only in an isolated copy).
- Locally verified: full discover on the working repo (addon present) → **73 OK**;
  isolated patched copy with addon unavailable → **73, 0 failures, 14 skipped, exit 0**;
  patched scanner without addon → **`ERROR …` exit 1** (hard failure preserved);
  unpatched repo with addon unavailable → reproduced `AddonPathError` + `LabValidationError`.
- `check_repository_integrity.py` locally: **NOT RUN** (jsonschema not installed here;
  the hosted CI installs it).

## STOP criteria

- If the diff makes offline tests require the live addon, weakens assertions, or makes
  `scan_build.main()` stop failing hard without the addon → **STOP, revise**.
- No catalog rescan, no gameplay files, no workflow broadening without separate approval.
