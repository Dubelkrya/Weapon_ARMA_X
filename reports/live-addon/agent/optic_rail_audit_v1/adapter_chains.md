# OPTICS / SIGHTS / RAILS - MULTI-HOP ADAPTER CHAINS (READ ONLY)

Each edge is validated independently; do not collapse.

## Prefabs/Weapons/Attachments/Optics/AKDovetailMount/armst_Optic_AKDovetailMount.et  (GUID D71FD2BD68AC4B31)
- outer host type: **AttachmentOpticsDovetailAK**
- inner child slot type: **AttachmentOpticsRIS1913**  (PivotID  / ChildPivotID )

## Prefabs/Weapons/Attachments/Optics/HKG36/armst_HKG36_CarryHandle_Picatinny.et  (GUID 8965EFD9F6CC9B95)
- outer host type: **AttachmentOpticsG36**
- inner child slot type: **AttachmentOpticsRIS1913**  (PivotID  / ChildPivotID )

## Validated example chains (authoritative knowledge)

1. AK-family DovetailAK slot {65AE4CB5E23C0F61} -> AKDovetail outer WAA AttachmentOpticsDovetailAK {557E85EEE1B60316} -> AKDovetail child RIS slot AttachmentOpticsRIS1913 {4289872E53434277} (snap_ris / snap_weapon) -> armst_Optic_Collimator WAA AttachmentOpticsRIS1913 {5284D858FFF9BE66}
   - each edge = EXACT_MATCH by class; child COLLIMATOR mount currently fails at runtime

2. G36 weapon slot AttachmentOpticsG36 -> CarryHandle_Picatinny outer WAA AttachmentOpticsG36 -> child slot AttachmentOpticsRIS1913 -> RIS optics
