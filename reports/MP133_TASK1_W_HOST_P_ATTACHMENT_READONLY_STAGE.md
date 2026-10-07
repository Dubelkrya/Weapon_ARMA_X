# W_HOST_P_ATTACHMENT_READONLY — staged review evidence

Status: **W_HOST_P_ATTACHMENT_READONLY_STAGE_READY_OWNER_REVIEW**.
Authority: [Issue #34 comment 6045697284](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6045697284). Date 2026-10-07. Base HEAD c8e48b203f63bf2acda2a63247b378f3e2856185; branch t4b/installed-mag-probe.

## Owner evidence and narrower scope

Owner Live Debug identified character-side MP133_Astra2.agr, MasterControl, MP133_Astra2_player.asi and evaluation. P_INJECTION_IDENTIFIED/P_GRAPH_EXISTS/P_GRAPH_EVALUATED=YES is **owner evidence**, not an agent runtime. Literal binding Weapon and attachment-API ownership were not visible in the screenshot. Multiple R presses in that log do not constitute a clean new transport experiment. Remaining questions: addressability, input transport and gates. No P setter/command/start attempt is prepared here; the earlier deep-dive request experiment is NOT authorized by this narrower stage.

## Source and stage ledger

Functional source is CURRENT INSTALLED V, never older tracked labs.

- Source: C:\\Users\\yshky\\Documents\\My Games\\ArmaReforgerWorkbench\\addons\\ARMSTMP133T4B_InstalledMagProbe\\Scripts\\Game\\ARMST_T4B\\ARMST_T4B_AstraV2_WeaponAnimationComponent.c
- SOURCE_SHA256: 411D5E127C5E97D6A3BAAA91D7B79C0CE662F06600D03EC31080A2C878C72640
- Staged: C:\\Users\\yshky\\Documents\\My Games\\ArmaReforgerWorkbench\\addons\\Weapon_ARMA_X\\artifacts\\astra-rebuild\\stagePAttachmentReadonly\\Scripts\\Game\\ARMST_T4B\\ARMST_T4B_AstraV2_WeaponAnimationComponent.c
- STAGED_SHA256: 241E6EC19633812740BBD25DB960E21F77A928AC2FD273C81D74B75E86BAA7BC
- Git normalized blobs: 8afef00 -> 0279d95. Delta +33/-0.

Exactly ONE staged file. No CustomR copy necessary: existing qualified shell-R resolves actual current AstraV2 and invokes T4BWPropRequest. One diagnostic call at its beginning performs lookup before existing WPROP writes. It runs once per invocation, including an invocation that subsequently takes existing manual-abort; no frame/event callbacks or timers added. A diagnostic failure returns only from the diagnostic, not from the existing request. Existing WPROP behavior, PACT and frozen rack caller/helper remain unchanged.

## Exact API evidence and interpretation

Installed Workbench/docs/EnfusionScriptAPI/html/interfaceBaseAnimationControllerComponent.html declares int BindAttachment(string), int BindAttBoolVariable(int,string), bool GetAttBoolVariable(int,int). WeaponAnimationComponent inherits through BaseItemAnimationComponent -> AnimationControllerComponent -> BaseAnimationControllerComponent (both installed documentation hierarchies inspected in deep dive). Calls are on THIS actual equipped component, not a speculative character FindComponent.

IDs are fresh local variables for each request; no cache retained across equip/detach. Negative IDs fail closed, following the existing probe convention; the native docs do not specify a sentinel. Nonnegative is therefore **provisional** and valid=true logs are not guaranteed native-valid/P-identity proof. ID0 is accepted. Failed bool binding logs IDs and stops before getters. Successful lookup/four getters gives addressability evidence on this controller, not proof of receiver identity or P activation. No method body or compiler/runtime claim.

Log schema:
```text
[ARMST-T4B-PATT] phase=bind attachment=Weapon id=<int> valid=<bool.ToString>
[ARMST-T4B-PATT] phase=vars req=<int> elig=<int> rep=<int> stop=<int>
[ARMST-T4B-PATT] phase=read req=<bool.ToString> elig=<bool.ToString> rep=<bool.ToString> stop=<bool.ToString>
[ARMST-T4B-PATT] phase=reject reason=variable-bind-invalid
```
Bool.ToString preserves the existing project's logging convention; do not infer numeric 0/1 formatting without owner output. Read is BEFORE WPROP current-session request, not its after-write readback.

## COMPLETE unified diff

```diff
diff --git "a/C:\\Users\\yshky\\Documents\\My Games\\ArmaReforgerWorkbench\\addons\\ARMSTMP133T4B_InstalledMagProbe\\Scripts\\Game\\ARMST_T4B\\ARMST_T4B_AstraV2_WeaponAnimationComponent.c" "b/C:\\Users\\yshky\\Documents\\My Games\\ArmaReforgerWorkbench\\addons\\Weapon_ARMA_X\\artifacts\\astra-rebuild\\stagePAttachmentReadonly\\Scripts\\Game\\ARMST_T4B\\ARMST_T4B_AstraV2_WeaponAnimationComponent.c"
index 8afef00..0279d95 100644
--- "a/C:\\Users\\yshky\\Documents\\My Games\\ArmaReforgerWorkbench\\addons\\ARMSTMP133T4B_InstalledMagProbe\\Scripts\\Game\\ARMST_T4B\\ARMST_T4B_AstraV2_WeaponAnimationComponent.c"	
+++ "b/C:\\Users\\yshky\\Documents\\My Games\\ArmaReforgerWorkbench\\addons\\Weapon_ARMA_X\\artifacts\\astra-rebuild\\stagePAttachmentReadonly\\Scripts\\Game\\ARMST_T4B\\ARMST_T4B_AstraV2_WeaponAnimationComponent.c"	
@@ -79,11 +79,44 @@ class ARMST_T4B_AstraV2_WeaponAnimationComponent : ARMST_T4B_WeaponAnimationComp
 			+ " stop=" + m_iWPropStop.ToString(), LogLevel.NORMAL);
 	}
 
+	// Read-only W-host attachment lookup. IDs are rebound per qualified request;
+	// nonnegative is provisional only, not proof of P-instance ownership.
+	protected void T4BPAttachmentReadonly()
+	{
+		int att = BindAttachment("Weapon");
+		Print("[ARMST-T4B-PATT] phase=bind attachment=Weapon id=" + att.ToString()
+			+ " valid=" + (att >= 0).ToString(), LogLevel.NORMAL);
+		if (att < 0)
+			return;
+
+		int req = BindAttBoolVariable(att, "ASTRA_ShellRequest");
+		int elig = BindAttBoolVariable(att, "ASTRA_ShellEligible");
+		int rep = BindAttBoolVariable(att, "ASTRA_ShellRepeat");
+		int stop = BindAttBoolVariable(att, "ASTRA_ShellStop");
+		Print("[ARMST-T4B-PATT] phase=vars req=" + req.ToString()
+			+ " elig=" + elig.ToString() + " rep=" + rep.ToString()
+			+ " stop=" + stop.ToString(), LogLevel.NORMAL);
+		if (req < 0 || elig < 0 || rep < 0 || stop < 0)
+		{
+			Print("[ARMST-T4B-PATT] phase=reject reason=variable-bind-invalid", LogLevel.NORMAL);
+			return;
+		}
+
+		bool rbReq = GetAttBoolVariable(att, req);
+		bool rbElig = GetAttBoolVariable(att, elig);
+		bool rbRep = GetAttBoolVariable(att, rep);
+		bool rbStop = GetAttBoolVariable(att, stop);
+		Print("[ARMST-T4B-PATT] phase=read req=" + rbReq.ToString()
+			+ " elig=" + rbElig.ToString() + " rep=" + rbRep.ToString()
+			+ " stop=" + rbStop.ToString(), LogLevel.NORMAL);
+	}
+
 	// Animation-only, one-cycle shell request originated on the WEAPON side.
 	// No ammo/mag/chamber writes, no native reload command, no P-side setter.
 	// Repeat is forced false. Only current graph variables are bound.
 	bool T4BWPropRequest()
 	{
+		T4BPAttachmentReadonly();
 		T4BWPropBind();
 		// NOTE: the < 0 invalid-sentinel is a bounded assumption (engine bind docs do
 		// not publish the sentinel); the readback below is the authoritative signal.
```

## Static checks and restrictions

New delta: BindAttachment=1, BindAttBoolVariable=4, GetAttBoolVariable=4. SetAtt*=0, CallAttCommand*=0, CallCommand*=0, ammo/chamber/magazine/G3B2 writers=0. Only Print, ToString, comparisons and the one helper call accompany those lookups. Braces38/38; parentheses244/244. All pre-existing method bodies remain text-identical except the one diagnostic call; no parent forwarding changed. Existing SetBoolVariable and PACT callbacks in the full baseline are preserved, not newly introduced. SETATT_CALLS=0 describes this delta/diagnostic, not other existing scripts.

Stage path confirmed git-ignored. No git add -f. No compile, Workbench, Reforger or runtime. Python addon resolver PASS. Previous suite failed and repeat was safety-rejected in the preceding audit; no unsafe repeat here. Integrity has 10 existing broken links; no unrelated repair. Publication only report + deep-dive wording correction + plan. Owner CORE_ARMST_READONLY_AUDIT.md remains excluded.

## Owner handoff (NOT an install/runtime GO)

Review exact delta/hash first. Future installation, compile and one qualified shell-R each require separate authorization. This stage does not activate P, so continued W-only markers would not be failure of this read-only probe. Lookup-negative -> W_HOST_ATTACHMENT_UNAVAILABLE; variable-bind-negative -> W_HOST_ATTACHMENT_VARIABLES_UNAVAILABLE; four getters observed -> W_HOST_ATTACHMENT_READBACK_OBSERVED (P identity still separate). Do not escalate to setters/commands, graph reattachment, native reload or G3B2 from any lookup result. No automatic retries/fallbacks. Rollback now: do not install; no historical restoration.

## Preservation

Pre/post aggregate SHA-256 guard, sorted absolute path|fileSHA rows, LF/UTF8, extensions c/conf/et/meta/layer/gproj/agr/agf/asi/ast/txa/anm:

| Root under addons | Files | Before = after SHA256 |
|---|---:|---|
| ARMSTMP133T4B_InstalledMagProbe | 105 | 4FEA157584BB49F6177AE83A6D1D48B928637905F46EE543C3CF5258AC464C8E |
| Weapon_ARMA_X/labs | 58 | 505C52A752D320DC69DD4E53E297AF87EF10ECC622AC04CDB07D2FEBC38D644C |
| ARMST-PLATFORM---Core | 5521 | 2EDF4D1DCA02F0C662AE1CA567D8B9655C374BC817883B7625A7AF02D8860B4B |
| ARMST-PLATFORM---Weapons | 1584 | A7C611FE0417F5A5E1DA6E4209F01E3CF846295E9ADA57999713FF1B4CC2AECF |

GAMEPLAY_FILES_CHANGED_BY_CLEANUP=0. Only ignored scratch plus authorized documentation changed.

```text
W_HOST_P_ATTACHMENT_READONLY_STAGE_READY_OWNER_REVIEW
HEAD = c8e48b203f63bf2acda2a63247b378f3e2856185 (source checkpoint; publication commit reported separately)
LIVE_BASELINE_FILES = ARMST_T4B_AstraV2_WeaponAnimationComponent.c (current installed V)
LIVE_BASELINE_SHA256 = 411D5E127C5E97D6A3BAAA91D7B79C0CE662F06600D03EC31080A2C878C72640
STAGED_FILES = artifacts/astra-rebuild/stagePAttachmentReadonly/Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c
STAGED_SHA256 = 241E6EC19633812740BBD25DB960E21F77A928AC2FD273C81D74B75E86BAA7BC
SETATT_CALLS = 0
COMMAND_CALLS = 0
GRAPH_CHANGED = NO
PREFAB_CHANGED = NO
INPUT_CHANGED = NO
G3B2_CHANGED = NO
LIVE_CHANGED = NO
WORKBENCH_LAUNCHED = NO
RUNTIME_TEST = NO
```

