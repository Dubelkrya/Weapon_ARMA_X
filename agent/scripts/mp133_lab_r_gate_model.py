#!/usr/bin/env python3
"""Faithful offline state model of the lab R entry gate (issue #27, V2.5b).

This is a *model* of the EnforceScript logic in `ARMST_MP133_Lab_Character.c`
(`LabRequestInsertFromHandler`, `LabDeferredBegin`, `LabCanBeginFromHandler`,
`LabInputReleased`, `LabWatchTick`) and the lab command-handler hook. It exists
so state transitions can be tested offline without Workbench/game. It is NOT
runtime evidence and must be kept in sync with the script by review.

Design points enforced here:
  * exactly one attempt per input hold (latch), and the latch is re-armed ONLY
    on positive idle evidence -- never by a timer while R may be held;
  * the insert begin is deferred by one short step so a LSHIFT+R pump whose
    action fires after the handler call is still caught (order-independent);
  * a missing input context is NOT a release.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LabRGateModel:
    latched: bool = False
    pending_begin: bool = False

    # --- handler call (mirrors LabRequestInsertFromHandler) ---------------
    def on_handler_call(self, *, lab: bool, gate_enabled: bool, request_active: bool,
                        pump: bool, raised: bool, tube: int, cap: int, reserve: int,
                        insert_active: bool) -> str:
        if not lab or not gate_enabled:
            return "passthrough"
        if self.latched:
            return "ignore"          # one attempt per hold
        if not request_active:
            return "ignore"          # no reload request

        can_begin = (not insert_active and raised and reserve > 0 and tube < cap)
        self.latched = True          # consume the hold regardless of outcome

        if pump:
            return "pump"
        if not can_begin:
            return "blocked"
        if self.pending_begin:
            return "ignore"
        self.pending_begin = True
        return "begin_deferred"      # actual begin deferred by one step

    # --- deferred begin (mirrors LabDeferredBegin) ------------------------
    def resolve_deferred_begin(self, *, pump: bool, insert_active: bool) -> str:
        self.pending_begin = False
        if insert_active:
            return "none"
        if pump:
            return "pump_abort"      # pump action fired after the handler call
        return "begin"

    # --- watcher tick (mirrors LabWatchTick) ------------------------------
    def on_watch_tick(self, *, start: bool, reload_type: int, is_reloading: bool,
                      pump: bool, insert_active: bool, input_ctx: bool = True) -> str:
        if not self.latched:
            return "none"
        if self._released(input_ctx=input_ctx, start=start, reload_type=reload_type,
                          is_reloading=is_reloading, pump=pump, insert_active=insert_active):
            self.latched = False
            return "rearmed_release"
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
            return False             # cannot prove a release
        return (not start) and reload_type == 0