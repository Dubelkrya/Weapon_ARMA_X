# PP/BP Magazine Tail Review

Read-only. No resources changed.

## STANAG Base

- `Magazine_556x45_STANAG_30rnd_Base.et` GUID `11B9CC1FB4AEE740`: used only as parent of M855 Ball and M855 Ball BP. No weapon MagazineTemplate reference.
- `armst_Magazine_556x45_STANAG_30rnd_Base_BP.et` GUID `98011CC596464D8F`: no children, no references.
- STANAG_BASE_ROLE: INHERITANCE_BASE
- STANAG_BASE_BP: REDUNDANT

## L1A1 M61 AP

- `armst_Magazine_762x51_L1A1_20_M61_AP.et` GUID `5D4E812AEAA7CC1F`: parent L1A1 20 M80 Ball, mapping index 2 (external M61 AP), no references.
- `armst_Magazine_762x51_L1A1_30_M61_AP.et` GUID `E70FEC32673242CB`: parent L1A1 30 M80 Ball, mapping index 2 (external M61 AP), no references.
- New local BP siblings map index 1 to the local ARMST config that reconstructs M61 AP over M80, giving the same effective AP behavior with local identity.
- L1A1_20_M61_CLASSIFICATION: REDUNDANT_LEGACY_AP
- L1A1_30_M61_CLASSIFICATION: REDUNDANT_LEGACY_AP

## Reference safety

- All listed redundant resources have REFERENCE_COUNT = 0. No redirection is required.

LIVE_FILES_CHANGED: NONE
