// ============================================================================
// ARMST MP-133 T4b - Task #1, A/B VARIANT: NO global reload-handler override.
// (STAGED, source prep only.)
//
// Purpose of the A/B: determine whether the mere presence of the T4B
// `modded SCR_CharacterCommandHandlerComponent.HandleWeaponReloading` override
// breaks the native rack, even when its rack branch returns `super`.
//
// This file therefore contains NO `modded class` and NO `HandleWeaponReloading`
// override at all. It keeps ONLY the two shared constants required by the
// weapon-local observer (`ARMST_T4B_AstraV2_WeaponAnimationComponent`), which are
// inert and cannot affect input/reload flow.
//
// Base (current live handler): SHA-256
//   83DA1EC584B13D251359B776D2C05AEE41E07A42ACB3334389814C0501BA8B39
//
// Not done here (by design): no replacement global handler, no
// HandleWeaponReloadingDefault call, no Update/HandleWeapons, no ammo/mag/chamber
// writers, no timers/polling.
// ============================================================================
// Shared inert reload-command value (kept for the weapon-local observer).
const int ARMST_T4B_INERT_RELOAD_CMD = 10;

// Reload command TYPE id (kept for the weapon-local observer). Evidence: T2c owner
// runtime observed commandID=0 for the reload command. The observer proves the route
// ONLY when commandID == this AND intValue == ARMST_T4B_INERT_RELOAD_CMD.
const int ARMST_T4B_RELOAD_COMMAND_ID = 0;
