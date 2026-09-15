// Scripts/Gamecode/AttachmentOpticsARMST.c
//
// ARMST gameplay compatibility types for weapon optics.
//
// IMPORTANT:
// - These classes define attachment compatibility only.
// - Real-world compatibility is documented separately.
// - Gameplay rule: every optic marked as DovetailRU can mount on every weapon
//   whose optic slot is marked as DovetailRU.
// - ADS, magnification, zeroing and pivots remain prefab data.

class AttachmentOpticsARMST_DovetailRUClass
{
};

AttachmentOpticsARMST_DovetailRUClass AttachmentOpticsARMST_DovetailRUSource;

class AttachmentOpticsARMST_DovetailRU : AttachmentOptics
{
};
