# ARMSTMP133T4B_InstalledMagProbe — published lab sources (T4b)

This directory is the **published copy** of the local isolated lab addon
`...\addons\ARMSTMP133T4B_InstalledMagProbe` (the folder Workbench actually loads).
It is published here (knowledge repo `Dubelkrya/Weapon_ARMA_X`, branch
`t4b/installed-mag-probe`) so the owner can review the exact lab code before a run.

Direction: **MP-133 magazine mechanics** (installed-magazine `+1`, later replenishment
research). Per the owner's branch rule this continues in `t4b/installed-mag-probe`; do
not create a new branch for follow-up T4b steps.

Local copy and this published copy are byte-identical (see `MANIFEST.sha256` and the
SHA references in `reports/MP133_V3_T4B_INSTALLED_MAG_PROBE.md`).

Contents:
- `addon.gproj` — lab project `ARMSTMP133T4BInstalledMag`, GUID `B1C2D3E4F5061728`.
- `Scripts/Game/ARMST_T4B/ARMST_T4B_InstalledMagProbe.c` — `ARMST_T4B_WeaponProbe`
  (installed-magazine baseline + identity) and `ARMST_T4B_AddRoundWeaponAction`
  (weapon-local context action: guarded one-shot `SetAmmoCount(old+1)`).
- `Prefabs/Test/ARMST_T4B_TestWeapon.et` (+ `.meta`) — lab MP-133 copy
  (inherits `{63FF6FDCA4E7E735}Prefabs/Weapons/Russian/Shotgun/armst_Shotgun_mp_133.et`)
  carrying the probe and the action on the inherited `ActionsManagerComponent {A29AE67FF4D82B0F}`.

Boundary: synthetic `+1` on a disposable lab weapon only — no donor, no inventory, no
detach/replace, no production/Core edits. It does not prove authority/replication.
