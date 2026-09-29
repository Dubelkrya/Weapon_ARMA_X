# Single-Canonical PSO Compatibility Architecture (READ ONLY)

## Canonical PSO
- `armst_Optic_PSO1.et` GUID `C850A33226B8F9C1` — safe to preserve (has live defaults on AKM_full/AK74M_full).

## Required slot types (frozen weapon overrides)
- `AttachmentOpticsDovetailAK`: AKM, 9A91/VAL/VSS/VSK94
- `AttachmentOpticsDovetailSVD`: SOC94 (+ vanilla SVD native)
- `AttachmentOpticsARMST_DovetailRU`: AEK971

## Compatibility mechanism (proven)
- Slot `AttachmentMuzzle545_39` accepts prefab typed `AttachmentFlashHider6P20` (which derives from `AttachmentFlashHider`). => compatibility = attachment type is the slot type **or a subclass of it** (slot = category ancestor, attachment = specific descendant).
- No list/polymorphic/whitelist field exists locally; `WeaponAttachmentAttributes` carries a single `AttachmentType`.

## Cardinality
- Each PSO prefab: exactly one `WeaponAttachmentAttributes` (instance `5284D858FFF9BE66`) with one `AttachmentType`.
- Multiple `WeaponAttachmentAttributes` observed only across DIFFERENT components (`UGL_M203_base.et`), never twice in one component. No local evidence that an item can declare multiple compatible types.

## Type relationships
- `AttachmentOpticsARMST_DovetailRU : AttachmentOptics` (addon script).
- `AttachmentOpticsDovetailAK` / `AttachmentOpticsDovetailSVD` are game-defined; their mutual inheritance is not locally inspectable.
- No aliases; no compatibility lists.

## Architecture evaluation
- OPTION_A (one prefab, multiple AttachmentType): not expressible — attributes hold a single type.
- OPTION_B (shared parent AttachmentType): requires all three slot types to be ancestors of one attachment type, i.e. the three types must form an inheritance chain; they are distinct families (unproven chain).
- OPTION_C (multiple AttachmentType entries/instances in one item): no local example; engine support unproven.
- OPTION_D (wrappers): rejected — a wrapper would be the attached entity, i.e. a separate playable optic, not one gameplay prefab.
- OPTION_E: none found.
- OPTION_F: as evidenced, one attachment type cannot satisfy three sibling slot types under subtype compatibility.

## Conclusion
- Under the observed subtype-compatibility rule and the override freeze, ONE playable PSO prefab cannot be compatible with all three slot types.
- A true single-prefab collapse therefore requires unifying the three weapon-side slot types == changing frozen weapon overrides.
- PSO1_ak (SVD type) and PSO1_DovetailRU (RU type) must remain as the only compatible optics for SOC94 and AEK971 respectively.
- Canonical `armst_Optic_PSO1.et` remains the AK-type PSO (default on AKM_full/AK74M_full).

LIVE_FILES_CHANGED: NONE
