@echo off
setlocal EnableExtensions

rem Resolver v2 one-click launcher.
rem ARMST is the frozen source snapshot for this catalog. Resolver v2 must use
rem only resources that physically exist inside the ARMST addon.
rem Current vanilla / Imported\VanillaSources are intentionally NOT consulted.
rem Override ARMST_ROOT / PYTHON before running if needed.

set "REPO_ROOT=%~dp0.."
if not defined PYTHON set "PYTHON=python"
if not defined ARMST_ROOT set "ARMST_ROOT=C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons"
set "OUTPUT_ROOT=%REPO_ROOT%\agent\v2_output"

rem Guard against inherited shell environment accidentally re-enabling vanilla roots.
set "VANILLA_ROOTS="
set "VANILLA_ROOT="

if not exist "%ARMST_ROOT%" (
  echo [resolver-v2] ARMST root not found:
  echo   %ARMST_ROOT%
  echo Set ARMST_ROOT and run this file again.
  exit /b 2
)

pushd "%REPO_ROOT%" || exit /b 4

echo [resolver-v2] Source policy: ARMST ONLY
echo [resolver-v2] ARMST:  %ARMST_ROOT%
echo [resolver-v2] Output: %OUTPUT_ROOT%
echo.

%PYTHON% agent\scripts\scan_build_v2.py ^
  --armst-root "%ARMST_ROOT%" ^
  --repo-root "%REPO_ROOT%" ^
  --output-root "%OUTPUT_ROOT%"
if errorlevel 1 goto :scan_failed

%PYTHON% agent\scripts\reference_cases_v2.py --output-root "%OUTPUT_ROOT%"
if errorlevel 1 goto :reference_failed

%PYTHON% agent\scripts\diagnose_unresolved_v2.py ^
  --repo-root "%REPO_ROOT%" ^
  --armst-root "%ARMST_ROOT%" ^
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
echo Source policy: ARMST only. Missing external resources are not filled from vanilla.
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
