# MP-133 V3 — Variant A architecture (owner decision) + gates G0–G5

**Status:** `V3_VARIANT_A_ARCHITECTURE_SELECTED / T4B_COMPILE_RECOVERY_OWNER_RECOMPILE_REQUIRED / REAL_DONOR_TRANSACTION_NOT_IMPLEMENTED`.
Documentation only — this file records the owner's architecture decision and execution gates
(Issue #34 comment 5972748555). It is **not** authorization to implement G2–G5 or any transfer.

---

## Decision

Variant A for SDK 1.8.0.13: keep the stock `WeaponComponent`, the real installed physical tub
magazine, and stock firing / chamber / pump; implement a **separate weapon-local source-selection
and one-real-cartridge transfer** mechanism. Input/animation is kept separate from the transfer
mechanism. A backend swap to stock `SCR_MagazineRepackingSystem` (SDK 1.9) is a **future option
only**, subject to a separate audit — stock repacking may forbid a magazine attached to a weapon.
Choosing Variant A does not prove transfer, usability, or an eventual 1.9 path.

## Three independent parts (not merged yet)

1. **Weapon:** stock firing, chamber, and pump action.
2. **Ammunition:** source selection, consuming one cartridge, replenishing the installed magazine.
3. **Animation/control:** shell insert, cycle repeat, and safe stop.

## Architectural boundaries

- **Input/animation state machine:** separate `pump / prepare / insert / stop / abort`; event marks
  are a **candidate commit only**, never proof of cartridge transfer.
- **Transfer interface/contract (conceptual — no guessed Enforce API):** validate eligible donor,
  recipient and identity, compatibility and capacity, server authority and a per-cycle id; request
  one transfer; return a distinct `committed / rejected / indeterminate` status plus diagnostic
  evidence. No coupling of graph / R handling to `SetAmmoCount` or a specific future engine backend.
- **SDK 1.8 candidate adapter (not implemented on live items):** donor real inventory magazine/stack
  `-1` and the **same installed physical magazine** `+1`; verify both identities/counts and
  `donorBefore + targetBefore == donorAfter + targetAfter` (chamber accounted separately). **Two
  setters are not atomic**; rollback/replication/MP are unproven — do not implement on live items
  until independently validated and approved. Prevent duplicate cycle commits and concurrent
  operations. No phantom/synthetic reserve, dummy rounds, automatic whole-mag swap, or extra chamber
  edits.
- **Chungus reference:** borrow staged animation and stop/continue flags only — no dummy `+1` on
  empty, no fallback magazine spawning, no unverified donor consumption. ARMST Core (OFF in the T4b
  owner run) is read-only reference, **not** the cause of the observed `1→0`, and not a mutation
  target. Incompatible native `Weapon_Spawn/Attach/DetachMagazine` events stay OUT of per-shell commit.

## Gates (stop after each for independent review / owner evidence)

- **G0 — restoring a compiling diagnostic (current).** Branch `t4b/installed-mag-probe` publishes
  compile-recovery script SHA-256 `D581B9C9EE270725FFEC94C7685CBBCB2AB41DBA717F2B4FBCF8C4AC8DDCBEB1`
  (the invalid `proto external` overrides removed). **Owner has not yet submitted a successful Game
  recompile for this revision.** No gameplay/test/feature changes until the owner confirms no lab
  `SCRIPT(E)`, exactly-one nested animation component, event/command logging, baseline and the
  existing 250 ms / 1 s passive samples.
- **G1 — locate the `1→0` transition without mutating ammo.** The Phase A read-only SDK evidence for
  the weapon-scoped existing-item `m_OnParentSlotChangedInvoker` is documented, but its firing over
  actual pickup/equip is **unproven**. Only a separately reviewed **minimal passive lab-only
  diagnostic** is authorized after G0 (subscribe once, unsubscribe correctly, log slot transitions +
  mag component/entity identity/ammo/muzzle/chamber, bounded, no polling, no setter). Tests: idle
  `+1`; `+1` then pickup/equip without R; then a separate first native R after capturing equip state.
  Do not attribute a change to a specific event unless pre/post observations isolate it. Core stays OFF.
- **G2 — actual usability of the target `+1`.** Only after G1: one isolated, owner-run test on an
  already-equipped T4b (if a safe, independently approved invocation exists): baseline `+1` on the
  same physical mag/chamber, then a controlled native rack and one actual shot with a valid loadout.
  Distinguish magazine count, muzzle supply, chamber flag, physical-mag identity and owner-visible
  result. Do not assume readback = a real usable shell. No donor yet.
- **G3 — isolated donor experiment.** After G2 proves target semantics: source and recipient are two
  explicitly expendable, compatible, homogeneous test magazines. First READ-ONLY verify the SDK 1.8
  API, authority, inventory lifetime and observers; then propose a guarded one-shell conservation test
  with an explicit stop/partial-failure policy and review before implementation.
- **G4 — integrate staged reload animation.** After G3: an isolated lab graph/ASI (not prod) following
  Chungus prepare/grab/insert/continue/stop; a reliable weapon-side or explicitly bridged event,
  per-cycle token and exactly-once commit, safe interruption. Keep short-R manual pump, hold-R
  inspection and frozen Core LSHIFT+R. Stock `CMD_Weapon_Reload=7` is excluded by the current MP-133
  graph; no blind command 7 or global `modded SCR_CharacterCommandHandlerComponent`.
- **G5 — integration / MP / optional backend change.** Only after gated owner tests: independent real
  donor→installed target, chamber/shot/stop, network authority/replication, low FPS, Core compatibility,
  then separate production-integration approval. Adapt SDK 1.9 repacking only after a feasibility
  audit; if the attached-mag prohibition persists, keep the custom backend.

## Scope / protections

Work continues on `t4b/installed-mag-probe` (no new branch per task). Unchanged and protected:
original T2a/T4a, frozen V2/P2, Astra, ARMST Core, production Weapons, worlds/layers, and the
user-owned untracked `reports/CORE_ARMST_READONLY_AUDIT.md`. No destructive git commands; preserve
`.meta`/GUIDs. Agent cannot claim owner Workbench/test results.

**Immediate next action:** G0 owner compile confirmation only. G1 passive code waits for review.
