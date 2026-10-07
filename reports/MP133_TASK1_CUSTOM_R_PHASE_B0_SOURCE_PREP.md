# MP-133 Task #1 — Custom-R input routing Phase B0 (source prep)

Статус: **T4B_CUSTOM_R_PHASE_B_FINAL_INPUT_CONFIG_INSTALLED_WAITING_OWNER_REGISTRATION**
Дата: 2026-10-07
Задание: Issue #34 — install финального input-конфига в live + labs ([#6025962357](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34)). Дальше owner вручную регистрирует `.conf` в Workbench.
Режим: **установлено в live + labs** — `chimeraInputCommon.conf` `57778A1D…`; `.meta`/GUID не создавались (их создаст Workbench).

---

## FINAL INPUT CONFIG STRUCTURE PRE-REGISTRATION (owner task 6025912911)

**Цель:** подготовить финальную структуру конфига, которую owner позже зарегистрирует через Workbench. Source-only / staging-only.

**Ровно одна правка** — новый контекст переведён с аддитивного оператора на обычный массив:

```diff
   ActionContext ARMST_MP133_ReloadContext {
    Priority 20000
    Flags 0x6 0
-   ActionRefs +{
+   ActionRefs {
     "ARMST_MP133_Reload"
    }
   }
```

**Итоговый staged блок:**

```text
ActionContext ARMST_MP133_ReloadContext {
 Priority 20000
 Flags 0x6 0
 ActionRefs {
  "ARMST_MP133_Reload"
 }
}
```

**SHA:**

| файл | old | new |
|---|---|---|
| staged `Configs/System/chimeraInputCommon.conf` | `71D4B2DD92B12BF93E76DEAF6B1B8CF763F2505D837981C7C469FF99D0DDCF4B` | `57778A1D2ED7EDCA8A321CCDF2D5A76A8092E8C0319D0D4ED9DDE07194F60993` |
| staged `Configs/System/keyBindingMenu.conf` | `368B51F7862B245C730E40CA1C226B369F845C7E0DC9B604E822F2078BCDC01D` | same (не менялся) |

**Не менялось:** Action `ARMST_MP133_Reload`, context `ARMST_MP133_ReloadContext`, `Priority 20000`, `Flags 0x6 0`, `keyboard:KC_R`, `InputSourceValue "{B1C2D3E4F5A60001}"`, `keyBindingMenu.conf`, скрипты, live/labs, Core.

**Verification:**
```
chimeraInputCommon.conf structural delta = exactly 1 token/operator change (+{ -> {)
keyBindingMenu.conf changed = NO
.meta created = NO
GUID invented = NO
script changed = NO
live changed = NO
labs installed copy changed = NO
Core changed = NO
```

**INSTALL (owner GO 6025962357):** финальный `chimeraInputCommon.conf` установлен byte-identical в live + labs:

| файл | live SHA | labs SHA |
|---|---|---|
| `Configs/System/chimeraInputCommon.conf` | `57778A1D2ED7EDCA8A321CCDF2D5A76A8092E8C0319D0D4ED9DDE07194F60993` | same |

`keyBindingMenu.conf` не менялся (`368B51F7…`); `.meta`/GUID не создавались; скрипты/protected/Core не менялись.

**Next (owner):** вручную в Workbench зарегистрировать оба `.conf` (`chimeraInputCommon.conf`, `keyBindingMenu.conf`) → Workbench создаёт реальные `.meta` + уникальные GUID → синк `.meta` в labs + commit → owner runtime (`context_state active=true`, `RINPUT = YES/NO`, vanilla cmd1..6 = YES/NO).

Status: **`T4B_CUSTOM_R_PHASE_B_FINAL_INPUT_CONFIG_INSTALLED_WAITING_OWNER_REGISTRATION`**. STOP.

---

## GUID / RESOURCE-REGISTRATION PATH (read-only, owner-review 6025746594)

**Scope:** определить корректный путь регистрации `.meta`/GUID (без ручного сочинения GUID, без создания `.meta`, без правок live/labs/Core).

### Почему ручной `.meta` — неправильный путь (source proof)

