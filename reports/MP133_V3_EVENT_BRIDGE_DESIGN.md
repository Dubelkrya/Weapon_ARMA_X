# MP-133 V3 — Event bridge design (character → specific weapon instance)

**Status:** `T2A_ROUTE_OBSERVED / BRIDGE_DESIGN_AUTHORIZED_ONLY`. Design only.
No implementation, prefab/clip/graph edits, Workbench run, R hooks, ammo/magazine/chamber
changes, production Weapons/Core/V2 edits, or new addon. Source: Issue #27 comment
5969505026. STOP for owner review before any lab implementation.

---

## 1. Confirmed facts (T2a run 2)

- Diagnostic MP-133 prefab `{5FB844730BED8BD1}` was equipped; screenshot + log show
  `hasT2AWpnComp=1`, so the subclass assignment took effect.
- **Weapon** callback receives weapon-side events (`BlendIn`, `Weapon_EnableFire`,
  `Weapon_Rack_Bolt`) → the subcomponent is live and `OnAnimationEvent` is the weapon-side
  receiver.
- **Character** invoker receives the player-only marker `ARMST_T2A_PM_C41F7A29`
  (4 events, `isServer=1`).
- **No** weapon-side marker line → the player-authored event is **not** automatically
  forwarded to the weapon component. (Applies to the tested configuration.)
- The 4 events and `isServer=1` are **not** proof of exactly-once delivery or of an
  authoritative transaction; subscription counting / authority must be established.

## 2. Goal

Design an explicit, lab-only **bridge**: a character-side observer of the unique marker
resolves the currently equipped lab MP-133 and calls a **dedicated diagnostic method** on
that exact weapon component (never the engine `OnAnimationEvent` path for the player
route).

## 3. Bridge design

### 3.1 Participants
- **Weapon instance** — `ARMST_T2A_WeaponAnimationComponent` (already on the lab prefab);
  add a plain public method `T2AOnPlayerMarker(int token)` (later, after approval) — this
  is a direct method call, not an engine callback.
- **Character observer** — the lab `modded SCR_CharacterControllerComponent` already
  subscribed to `GetOnAnimationEvent()`; it detects the marker and forwards.

### 3.2 Route (per marker callback)
1. `animEventType == marker` (unique `ARMST_T2A_PM_C41F7A29`). Any other event is ignored.
2. `wpn = GetWeaponManagerComponent().GetCurrentWeapon()` — resolve **at callback time**;
   null → drop (`no-weapon`).
3. `we = wpn.GetOwner()`; null → drop.
4. `comp = we.FindComponent(ARMST_T2A_WeaponAnimationComponent)`; null → drop
   (`not-lab`/`no-component`).
5. `comp.T2AOnPlayerMarker(seq)`.

This guarantees delivery **only to the equipped lab MP-133 instance**; there is no global
event bus and no dependency on `SyncWithCharacter`.

### 3.3 Event identity and cycle boundaries
- The char observer assigns a **monotonic token** per marker callback
  (`m_iMarkerSeq++`).
- The weapon method dedupes on the token (`token != m_iLastToken` → process; else
  `dup-token`). This is at-most-once per callback and **does not lose later plays**: every
  replay of the clip produces a new callback → new token.
- **Cycle** = one authored marker occurrence. `BlendIn`/`BlendOut` remain separate events;
  the bridge reacts only to the marker. A cycle ends at the next marker or at `BlendOut`.
- **Interrupt:** interrupted **before** the marker frame → no callback → no forward (no
  phantom). Interrupted **after** the marker → the single forward already happened; a later
  replay is a new cycle (intended).

### 3.4 Weapon switch / instance changes
- The route resolves the weapon **per callback**, so a switch targets the new weapon; if it
  is not a lab MP-133, the event is dropped. No stale reference is retained.
- Unequip/drop mid-clip → no callback or the component is gone → drop.

### 3.5 Server / client
- The bridge is **side-local**: wherever the character invoker fires, it forwards to that
  side's weapon instance. Run 2 showed `isServer=1` in solo (server+client are the same
  machine).
- For any future ammo commit, only the **server-side** forward may perform the transaction.
  Whether the invoker also fires on a remote client and/or on a dedicated server is
  **UNRESOLVED**; if it does not fire server-side in MP, a client→server RPC carrying the
  token would be required, and that must be proven by a separate MP test **before** any
  ammo work. `isServer=1` is **not** authority proof.

