@echo off
setlocal EnableExtensions

rem Resolver v2 one-click launcher.
rem ARMST is the editable mod source. Materialized vanilla is READ-ONLY resolver
rem context for inherited/base resources that ARMST still references.
rem Never edit Imported\VanillaSources; all game-resource edits belong in ARMST.
rem Override ARMST_ROOT / VANILLA_ROOT / PYTHON before running if needed.

set "REPO_ROOT=%~dp0.."
if not defined PYTHON set "PYTHON=python"
if not defined ARMST_ROOT set "ARMST_ROOT=C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons"
if not defined VANILLA_ROOT set "VANILLA_ROOT=%REPO_ROOT%\Imported\VanillaSources"
set "OUTPUT_ROOT=%REPO_ROOT%\agent\v2_output"

if not exist "%ARMST_ROOT%" (
  echo [resolver-v2] ARMST root not found:
  echo   %ARMST_ROOT%
  echo Set ARMST_ROOT and run this file again.
  exit /b 2
)

if not exist "%VANILLA_ROOT%" (
  echo [resolver-v2] Read-only materialized vanilla root not found:
  echo   %VANILLA_ROOT%
  echo.
  echo Open Weapon_ARMA_X in Arma Reforger Workbench and run:
  echo   WAX: Materialize Vanilla Weapon Dataset
  echo.
  echo This vanilla copy is resolver evidence only. Do NOT edit it.
  exit /b 3
)

pushd "%REPO_ROOT%" || exit /b 4

echo [resolver-v2] Source policy: ARMST editable + vanilla read-only inheritance
 echo [resolver-v2] ARMST:                %ARMST_ROOT%
echo [resolver-v2] Vanilla read-only:     %VANILLA_ROOT%
echo [resolver-v2] Output:               %OUTPUT_ROOT%
echo.

%PYTHON% agent\scripts\scan_build_v2.py ^
  --armst-root "%ARMST_ROOT%" ^
  --vanilla-root "materialized_base=%VANILLA_ROOT%" ^
  --repo-root "%REPO_ROOT%" ^
  --output-root "%OUTPUT_ROOT%"
if errorlevel 1 goto :scan_failed

%PYTHON% agent\scripts\reference_cases_v2.py --output-root "%OUTPUT_ROOT%"
if errorlevel 1 goto :reference_failed

%PYTHON% agent\scripts\diagnose_unresolved_v2.py ^
  --repo-root "%REPO_ROOT%" ^
  --armst-root "%ARMST_ROOT%" ^
  --vanilla-root "%VANILLA_ROOT%" ^
  --output-root "%OUTPUT_ROOT%"
if errorlevel 1 goto :diagnostic_failed

echo.
echo [resolver-v2] SUCCESS
echo Reports:
echo   %OUTPUT_ROOT%\reports\scan_summary_v2.json
echo   %OUTPUT_ROOT%\reports\resolver_v2_diff.json
echo   %OUTPUT_ROOT%\reports\anomalies_v2.json
echo   %OUTPUT_ROOT%\reports\reference_cases_v2.json
echo   %OUTPUT_ROOT%\reports\diagnostics_v2.json
echo.
echo Policy: read both ARMST and vanilla, but edit ARMST only.
echo Send the reports back for review before merging PR #2.
popd
exit /b 0

:scan_failed
echo.
echo [resolver-v2] Scan failed. No legacy catalog was overwritten.
popd
exit /b 10

:reference_failed
echo.
echo [resolver-v2] Scan finished, but no configured reference cases were found.
echo Review %OUTPUT_ROOT%\reports\scan_summary_v2.json first.
popd
exit /b 11

:diagnostic_failed
echo.
echo [resolver-v2] Scan/reference reports finished, but unresolved diagnostics failed.
echo Existing reports remain valid under %OUTPUT_ROOT%\reports.
popd
exit /b 12
