param(
 [ValidateSet('Server','Client')][string]$Role='Client',
 [ValidateSet('ARMST','SoundsOnly')][string]$Test='ARMST',
 [string]$ServerExecutable,
 [ValidateRange(1,8)][int]$ClientNumber=1,
 [switch]$PromptAdminPassword,
 [switch]$MatchClientDiagDefines,
 [switch]$UseClientExeForServer,
 [switch]$DryRun
)
$ErrorActionPreference='Stop'
# For the paired test, pass MatchClientDiagDefines to BOTH processes so the
# explicit define list (including its order) is identical. Does not bypass CRC.
if($UseClientExeForServer -and ($Role -ne 'Server' -or $MatchClientDiagDefines -or $ServerExecutable)){throw 'UseClientExeForServer requires Role Server and no extra defines or ServerExecutable.'}
$gameRoot='C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger'
$localAddons='C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons'
$workshopAddons='C:\Users\yshky\Documents\My Games\ArmaReforger\addons'
$project=Join-Path $gameRoot 'addons\data\ArmaReforger.gproj'
$world='worlds/MP/MpTest/MP_test.ent'
# Core declares Weapons and required gameplay dependencies. Do not select both
# local and published MOVehicles by their shared project ID.
$mods='69E4C3542B6CDC19'
$addonSearchPaths=(Join-Path $gameRoot 'addons')+','+$localAddons+','+$workshopAddons
if($Test -eq 'SoundsOnly') {
 $mods='6A8EE94F15EF61E0'
 $addonSearchPaths=(Join-Path $gameRoot 'addons')+','+$workshopAddons
 $world='worlds/Tests/TestFramework/Autotest_GameMode_Plain.ent'
}
if($Role -eq 'Server') {
 if($UseClientExeForServer) {
  $exe=Join-Path $gameRoot 'ArmaReforgerSteamDiag.exe'
 } else {
 if(!$ServerExecutable) {throw 'Provide the actual full path using -ServerExecutable. No process started.'}
 $exe=$ServerExecutable
 if((Split-Path $exe -Leaf) -notin @('ArmaReforgerServer.exe','ArmaReforgerServerDiag.exe')) {throw 'Not a server executable.'}
 }
 $profileName='ARMST_Shotgun_DirectServer_'+$Test
} else {
 $exe=Join-Path $gameRoot 'ArmaReforgerSteamDiag.exe'
 $profileName='ARMST_Shotgun_DirectClient_'+$Test+'_'+$ClientNumber
}
foreach($required in @($exe,$project,$localAddons,$workshopAddons)) {
 if(!(Test-Path -LiteralPath $required)){throw ('Missing: '+$required)}
}
function Quote-Argument([string]$value) {
 if($value.Contains('"') -or $value.EndsWith('\')){throw 'Unsupported argument quoting.'}
 return '"'+$value+'"'
}
$arguments='-gproj '+(Quote-Argument $project)
$arguments+=' -addonsDir '+(Quote-Argument $addonSearchPaths)
$arguments+=' -addons '+(Quote-Argument $mods)+' -profile '+(Quote-Argument $profileName)
if($Role -eq 'Server') {$arguments+=' -server '+(Quote-Argument $world)+' -maxFPS 30'}
else {$arguments+=' -client 127.0.0.1 -window -forceupdate -nofocus'}
if($MatchClientDiagDefines){$arguments+=' -scrDefine ENABLE_DIAG -scrDefine GAME_MODE_DEBUG'}
Write-Output ('Executable: '+$exe)
Write-Output ('Arguments: '+$arguments)
Write-Output ('Logs: C:\Users\yshky\Documents\My Games\'+$profileName+'\logs')
if($DryRun){return}
if($PromptAdminPassword) {
 if($Role -ne 'Server'){throw 'Admin password belongs to Server, not Client.'}
 $adminSecureValue=Read-Host 'Temporary test server admin password (do not reuse a real password)' -AsSecureString
 $adminPointer=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($adminSecureValue)
 try {
  $adminPlainValue=[Runtime.InteropServices.Marshal]::PtrToStringBSTR($adminPointer)
  if([string]::IsNullOrWhiteSpace($adminPlainValue)){throw 'Empty admin password.'}
  $arguments+=' -adminPassword '+(Quote-Argument $adminPlainValue)
 } finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($adminPointer)
  $adminPlainValue=$null
  $adminSecureValue.Dispose()
 }
 # Never print the final arguments: they contain the password.
 # The engine may still record it in console.log / process command line.
}
if($Role -eq 'Server') {
 $process=Start-Process -FilePath $exe -ArgumentList $arguments -WorkingDirectory (Split-Path $exe -Parent) -WindowStyle Hidden -PassThru
} else {
 $process=Start-Process -FilePath $exe -ArgumentList $arguments -WorkingDirectory (Split-Path $exe -Parent) -PassThru
}
Write-Output ('Started PID: '+$process.Id+'. Stop only this process after testing.')