### 3.6 Subscription lifecycle
- Subscribe **once** per character component: `m_bT2ASubscribed` guard in `OnInit`; remove
  the handler on `OnDelete` / `OnControlledByPlayer(false)`.
- Log `init #n` and `subscribed=0|1`, and a per-subscription id, so duplicate
  subscriptions are visible (run 1 showed 6 char events, run 2 showed 4 — the counter must
  establish whether that is multiple plays or duplicate handlers).

### 3.7 Passive logs, failure and STOP
- Char observer: `[ARMST_T2A-CHR] MARKER seq=N`.
- Weapon method: `[ARMST_T2A-BRIDGE] token=N ok | drop=<reason>` with reasons
  `no-weapon`, `not-lab`, `no-component`, `dup-token`.
- **STOP/abort** if: one marker yields more than one bridge call with **distinct** tokens
  (bridge duplication); the bridge is called without a marker; the weapon component ever
  receives the marker through the engine `OnAnimationEvent` (route collision); or native
  short-R / hold-R / other weapons regress.

## 4. Alternative — marker authored on a weapon-side clip

The weapon component already receives weapon-side events (run 2). If the marker is authored
in the **weapon.asi** clip instead of the player clip, the weapon component receives it
**directly — no bridge needed**.

Limitations:
- The weapon clip may not carry the needed motion/timing (e.g. a shell-grab is a player
  motion); a weapon-only event may not coincide with the player action.
- It couples logic to a visual weapon clip; retiming the clip moves/removes the event.
- It cannot express triggers that are inherently player-side.

**Comparison:** if the required trigger can be co-authored on the weapon clip at the same
frame, it is simpler and preferred. If the trigger must follow a player action, the bridge
is required. **Decision deferred to owner.**

## 5. Minimal log-only follow-up test plan (single, later — not now)

Goal: prove the bridge delivers to the correct instance, with no ammo/R changes.
1. (After approval) add the bridge to the T2A lab: the weapon method logs
   `[ARMST_T2A-BRIDGE] token=N wep=… comp=1`; the char observer logs `MARKER seq=N`.
2. Owner run: equip `MP-133 [T2A-DIAG]`, one ordinary short R; capture
   `console.log`/`script.log`.
3. Assert: exactly **one** `[ARMST_T2A-BRIDGE]` per `MARKER` (token match); `wep=` is the
   T2A prefab; **no** `[ARMST_T2A-WPN] MARKER` from the engine route; pump unaffected.
4. STOP conditions as §3.7.

## 6. Dependency check (existing Weapons)

- Weapons' own scripts (`Scripts/Gamecode/*.c`) define only `MagazineWell*`
  (`: BaseMagazineWell`) and two attachment classes (`AttachmentMuzzle9_39_armst`,
  `AttachmentOptics…`). **No UI classes are used.**
- Weapons `addon.gproj` dependencies: `58D0FB3206B6F859` (the common base project used by
  every sibling addon) and `6922BE16974B3AED` — **not present as a local addon** (no local
  `addon.gproj` owns that GUID; it appears only as a dependency). Per the owner this is an
  **ASTRA/UI-related** project.
- The T2A lab (deps `58D0FB3206B6F859` + Weapons `6A70E400C54051DC`) therefore
  **transitively pulls** `6922BE16974B3AED`. The bridge design adds **no** new dependency
  (character/weapon/inventory APIs only). No Core/third-party addon is enabled.

## 7. Facts / hypotheses / owner decisions

- **Facts:** the weapon component is live and receives weapon events; the player marker
  reaches the char invoker but not the weapon; T2A lab deps = base + Weapons; the only
  non-base Weapons dep `6922BE16974B3AED` is absent locally (ASTRA/UI per owner); Weapons'
  own scripts have no UI.
- **Hypotheses:** the 4 char events are one authored event with duplicate subscriptions or
  multiple plays (needs the counter); MP remote-server behavior of the invoker; exactly-once.
- **Owner decisions required:** (a) bridge vs weapon-side marker; (b) whether the trigger
  must follow a player motion; (c) MP authority/RPC approach.

## 8. Authorization

Design only. No lab implementation, prefab/clip/graph edits, Workbench/game, R hooks,
ammo/magazine/chamber changes, production Weapons/Core/V2 edits, or new addon. STOP for
owner review. Status `T2A_ROUTE_OBSERVED / BRIDGE_DESIGN_AUTHORIZED_ONLY`.
