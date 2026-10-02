#!/usr/bin/env python3
"""Faithful offline state model of the lab R entry gate (issue #27 review).

This is a *model* of the EnforceScript logic in
`ARMST_MP133_Lab_Character.c` (`LabRequestInsertFromHandler`,
`LabCanBeginFromHandler`, `LabInputReleased`, `LabWatchTick`) and
`ARMST_MP133_Lab_CommandHandler.c`. It exists so the state transitions can be
tested offline without launching Workbench/game. It is NOT runtime evidence and
must be kept in sync with the script by review.

Signals are the project-facing ones actually used by the script:
  request_active : start == true OR reload_type != 0
  pump           : the existing Core pump action (ARMST_LIGHT_RELOAD_ACTION) latch
  raised         : inputCtx.WeaponIsRaised()
  lab/gate/tube/cap/reserve/insert_active : weapon + gate state
  is_reloading   : SCR_CharacterControllerComponent.IsReloading()
"""

from __future__ import annotations

from dataclasses import dataclass, field

WATCH_MS = 100
SAFETY_MS = 2000


@dataclass
class LabRGateModel:
    latched: bool = False
    latched_ticks: int = 0

    # --- handler call (mirrors LabRequestInsertFromHandler) ---------------
    def on_handler_call(self, *, lab: bool, gate_enabled: bool, request_active: bool,
                        pump: bool, raised: bool, tube: int, cap: int, reserve: int,
                        insert_active: bool) -> str:
        # Non-lab weapons pass straight through to the engine.
        if not lab or not gate_enabled:
            return "passthrough"
        # One attempt per input hold.
        if self.latched:
            return "ignore"
        # No request at all.
        if not request_active:
            return "ignore"

        can_begin = (not insert_active and raised and reserve > 0 and tube < cap)
        # Consume the hold regardless of outcome (terminal for this attempt).
        self.latched = True

        if pump:
            return "pump"
        if not can_begin:
            return "blocked"
        return "begin"

    # --- watcher tick (mirrors LabWatchTick) ------------------------------
    def on_watch_tick(self, *, start: bool, reload_type: int, is_reloading: bool,
                       pump: bool, insert_active: bool, input_ctx: bool = True) -> str:
        if not self.latched:
            return "none"
        self.latched_ticks += 1
        if self._released(input_ctx=input_ctx, start=start, reload_type=reload_type,
                          is_reloading=is_reloading, pump=pump, insert_active=insert_active):
            self.latched = False
            self.latched_ticks = 0
            return "rearmed_release"
        if (self.latched_ticks * WATCH_MS > SAFETY_MS
                and not insert_active and not is_reloading):
            self.latched = False
            self.latched_ticks = 0
            return "rearmed_timeout"
        return "none"

    # --- release predicate (mirrors LabInputReleased) ---------------------
    def _released(self, *, input_ctx: bool, start: bool, reload_type: int,
                  is_reloading: bool, pump: bool, insert_active: bool) -> bool:
        if insert_active:
            return False
        if is_reloading:
            return False
        if pump:
            return False
        if not input_ctx:
            return True
        return (not start) and reload_type == 0