Регистрация в ResourceDB — это операция **Workbench**. Installed SDK (`…\Workbench\docs\EnfusionScriptAPI\html\`) экспонирует:

| API | сигнатура | назначение |
|---|---|---|
| `ResourceManager` | `proto external MetaFile GetMetaFile(string absFilePath)` | получить `.meta` файла |
| `ResourceManager` | `proto external bool RegisterResourceFile(string absFilePath, bool bBuildRuntimeResource)` | **зарегистрировать файл ресурса (создать `.meta`/GUID)** |
| `ResourceManager` | `proto external void RebuildResourceFile(...)` / `RebuildResourceFiles(...)` | перестроить ресурс(ы) |
| `GeneratedResources` | `proto bool RegisterResource(string absPath, out ResourceName resourceName)` | регистрация из absolute path |
| `CheckGUID` | NetApiHandler | проверка уникальности GUID |
| `ResaveMetaPlugin` | `Resave()`, `Run()`, `RunCommandline()`, `OnResourceContextMenu(...)` | Workbench-плагин записи/пересохранения `.meta` |
| `ResourceProcessorPlugin` | `ForceResaveMetaFile`, `static FixMetaFile(...)` | форс-пересохранение/фикс `.meta` |

Дополнительно: Workbench **не** создаёт `.meta` для loose-файла при простом скане проекта — оба T4B `.conf` остались незарегистрированными в двух подряд запусках (`Setting null GUID`, L166–167 в обоих логах).

→ **`.meta` должен быть произведён Workbench** (resource registration / resave), а не написан вручную.

### Корректная процедура (proven, выполняет owner)

1. Owner открывает T4B addon в Workbench с обоими `.conf` на месте.
2. Регистрирует ресурсы так, чтобы Workbench записал `.meta` — через Resource Browser/import (`RegisterResourceFile`) или Resave-Meta plugin (в т.ч. его `RunCommandline`). Workbench присваивает **уникальный** GUID и пишет `Name "{GUID}Configs/System/<file>"` с `CONFResourceClass`-конфигурациями.
3. Проверка: в логе Workbench больше нет `resource not registered` для этих двух путей; запись в `resourceDatabase.rdb` несёт ненулевой GUID.
4. Закоммитить сгенерированные `.meta` (live + labs byte-identical).

### GUID handling

- GUID — Workbench-generated, глобально уникальный; для валидации существует `CheckGUID`.
- **Не** переиспользовать Core GUID: `{795184CF9AD764DB}` (`chimeraInputCommon`) и `{4EE7794C9A3F11EF}` (`keyBindingMenu`) — это ресурсы Core на тех же путях.
- Live и labs — один и тот же addon content → одинаковые `.meta`/GUID (byte-identical mirror).

### Same-path-with-Core: merge vs conflict

- Layering по одному пути **поддерживается**: Core `Configs/System/chimeraInputCommon.conf` лежит на vanilla-пути и использует аддитивный `ActionRefs +{` на vanilla `CharacterGeneralContext`/`InventoryContext`; это работает только если движок **сливает** слои (иначе базового контекста не было бы).
- **Не доказано из source:** точное взаимодействие двух *не-vanilla* слоёв (Core + T4B) на одном пути. Это и есть остаточный «скрытый конфликт»: после Workbench-регистрации подтвердить, что действия Core **и** контекст T4B присутствуют (`IsContextActive == true`).
- Если конфликт проявится — альтернатива дать T4B-конфигу отдельный путь; но source не показывает, как `ActionContext` с отдельного пути попадает в ActionManager, поэтому общий путь — единственный пока подтверждённый маршрут.

**`.meta` не создавались, `.conf`/script/live/labs/Core не менялись.**

Status: **`T4B_CUSTOM_R_PHASE_B_GUID_REGISTRATION_PATH_AUDIT_COMPLETE`**. STOP.

---

## INPUT CONTEXT REGISTRATION AUDIT (owner runtime result 6025241031)

**Owner runtime:** `listener_registered=YES`, `weapon_gate_pass=YES`, `context_state active=false`, `RINPUT=NO`, vanilla `cmd1=YES` → `CUSTOM_R_CONTEXT_REGISTRATION_FAILURE`.

**Classification: `ROOT_CAUSE_PROVEN_MISSING_META`.**

### PRIMARY AUDIT — Core radiation detector R input (owner 6025438406 / 6025639819)

Полная трассировка по source (не по именам файлов):

| шаг | артефакт | доказательство |
|---|---|---|
| item prefab | `ARMST-PLATFORM---Core/Prefabs/Items/devices/armst_itm_atmos.et` (также radon/muha/voron/olimp/diatel; база `Flashlight_base.et`) | `ItemAnimationAttributes.AnimationAttachments → BindingName "Gadget"` |
| component | `ARMST_DETECTOR_COMPONENTS : SCR_GadgetComponent` (`Scripts/Game/Devices/ARMST_DETECTOR_COMPONENTS.c`) | `override void ActivateAction()` (L78) → `PerformActionDetector(...)` |
| actions manager | prefab `ActionsManagerComponent "{56A4B11C0BE428FF}"` | `ActionContexts { UserActionContext "{62EA972C3D31CF14}" { ContextName "Toggles" } }` + `additionalActions { ARMST_USER_DETECTOR_TOGGLE … }` |
| action | `ARMST_USER_DETECTOR_TOGGLE : ScriptedUserAction` (тот же файл, L492) | `PerformAction` toggle; `GetActionNameScript` → "On"/"Off"; `CanBeShownScript` → `charComp.GetInspect()` (L546) |
| physical binding | **vanilla `Gadget`** (`BindingName "Gadget"`) + inspect | **`keyboard:KC_R` в Core Scripts отсутствует** (grep = 0) |
| config | **нет** — в `Configs/System/chimeraInputCommon.conf` нет детекторного `Action`/`ActionContext`, контекста `Toggles` нет; в `keyBindingMenu.conf` детекторных записей нет | прочитан весь Core-конфиг |
| `AddActionListener` | **нет** | для детектора listener не добавляется |
| `ActivateContext` | **нет** (для детектора) | детектор идёт через vanilla gadget/inspect |

**Вывод:** `R` у Core-детектора — это **НЕ** custom addon `Action`/`ActionContext`. Это **vanilla `Gadget` binding** + `ScriptedUserAction` (`UserActionContext "Toggles"`) + `SCR_GadgetComponent.ActivateAction()`. Он **не требует** регистрации кастомного конфига и потому **не является** эталоном «как регистрируется кастомный addon ActionContext».

Настоящий Core-эталон **config-defined** контекста — `ARMST_Pda3DContext` / `ARMST_Open_PDA` в `.meta`-backed `chimeraInputCommon.conf` (Audit 1).

### Mandatory 1:1 — Core detector vs T4B

| Field | Core working detector | T4B custom-R | Difference | Relevant to `active=false`? |
|---|---|---|---|---|
| Action | `ARMST_USER_DETECTOR_TOGGLE` (`ScriptedUserAction`) | `ARMST_MP133_Reload` (config `Action`) | разная подсистема (UserAction vs ActionManager Action) | YES — T4B нужна регистрация конфига, детектору нет |
| ActionContext | `UserActionContext "Toggles"` (prefab) | `ActionContext ARMST_MP133_ReloadContext` (config) | разная подсистема | YES |
| physical binding | vanilla `BindingName "Gadget"` + inspect | `keyboard:KC_R` в конфиге | у детектора нет своего key | YES |
| Priority | n/a (нет) | `20000` | детектор priority не задаёт | partial |
| Flags | n/a (нет) | `Flags 0x6 0` | детектор flags не задаёт | partial |
| config file | **нет** (vanilla systems) | `Configs/System/chimeraInputCommon.conf` | детектору конфиг не нужен | YES — конфиг T4B unregistered |
| `.conf.meta` | n/a | **отсутствует** | T4B unregistered | **YES — root cause** |
| config GUID | n/a | null | T4B unregistered | **YES** |
| listener/callback | `ScriptedUserAction.PerformAction` (engine dispatch) | `AddActionListener("ARMST_MP133_Reload", DOWN, T4BRInputDown)` | разный dispatch | YES |
| context activation | implicit (gadget/inspect) | explicit `ActivateContext("ARMST_MP133_ReloadContext")` | T4B нужен зарегистрированный контекст | YES |
| conditional activation | yes (`GetInspect()`) | yes (T4B weapon gate) | похоже | no |
| coexist с vanilla reload R | yes (другой key/system) | ожидается (Phase B) | n/a | no |

**Ответ на primary question:** Core-детектор вообще **не создаёт** новый ActionManager-контекст — он использует уже зарегистрированные vanilla `Gadget`/inspect системы. T4B **создаёт** новый контекст, но его конфиг **unregistered** (`Setting null GUID`, нет `.meta`), поэтому `ARMST_MP133_ReloadContext` не попадает в ActionManager и `ActivateContext` оставляет `IsContextActive == false`. Детектор косвенно подтверждает требование регистрации: существуют только config-registered контексты, а конфиг T4B не зарегистрирован.

### Source proof chain

1. **On disk:** обе lab-конфиги не имеют `.meta`:
   - `ARMSTMP133T4B_InstalledMagProbe/Configs/System/chimeraInputCommon.conf` (1661 B) — `.meta` отсутствует;
   - `ARMSTMP133T4B_InstalledMagProbe/Configs/System/keyBindingMenu.conf` (791 B) — `.meta` отсутствует.
   Это единственные `.conf` под `Configs/System/`; все рабочие addon-конфиги (Core) несут `.meta`.

2. **Owner Workbench log** (`logs_2026-10-06_23-50-52/console.log`, L166–167; то же в `logs_2026-10-06_23-12-57`):
   ```
   RESOURCES (W): resource not registered: @"$ARMSTMP133T4BInstalledMag:Configs/System/chimeraInputCommon.conf". Setting null GUID
   RESOURCES (W): resource not registered: @"$ARMSTMP133T4BInstalledMag:Configs/System/keyBindingMenu.conf". Setting null GUID
   ```
   → `INPUT_CONFIG_NULL_GUID_WARNING = OBSERVED` теперь **объяснён**: файлы не зарегистрированы.

3. **ResourceDB decode** (`ARMSTMP133T4B_InstalledMagProbe/resourceDatabase.rdb`): запись `Configs/System/chimeraInputCommon.conf` хранит **нулевой GUID** (8 нулевых байт) и флаг «не зарегистрирован» (`0x04`); в `ARMST-PLATFORM---Core/resourceDatabase.rdb` та же запись хранит GUID `DB 64 D7 9A CF 84 51 79` (= `{795184CF9AD764DB}`, совпадает с Core `.meta`) и флаг «зарегистрирован» (`0x06`).

4. **Рабочий аналог (Core, тот же движок):** `ARMST-PLATFORM---Core/Configs/System/chimeraInputCommon.conf` + `.meta` (`Name "{795184CF9AD764DB}Configs/System/chimeraInputCommon.conf"`) зарегистрирован; его **собственный** контекст `ARMST_Pda3DContext` **успешно активируется в runtime** (`.../Scripts/Game/Devices/ARMST_PDA_COMPONENT.c:633`, `.../Camera/ARMST_CharacterCameraCustomPoint.c:122`) и сбрасывается (`ARMST_PDA_COMPONENT.c:406`). → addon-local custom `ActionContext` работает **тогда и только тогда**, когда его конфиг зарегистрирован.

5. **Следствие:** незарегистрированный конфиг не попадает в ActionManager → `ARMST_MP133_ReloadContext` не существует → `ActivateContext(...)` → `IsContextActive(...) == false` (наблюдено), `ARMST_MP133_Reload` не firing → `RINPUT = NO`.

### Audit 1 — рабочие примеры (addon-local custom input action)

| # | addon | config path | .meta | config GUID | discovery | Action | ActionContext | keyBinding entry |
|---|---|---|---|---|---|---|---|---|
| 0 (PRIMARY) | ARMST-PLATFORM---Core | **нет config** — prefab `armst_itm_atmos.et`: `BindingName "Gadget"` + `UserActionContext "Toggles"` + `ScriptedUserAction` | n/a | n/a | vanilla gadget/inspect (не ActionManager) | `ARMST_USER_DETECTOR_TOGGLE` (ScriptedUserAction) | `UserActionContext "Toggles"` | нет |
| 1 | ARMST-PLATFORM---Core | `Configs/System/chimeraInputCommon.conf` | YES | `{795184CF9AD764DB}` | merge по пути (config layer) | `ARMST_Open_PDA` | `CharacterGeneralContext` (vanilla, `ActionRefs +{`) | `{6672D1E0D9F7A127}` |
| 2 | ARMST-PLATFORM---Core | same | YES | same | same | `ARMST_Ragdoll` | `CharacterGeneralContext` | `{6672D62E4309E322}` |
| 3 | ARMST-PLATFORM---Core | same | YES | same | same | `ARMST_NVG_ACTION` | `CharacterGeneralContext` | `{69EB05063326D4D6}` |
| 4 | ARMST-PLATFORM---Core | same | YES | same | same | `ARMST_PDA_Touch` | **новый** `ARMST_Pda3DContext` (Priority 10000, plain `ActionRefs {}`) | нет |
| 5 | ARMST-PLATFORM---Core | same | YES | same | same | `Escape` (context-local) | `ARMST_Pda3DContext`/`PdaContext`/`BookContext`/`TraderContext` | n/a |

Ответы:
1. `Configs/System/*.conf` **merge'ятся между addons по пути** (Core `ActionRefs +{` на vanilla `CharacterGeneralContext`/`InventoryContext` имеет смысл только как overlay поверх существующей базы).
2. Файл **обязан быть зарегистрирован через `.meta`** — loose `.conf` без `.meta` даёт null GUID и не загружается (доказано выше).
3. Reference из `addon.gproj`/другого config **не нужен**: у lab `addon.gproj` нет config-блока, у Core тоже; discovery — по пути под `Configs/System/`.
4. **Нет** — loose `.conf` без GUID **не** участвует в ActionManager merge (пропускается с null-GUID warning).

### Audit 2 — наши текущие конфиги

| файл | SHA-256 | .meta exists | registered GUID | ResourceDB sees resource |
|---|---|---|---|---|
| `Configs/System/chimeraInputCommon.conf` | `71D4B2DD…CF4B` | **NO** | нет (null) | **NO** (`Setting null GUID`) |
| `Configs/System/keyBindingMenu.conf` | `368B51F7…C01D` | **NO** | нет (null) | **NO** (`Setting null GUID`) |

`INPUT_CONFIG_NULL_GUID_WARNING = OBSERVED` — теперь **root-caused** (unregistered), не безобидный артефакт.

### Audit 3 — `.meta` procedure (proof only; НЕ создано)

Формат (из Core `.meta`):
```
MetaFileClass {
 Name "{GUID}Configs/System/<file>"
 Configurations {
  CONFResourceClass PC { }
  CONFResourceClass XBOX_ONE : PC { }
  CONFResourceClass XBOX_SERIES : PC { }
  CONFResourceClass PS4 : PC { }
  CONFResourceClass PS5 : PC { }
  CONFResourceClass HEADLESS : PC { }
 }
}
```
- GUID генерирует **Workbench** (ResourceDB registration); 16-hex, глобально уникальный.
- Live и labs — **один и тот же addon content** → одинаковые `.meta`/GUID (byte-identical mirror).
- Риск: `Configs/System/chimeraInputCommon.conf` также поставляется **vanilla** и **Core** (`{795184CF9AD764DB}`). Lab-копия должна быть зарегистрирована и **не** переиспользовать GUID Core/vanilla. Сливается ли третий same-path слой так же, как Core поверх vanilla, — единственный остаточный пункт для runtime-подтверждения после регистрации.

### Audit 4 — ActionContext validation

| элемент | вердикт |
|---|---|
| `ActionContext ARMST_MP133_ReloadContext { … }` | валидная форма класса/имени |
| `ActionRefs +{ "ARMST_MP133_Reload" }` | **NON-CONFORMING** — Core использует `+{` только на **предсуществующих** контекстах (`CharacterGeneralContext`, `InventoryContext`); **новые** контексты Core — plain `ActionRefs { … }`. Для brand-new контекста additive-оператор не имеет базы. Не доказано фатально, но должно стать plain `ActionRefs { … }`. |
| `"ARMST_MP133_Reload"` ActionRef | валиден — совпадает с объявленным именем Action |
| `Priority 20000` | не доказано невалидно; выше максимума наблюдённого (10000, `ARMST_Pda3DContext`); смысл/предел не документированы |
| `Flags 0x6 0` | не доказано невалидно; наблюдён только на **override**-контекстах (`BookContext`, `TraderContext`), семантика не документирована |
| обязательный parent/base context | не нужен — у новых контекстов Core его нет |
| блокирует ли `Flags` активацию | **не доказано**; в source такого утверждения нет |

### Audit 5 — Action validation

| элемент | вердикт |
|---|---|
| `InputSource InputSourceValue "{B1C2D3E4F5A60001}" { Input "keyboard:KC_R" }` | валидная форма — как Core `ARMST_NVG_ACTION` (`InputSourceValue "{GUID}" { Input … }`) |
| `{B1C2D3E4F5A60001}` | config-object instance ID (тот же namespace, что object ID в `.et`), **не** resource GUID; должен быть глобально уникален; hand-made 16-hex допустим при уникальности (Core использует Workbench-сгенерированные) |
| `keyboard:KC_R` | валиден — Core биндит `KC_R` в `ARMST_CHECK_AMMO_ACTION`, `ARMST_LIGHT_RELOAD_ACTION`, `RotateItem`, `BuyItem` |

### Minimal proposed fix (НЕ выполняется)

1. Добавить `.meta` для обоих конфигов (Workbench-generated GUID, уникальный), live + labs byte-identical:
   - `Configs/System/chimeraInputCommon.conf.meta`
   - `Configs/System/keyBindingMenu.conf.meta`
2. Сменить `ActionRefs +{ … }` → `ActionRefs { … }` (конформность новым контекстам Core).
3. Файлы, которые изменились бы: два `.conf` (только `+{`→`{`) + два новых `.meta`, live + labs.
4. Затем owner recompile/run: подтвердить `context_state active=true` и `RINPUT`.

Остаточное (проверить после регистрации): same-path layer merge с vanilla/Core для `chimeraInputCommon.conf`.

**`.meta` не создавались, `.conf`/script не менялись, live/labs не тронуты. Read-only audit.**

Status: **`T4B_CUSTOM_R_PHASE_B_CONTEXT_REGISTRATION_AUDIT_COMPLETE`**. STOP.

---

## PHASE B INPUT ROUTING DIAGNOSTICS (owner result 6024714308)

**Owner runtime:** `PHASE_B_COMPILE_PASS`; `[ARMST-T4B-RINPUT]` НЕ появился, тогда как vanilla `cmd1`/`cmd5`/`cmd3` продолжали приходить →
`ARMST_R_RECEIVED = NO`, `VANILLA_RELOAD_RECEIVED = YES`, `CUSTOM_R_ROUTING_FAIL`.
Это не double-fire: custom-ветка просто не сообщила о нажатии `R`.

**Цель задачи:** только выяснить, на каком уровне теряется custom `R`. Reload/routing behaviour не меняется. **STAGING ONLY** — live/labs НЕ тронуты.

**Diagnostic source:** `Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c` (staged в `artifacts/astra-rebuild/stageCustomRInput/…`, byte-identical)
SHA-256 `C47569404920C9D8C70C331706FD164DC372A95C215FD0BCE3739E2F5633823F` (7259 B) — **установлен в live + labs**.

### Три диагностические границы (one-shot / transition-only)

| marker | где | ограничение повторов |
|---|---|---|
| `[ARMST-T4B-RCTX] phase=listener_registered action=ARMST_MP133_Reload` | сразу после `AddActionListener` | привязан к max-once регистрации (`m_bT4BRListenerActive`) |
| `[ARMST-T4B-RCTX] phase=weapon_gate_pass` | первый раз, когда проходит весь путь local→controlled→character→weapon-manager→current weapon→`ARMST_T4B_WeaponProbe` | bool `m_bT4BRWeaponGateLogged`, сбрасывается, когда current weapon больше не T4B |
| `[ARMST-T4B-RCTX] phase=context_state active=true\|false` | сразу после `ActivateContext(...)` | первое наблюдение + максимум одна смена на T4B-entry (`m_bT4BRContextStateKnown` + `m_bT4BRContextChangeLogged`) |

`[ARMST-T4B-RINPUT]` callback сохранён без изменения поведения (финальное доказательство firing).

### Context-state API — VERIFIED в installed SDK (Doxygen 1.8.0.13)

Source proof: `…\Arma Reforger Tools\Workbench\docs\EnfusionScriptAPI\html\interfaceInputManager.html` (и `interfaceActionManager.html`):

```
proto external bool ActivateContext ( string contextName, int duration=0)
proto external bool IsContextActive ( string contextName)
proto external void ResetContext ( string contextName)
```

→ **`CONTEXT_ACTIVE_QUERY = VERIFIED_IS_CONTEXT_ACTIVE`** — используется `IsContextActive("ARMST_MP133_ReloadContext")` после активации.

Нюанс поиска: `ArmaReforgerScriptAPIPublic` (публичный game API) **не** содержит `InputManager`/`IsContextActive`; движковый **EnfusionScriptAPI** содержит. `DeactivateContext` отсутствует в обоих; `ResetContext` существует, но запрещён → не вызывается.

### Классификация, которую это включает

```
listener_registered = NO                                   -> listener lifecycle failure
listener_registered = YES, weapon_gate_pass = NO           -> T4B weapon/current-weapon gate failure
listener_registered = YES, weapon_gate_pass = YES, context active = NO
                                                           -> context activation/config registration failure
listener_registered = YES, weapon_gate_pass = YES, context active = YES, RINPUT = NO
                                                           -> action/input-config registration или physical-key routing failure
RINPUT = YES, vanilla cmd1..6 = YES                        -> CUSTOM_R_DOUBLE_FIRE_CONFIRMED
RINPUT = YES, vanilla cmd1..6 = NONE                       -> CUSTOM_R_CONTEXT_FEASIBLE_WITH_VANILLA_SUPPRESSION
```

### Static verification (staged source)

```
existing RINPUT callback = unchanged
listener_registered marker = present (code occurrences = 1)
weapon_gate_pass marker    = present (code occurrences = 1)
context state marker       = VERIFIED_IS_CONTEXT_ACTIVE
per-frame Print spam       = 0 (все три маркера one-shot/transition-only)
DeactivateContext = 0
ResetContext = 0
reload APIs = 0
ammo writers = 0
mag writers = 0
chamber writers = 0
ASTRA/G3B2 = 0
input configs changed = NO
.meta created = NO
braces 21/21   parens 97/97
```

**Не менялось:** `Action ARMST_MP133_Reload`, `Context ARMST_MP133_ReloadContext`, `KC_R`, `Priority 20000`, `Flags 0x6 0`.
`INPUT_CONFIG_NULL_GUID_WARNING = OBSERVED` — остаётся гипотезой.

**Live/labs (установлено):** `Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c` = `C47569404920C9D8C70C331706FD164DC372A95C215FD0BCE3739E2F5633823F` (live = labs). Input configs не менялись.
**Workbench/Reforger/Game Mode/Animation Editor агентом не запускались; compile/runtime — owner-only.**

### Owner runtime — ожидаемые маркеры

```
[ARMST-T4B-RCTX] phase=listener_registered
[ARMST-T4B-RCTX] phase=weapon_gate_pass
[ARMST-T4B-RCTX] phase=context_state active=...
[ARMST-T4B-RINPUT]
```

Status: **`T4B_CUSTOM_R_PHASE_B_ROUTING_DIAG_INSTALLED_WAITING_OWNER_RUNTIME`**. STOP.

---

## 0. Lab-isolation — доказана как возможная (SOURCE)

**Ключевое доказательство:** `ARMST-PLATFORM---Core/Configs/System/chimeraInputCommon.conf` **переобъявляет** vanilla-контекст `CharacterGeneralContext` через **аддитивный** массив `ActionRefs +{ ... }`. Оператор `+{` имеет смысл только если базовый контекст уже существует → движок **сливает** (overlay) addon-овый `chimeraInputCommon.conf` с базовым (иначе Core-файл стёр бы vanilla-actions и сломал игру). → **lab-owned input config возможен без правки Core**.

Дополнительно (SOURCE): одна физическая клавиша `R` уже привязана к нескольким action'ам в разных контекстах — `RotateItem` (single `KC_R`, `InventoryContext`), `BuyItem` (single `KC_R`, `CharacterGeneralContext`), `ARMST_LIGHT_RELOAD_ACTION` (`R+LSHIFT`), `ARMST_CHECK_AMMO_ACTION` (`R+LCONTROL`) → контекст управляет тем, какой action сработает.

**Suppression (Priority/Flags) — UNRESOLVED:** базовый приоритет контекста и семантика `Flags` в SDK 1.8.0.13 не документированы. В staged-конфиге `Flags 0x6 0` скопирован из **существующего** контекста (`BookContext`/`TraderContext`), `Priority 20000` выбран выше максимального наблюдённого (10000). Это ровно то, что измеряет Phase B.

→ статус **PREPARED** (не BLOCKED).

---

## 1. Staged-файлы

| path | SHA-256 | bytes | назначение |
|---|---|---|---|
| `Configs/System/chimeraInputCommon.conf` | `71D4B2DD92B12BF93E76DEAF6B1B8CF763F2505D837981C7C469FF99D0DDCF4B` | 1661 | additive: `Action ARMST_MP133_Reload` (KC_R) + `ActionContext ARMST_MP133_ReloadContext` |
| `Configs/System/keyBindingMenu.conf` | `368B51F7862B245C730E40CA1C226B369F845C7E0DC9B604E822F2078BCDC01D` | 791 | key-binding entry для `ARMST_MP133_Reload` |
| `Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c` | `61F9671763889BBF933DDA33F4848A45FC3E08C1938597CF0250C599D71247AC` | 4807 | listener + per-frame context activation + `[ARMST-T4B-RINPUT]` log |

**Целевые live-пути (при GO):** те же три пути в `ARMSTMP133T4B_InstalledMagProbe/`.

---

## 2b. Corrections (owner review #6022566622)

| # | Проблема | Исправление |
|---|---|---|
| 1 | callback `T4BRWeaponChanged()` не совпадал с `ScriptInvoker<BaseWeaponComponent>` | сигнатура → `protected void T4BRWeaponChanged(BaseWeaponComponent newWeapon)`; аргумент **не** используется для мутаций |
| 2 | `Insert` без `Remove` | менеджер сохранён в `m_pT4BRWeaponManager`; в `OnDelete` — `m_pT4BRWeaponManager.m_OnWeaponChangeCompleteInvoker.Remove(T4BRWeaponChanged)` (Insert=1/Remove=1) |
| 3 | глобальный `AddActionListener`/context без local-gate | **proven pattern** (историческая ARMST lab + Core): `owner == SCR_PlayerController.GetLocalControlledEntity()` внутри `override protected void OnControlledByPlayer(IEntity owner, bool controlled)`; только local player делает `AddActionListener`/`ActivateContext`/`DeactivateContext`/лог |
| 4 | нет initial sync | после локальной регистрации — один `T4BRSyncContext()` (context активируется, если lab MP-133 уже current) |

**Cleanup path:** `OnControlledByPlayer` (loss of local control) → `T4BRTeardownLocal()` (Remove listener + DeactivateContext); `OnDelete` → `T4BRTeardownLocal()` + invoker `Remove`. Все снятия под флагами `m_bT4BRListenerActive`/`m_bT4BRContextActive`.

**Local-player proof:** `SCR_PlayerController.GetLocalControlledEntity()` — проверенный API (historical `ARMST_MP133_Lab_Character.c` L546/L609/L702; множество Core-файлов). Не изобретён.

**Initial sync:** 1 явный вызов `T4BRSyncContext()` в `OnControlledByPlayer` (local+controlled); +1 вызов из `T4BRWeaponChanged` (weapon change). Без `Update`/polling.

**Suppression остаётся UNRESOLVED:** `Priority 20000` / `Flags 0x6 0` не менялись (Phase B измеряет).

## 2c. Static verification (corrected)

```
callback sig T4BRWeaponChanged(BaseWeaponComponent) = 1
Insert = 1   Remove = 1
AddActionListener = 1   RemoveActionListener = 1
GetLocalControlledEntity (local gate) = 4
initial/weapon-change T4BRSyncContext call sites = 2 (+1 definition)
ActivateContext = 1   DeactivateContext = 2 (sync + teardown)
braces 21/21   parens 83/83
FORBIDDEN (writers/reload APIs/Update/timers) = 0
staged configs unchanged vs 50a1295 (diff empty)
```



| Проверка | Результат |
|---|---|
| action name (`ARMST_MP133_Reload`) | conf=5, kb=3, script=8 (вкл. комментарии) |
| `keyboard:KC_R` | conf=1 |
| context name | conf=2, script=4 |
| `ActivateContext` / `DeactivateContext` | 1 / 2 (вторая — delete-cleanup, под `m_bT4BRContextActive`) |
| `AddActionListener` / `RemoveActionListener` | 1 / 1 (сбалансировано) |
| `ARMST_T4B_WeaponProbe` gate | 3 (комментарий + 2 кода) |
| braces / parens | 15/15, 60/60 |
| FORBIDDEN (`SetAmmoCount`/`ReloadWeapon`/`ReloadWeaponWith`/`SetReloadWeapon`/`HandleWeaponReloading`/`HandleWeaponReloadingDefault`/`SetCurrentCommand`/`CallCommand`/`Update`/`HandleWeapons`/`CallLater`/mag spawn-attach-detach-despawn-release/`ClearChamber`) | **0** |

---

## 3. Lifecycle (corrected)

- `OnInit`: `m_pT4BRWeaponManager = GetWeaponManagerComponent()`; `Insert(T4BRWeaponChanged)` на `m_OnWeaponChangeCompleteInvoker`.
- `OnControlledByPlayer(owner, controlled)`: **local gate** `owner == SCR_PlayerController.GetLocalControlledEntity()`; если `controlled && local` → `AddActionListener("ARMST_MP133_Reload", DOWN, T4BRInputDown)` + **initial** `T4BRSyncContext()`; иначе → `T4BRTeardownLocal()`.
- `T4BRWeaponChanged(BaseWeaponComponent newWeapon)` (local-gated) → `T4BRSyncContext()`.
- `T4BRSyncContext()` (local-gated): `ActivateContext` если current weapon несёт `ARMST_T4B_WeaponProbe`, иначе `DeactivateContext`.
- `OnDelete`: `T4BRTeardownLocal()` + `Remove(T4BRWeaponChanged)` на сохранённом `m_pT4BRWeaponManager`.
- **Без** `Update`/polling/таймеров. Только local player регистрирует listener/context и пишет лог.

---

## 4. Phase B runtime test (описать, НЕ запускать)

**Test A — control weapon (не-MP-133):** нажать `R` → `[ARMST-T4B-RINPUT]` отсутствует; vanilla reload работает как раньше.
**Test B — canonical T4B MP-133:** нажать `R` один раз; смотреть одновременно `[ARMST-T4B-RINPUT]` и `[ARMST-T4B-CMDROUTE]`.
- SUCCESS: `ARMST_R_RECEIVED=YES` и vanilla `CMD_Weapon_Reload = NONE` → `CUSTOM_R_CONTEXT_FEASIBLE_WITH_VANILLA_SUPPRESSION`.
- DOUBLE-FIRE FAIL: `ARMST_R_RECEIVED=YES` и присутствует любой vanilla cmd1–6 → `CUSTOM_R_DOUBLE_FIRE_CONFIRMED`.
- ROUTING FAIL: `ARMST_R_RECEIVED=NO`.

**Не является fail:** если context забрал `R` и vanilla `cmd1` больше не появляется — ожидаемо; rack восстанавливать в Phase B **не** нужно.

---

## 5. Границы

Live/labs/Core/world/grid/inventory/prefab/ASTRA2/Tube3/handler/observer — не тронуты. Глобальный `HandleWeaponReloading` не добавляется; global storage override не добавляется; cmd7 не используется; Chungus не копируется. Ничего в live не устанавливалось.

Статус: **`T4B_CUSTOM_R_PHASE_B_V2_INSTALLED_WAITING_OWNER_COMPILE`**. STOP.

---

## 9. V2 INSTALL (owner GO_COMPILE_ONLY #6024198564)

Установлен **только V2 script** (byte-identical) в live + labs:

| файл | live SHA-256 | labs SHA-256 |
|---|---|---|
| `Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c` | `61F9671763889BBF933DDA33F4848A45FC3E08C1938597CF0250C599D71247AC` | same |

Input configs **не менялись**: `chimeraInputCommon.conf` `71D4B2DD…`, `keyBindingMenu.conf` `368B51F7…`.
Protected **не менялись**: handler `D5BA3052…`, weapon observer `7BE1D375…`, character observer `88BC52CB…`.

**Compile test выполняет владелец вручную** (агент Workbench/игру не запускает). Ожидается: V2 source не даёт compile errors → `PHASE_B_COMPILE_PASS`; иначе `PHASE_B_COMPILE_FAIL` с точной ошибкой из `ARMST_T4B_CustomRInputProbe.c`.
`INPUT_CONFIG_NULL_GUID_WARNING = OBSERVED` (наблюдение; `.meta` не создавались).

**R не нажималась, Game Mode не запускался.**

---

## 8. PLAYERCONTROLLER LIFECYCLE V2 (owner #6023891764)

**Blocker:** `override void OnDelete(IEntity owner)` на `SCR_PlayerController` — **не существует** (PlayerController/SCR_PlayerController не экспонируют `OnDelete`; есть `OnInit`/`OnUpdate`/`OnOwnershipChanged`/`OnControlledEntityChanged`/`OnDestroyed`). Удалён.

**Исправление (staged):**
- `override void OnDelete(...)` → **удалён** (`PlayerController OnDelete override = 0`).
- Cleanup listener'а → **VERIFIED_LIFECYCLE**: `override void OnOwnershipChanged(bool changing, bool becameOwner)` + `super.OnOwnershipChanged(changing, becameOwner)`; при `!becameOwner && m_bT4BRListenerActive` → `RemoveActionListener("ARMST_MP133_Reload", DOWN, T4BRInputDown)` + `m_bT4BRListenerActive = false`.
- Signature подтверждена SDK 1.8.0.13: `SCR_PlayerController.OnOwnershipChanged(bool changing, bool becameOwner)` переопределяет `PlayerController.OnOwnershipChanged(bool changing, bool becameOwner)` (void).
- Periodic activation (`SCR_PlayerController.OnUpdate`) — **без изменений**.
- Registration-once гарантирован флагом `m_bT4BRListenerActive` в `OnUpdate`.

**Static verification (V2):**
```
PlayerController OnDelete override = 0
DeactivateContext = 0
ResetContext = 0
ActivateContext = 1
super.OnUpdate = 1
local gate (m_bIsLocalPlayerController) = present
controlled entity path (GetControlledEntity) = present
ARMST_T4B_WeaponProbe gate = present
listener registration = max once (m_bT4BRListenerActive)
listener cleanup = VERIFIED_LIFECYCLE (OnOwnershipChanged, super present, RemoveActionListener path proven)
unsupported lifecycle callbacks = 0
reload APIs / ammo / mag / chamber / ASTRA / G3B2 = 0
braces 11/11   parens 65/65
```

**ResourceDB:** `INPUT_CONFIG_NULL_GUID_WARNING = OBSERVED` — только observation; `.meta`/input configs **не менялись**.

**Не менялось:** `Action = ARMST_MP133_Reload`, `Context = ARMST_MP133_ReloadContext`, `KC_R`, `Priority 20000`, `Flags 0x6 0`.

**Live/labs остаются на `9DBF75C4C9721C23DB7663C6F0094C0678D9047711DACAA913145326E289BA69`.**

**Следующий шаг (после re-review):** установить V2 source в live/labs и запустить Workbench **только ради compile PASS**; поведение `R` проверять лишь после чистой компиляции.

---

## 7. PHASE B COMPILE BLOCKER / CONTEXT LIFECYCLE CORRECTION (owner #6023499846)

**Compile blocker:** `InputManager.DeactivateContext` — **Undefined** в 1.8.0.13 (строки 75/128) → Game module не собрался. Инсталляция `c069038` в live была **непригодна** для runtime.

**Исправление (staged):**
- `DeactivateContext` удалён полностью (`= 0`); `ResetContext` не используется (`= 0`).
- Context lifecycle → **periodic activation**: `modded class SCR_PlayerController` + `override void OnUpdate(float timeSlice)` c `super.OnUpdate(timeSlice)` (PROVEN local pattern: Core `ARMST_PLAYER_WEIGHT_SYSTEN.c`). Каждый кадр: local gate (`m_bIsLocalPlayerController`) → controlled entity → character controller → weapon manager → current weapon → `ARMST_T4B_WeaponProbe` → `ActivateContext("ARMST_MP133_ReloadContext")`. Когда условие не выполняется — просто **не активируем** (без deactivate).
- Action listener оставлен log-only, balanced (`AddActionListener=1`/`RemoveActionListener=1`), local-only.
- Weapon-change invoker удалён полностью (не нужен при per-frame модели).
- Per-frame тело — **только** local gate + weapon probe + `ActivateContext`; никаких ammo/donor/reload/mag/chamber/ASTRA/G3B2/Print-спама.

**Static verification:**
```
DeactivateContext = 0
ResetContext = 0
ActivateContext = 1
m_bIsLocalPlayerController (local gate) = 2
ARMST_T4B_WeaponProbe gate = 2
super.OnUpdate = 1
AddActionListener = 1   RemoveActionListener = 1
modded class SCR_PlayerController = 1
braces 11/11   parens 64/64
reload APIs / ammo / mag / chamber / ASTRA / G3B2 / HandleWeapons / CallLater = 0
```

**ResourceDB warning (observation, НЕ fatal):**
`INPUT_CONFIG_NULL_GUID_WARNING = OBSERVED` для `Configs/System/chimeraInputCommon.conf` и `keyBindingMenu.conf`.
Проверка конвенции: рабочие Core-конфиги **имеют `.meta`** (`ARMST-PLATFORM---Core/Configs/System/chimeraInputCommon.conf.meta`, `keyBindingMenu.conf.meta` — `exists=True`), а lab-копии — **нет** (`exists=False`). Вероятная причина null-GUID. **Конфиги не меняю** до доказательства (компиляция + регистрация input проверяются runtime).

**Не менялось:** `Action = ARMST_MP133_Reload`, `Context = ARMST_MP133_ReloadContext`, `KC_R`, `Priority 20000`, `Flags 0x6 0` (suppression всё ещё UNRESOLVED до runtime).

**НЕ устанавливалось в live/labs в этой правке** — только staged correction + отчёт.

---

## 6. LIVE INSTALL (owner GO #6023003378, Workbench/editor/game закрыты)

Установлены ровно 3 staged-файла (byte-identical) в live + labs:

| файл | live SHA-256 | labs SHA-256 |
|---|---|---|
| `Configs/System/chimeraInputCommon.conf` | `71D4B2DD92B12BF93E76DEAF6B1B8CF763F2505D837981C7C469FF99D0DDCF4B` | same |
| `Configs/System/keyBindingMenu.conf` | `368B51F7862B245C730E40CA1C226B369F845C7E0DC9B604E822F2078BCDC01D` | same |
| `Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c` | `9DBF75C4C9721C23DB7663C6F0094C0678D9047711DACAA913145326E289BA69` | same |

Protected (unchanged): handler `D5BA3052…`, weapon observer `7BE1D375…`, character observer `88BC52CB…`.
Live addon resolved manually (no real Python in env; `addon_path.py` = Windows Store stub) and validated: `ARMSTMP133T4B_InstalledMagProbe/addon.gproj` ID `ARMSTMP133T4BInstalledMag`, GUID `B1C2D3E4F5061728`, `Prefabs/`+`Scripts/` present. **Core untouched.**

**Owner Phase-B test (не запускаю сам):** Test A (не-MP-133) → `R` → `[ARMST-T4B-RINPUT]` отсутствует, vanilla работает. Test B (canonical MP-133) → один `R` → смотреть `[ARMST-T4B-RINPUT]` + `[ARMST-T4B-CMDROUTE]`.
