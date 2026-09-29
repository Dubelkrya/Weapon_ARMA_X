# Groza ActionsManager Context Audit (READ ONLY)

- target: `Prefabs/Weapons/Russian/Rifle/Groza/armst_Groza_base.et`
- parent chain: `Rifle_Base.et` -> `Weapon_Base.et`; neither declares any UserActionContext => all contexts are LOCAL_ADDITION

TOTAL_CONTEXTS: 9
KEEP_REQUIRED: 1
KEEP_OVERRIDE: 0
REMOVE_STALE_LOCAL: 5
REVIEW_REQUIRED: 3

| instance | name | pivot | origin | live_owner | references | child | class |
|---|---|---|---|---|---|---|---|
| 5086F9ADF588DCA4 | None | None | LOCAL_ADDITION | UNKNOWN (unnamed interaction point) | possibly core action context (muzzle/firemode/bipod) | NO | REVIEW_REQUIRED |
| 5956E32BAAADE657 | None | None | LOCAL_ADDITION | UNKNOWN (unnamed interaction point) | possibly core action context (muzzle/firemode/bipod) | NO | REVIEW_REQUIRED |
| 5A1E58F7B04F9BE5 | None | slot_magazine | LOCAL_ADDITION | magazine well / MagazineWell | magazine action | NO | KEEP_REQUIRED |
| 5A1E58F7AED270D4 | None | None | LOCAL_ADDITION | UNKNOWN (unnamed interaction point) | possibly core action context (muzzle/firemode/bipod) | NO | REVIEW_REQUIRED |
| 5AF896EFFE8D407A | optic | slot_optics | LOCAL_ADDITION | NO_LIVE_OWNER | none (only agent backup copies) | NO | REMOVE_STALE_LOCAL |
| 5D16CD572EBFE7C3 | ris_right | slot_ris_right | LOCAL_ADDITION | NO_LIVE_OWNER | none (only agent backup copies) | NO | REMOVE_STALE_LOCAL |
| 5D16CD57294C5019 | ris_left | slot_ris_left | LOCAL_ADDITION | NO_LIVE_OWNER | none (only agent backup copies) | NO | REMOVE_STALE_LOCAL |
| 5D16CD5729B8BD31 | ironsight_front | slot_ironsight_front | LOCAL_ADDITION | NO_LIVE_OWNER | none (only agent backup copies) | NO | REMOVE_STALE_LOCAL |
| 5D16CD57285E8439 | ironsight_rear | slot_ironsight_rear | LOCAL_ADDITION | NO_LIVE_OWNER | none (only agent backup copies) | NO | REMOVE_STALE_LOCAL |

## Notes
- Named contexts `optic`, `ris_right`, `ris_left`, `ironsight_front`, `ironsight_rear` correspond only to the removed Groza attachment slots; their attachment slots no longer exist, no active UserAction and no child prefab references them (only stale `agent/weapon_relocation/...` backup copies) => REMOVE_STALE_LOCAL.
- The 4 unnamed contexts are UI-visible core interaction points (by elimination: bipod / magazine / firemode / muzzle). One is anchored at PivotID `slot_magazine` => KEEP_REQUIRED. The other three are unnamed and could not be definitively mapped or proven unbound => REVIEW_REQUIRED (do not remove).
- No `firemode` / `muzzle` / `bipod` named contexts exist in this file; the muzzle slot (`4E2B66CBA589F625`) has no named action context left.

LIVE_FILES_CHANGED: NONE
