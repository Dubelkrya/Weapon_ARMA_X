# ARMSTMP133T4A_SetProbe — historical diagnostic snapshot (T4a)

This directory is a **published snapshot** of the local isolated lab
`...\addons\ARMSTMP133T4A_SetProbe`, published for review in the knowledge repo
(`Dubelkrya/Weapon_ARMA_X`, branch `t4b/installed-mag-probe`).

It is the **historical diagnostic** for the **disposable**-magazine `SetAmmoCount` API test
(T4a): a disposable test magazine prefab carrying a `ScriptedUserAction`
("T4a: add 1 test round") added to the magazine's **inherited** `ActionsManagerComponent`
(`{F092E6B0537754FD}`) via `additionalActions +{ … ParentContextList { "default" } UIInfo … }`,
with one guarded `SetAmmoCount(+1)`.

Notes:
- Same **MP-133 magazine direction** as T4b. This is a snapshot only: it is **not** merged from
  the `t4a/interaction-patch` branch, and the local T4a lab is **unchanged**.
- It is **not** used by the T4b installed-magazine probe and is not a gameplay feature.
- The T4a `+1` action/context was never verified in game; T4b supersedes it as the active
  line of work.
- Local copy and this published copy are byte-identical (see `MANIFEST.sha256`).
