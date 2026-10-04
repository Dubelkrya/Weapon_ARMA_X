# MP-133 Task #1 — Astra как основной путь перезарядки: BLOCKED (native routing)

Статус: **T4B_TASK1_BLOCKED_NATIVE_ROUTING**
Дата: 2026-10-04
Задание: Issue #34 [#5983639966](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5983639966) (owner priority task #1).
Режим: **READ-ONLY**. Живой аддон и `labs/` не изменялись; правки не вносились.
База: `t4b/installed-mag-probe` @ `d23417f`; `reports/MP133_STAGE1E_POST_SAVE_BINDINGS_PASS.md`.

---

## 0. Preflight

- Workbench/редактор/игра: **закрыты** (процессов `Workbench|Reforger|Arma|Enfusion` нет) — проверено перед анализом.
- Addon: `ARMSTMP133T4B_InstalledMagProbe`, ID `ARMSTMP133T4BInstalledMag`.
- Live re-saved Workbench в **22:36:38**; `MP133_Astra.ast` и обе `.asi` по-прежнему **байт-идентичны `88fa374`**; `MP133_Astra.agf` отличается только benign-нормализацией (`EditorPos` + отступы), логика идентична Stage 1E. Защищённый набор и 10 ANM/meta не менялись.

---

## 1. Цель и текущая схема

`MasterControl → IdleReloadSTM` содержит два пути:

- **Astra:** `Idle → AstraShell` при
  `ASTRA_ShellRequest && ASTRA_ShellEligible && !ASTRA_ShellStop && !ASTRA_FireStop && !Firing && WeaponInspectionState == 0 && Stance == 0 && !IsCommand(CMD_Weapon_Reload)`
  → `AstraShellErcG` (`Reload/Erc`) → `ShellReloadSTM`: `StartReload → GrabShell → InsertShell → CheckContinue → EndReload` (+ повтор `CheckContinue → GrabShell`), затем `AstraWaitRelease → Idle` при `!ASTRA_ShellRequest`.
- **Native:** `Idle → Buffer3 → Reload → WeaponReloadStanceSTM → WeaponReloadSTM → MagReloadSTM` (cmd2/3 insert, cmd4/5 remove+insert, cmd6 remove); cmd1 → `RackBoltAnim → Reload.ReloadActionBolt → P/W_MP133_Reload_Bolt` (`Weapon_Rack_Bolt`).

Текущий gate старого пути: `(!ASTRA_ShellRequest || cmd==1)`.

---

## 2. Блокирующая причина (доказано, read-only)

**Ничто не устанавливает `ASTRA_ShellRequest` (и `ASTRA_ShellRepeat/Stop/Eligible/FireStop`).**

- Поиск по всему аддону и всем установленным аддонам: единственные упоминания — в `MP133_Astra.agf` (условия) и `MP133_Astra.agr` (объявление переменных). Сеттера нет.
- Bridge-компонент `ARMST_T4B_AstraV2_WeaponAnimationComponent` — **только `OnAnimationEvent`** (диагностика); «No input hooks, subscriptions or ammo writes»; граф-переменные не пишет.
- `ARMST_T4B_WeaponAnimationComponent.OnCharacterCommand` — только **логирует** команды (`[ARMST_T4B-CMD]`), не маршрутизирует.
- Единственная запись — отдельный guarded user-action `+1` (`ARMST_T4B_AddRoundWeaponAction`), к Astra-пути отношения не имеет.

**Следствие:** Astra-путь достижим **только через Controls редактора**, а не из игрового ввода. Значит, чтобы Astra стала основным путём перезарядки по игровой команде, нужно **изменение маршрутизации ввода/команды** (script/prefab) — это выходит за рамки AGF и прямо подпадает под HARD STOP задания.

Дополнительно: даже графовый gate не доказывает остановку физической смены магазина движком. Известно (owner-runtime), что нативный CMD5 физически заменяет фиксированную Tube3; задание прямо запрещает утверждать, что «графовый gate сам по себе» предотвращает смену магазина. Это отдельный, нерешённый engine-level вопрос.

---

## 3. Почему безопасной graph-only переподключки для конечной цели нет

- Сделать Astra **primary по вводу** одним AGF-изменением нельзя: переменную `ASTRA_ShellRequest` никто не выставляет.
- «Отображение» игровой команды на Astra внутри графа потребовало бы одновременно снять текущее `!IsCommand(CMD_Weapon_Reload)` в условии входа и завести latch/hold для 5-фазного hold-цикла; при этом движок всё равно может выполнить mag-операции по команде — небезопасно и недоказуемо.
- Graph-only fail-close старого cmd2-6 (оставить только cmd1) **не достигает** цели «Astra primary» (игра не запускает Astra) и не доказывает engine-mag safety. Это возможный *частичный* шаг, но он не удовлетворяет конечному состоянию и меняет нативное поведение — по правилу HARD STOP не применялся.

Итог: корректное переподключение требует (b) input/command routing и (c) подтверждения engine-mag поведения. Оба вне полномочий этого задания → **STOP**.

---

## 4. Минимальное предложение для отдельной авторизации

**Шаг 1 (read-only, без изменений): доказательство engine-поведения.** Определить по SDK/логам, выполняет ли движок физическую замену/извлечение фиксированной Tube3 по CMD2-6 **независимо** от воспроизведения клипов `Reload_InsertMag/Reload_RemoveMag` (то есть от событий `Weapon_Spawn/Attach/Detach/DespawnMagazine`). Это решает, достаточно ли графового gate или нужен script-level запрет. Результат — отдельный отчёт, без правок.

**Шаг 2 (bounded script, отдельное одобрение): маршрутизация ввода в Astra.** На lab-компоненте анимации оружия связать и выставлять граф-переменные штатным SDK API:

- `BaseAnimPhysComponent.BindVariableBool(string pVariableName)` → `TAnimGraphVariable`;
- `BaseAnimPhysComponent.SetVariableBool(TAnimGraphVariable varIdx, bool value)` (+ `SetVariableFloat/Int`).

Связывать `ASTRA_ShellRequest`, `ASTRA_ShellRepeat`, `ASTRA_ShellStop`; лаб-действие/ввод выставляет `ShellRequest=true` (удержание на сессию), `ShellRepeat` — для повтора, сброс в 0 — выход. Сохранить `ReloadActionBolt`/cmd1, стрельбу, idle, inspection. Только lab-компонент, без Core/production.

**Шаг 3 (опционально, graph-only): fail-close старого cmd2-6** в лаборатории (оставить только cmd1), чтобы нативная mag-swap анимация не проигрывалась. Применять только вместе с Шагом 2 и без утверждений о engine-mag safety.

---

## 5. Сохранность и границы

Только чтения. Живой аддон, `labs/`, `.anm/.anm.meta`, `.agr/.ast/.asi`, скрипты, bridge prefab, G3B2, Core/production/worlds — **не изменялись**. R/CMD5 и ammo-записи не запускались. Опубликован только этот отчёт.

Возврат: **`T4B_TASK1_BLOCKED_NATIVE_ROUTING`** — блокирующее взаимодействие: отсутствие сеттера `ASTRA_ShellRequest` (Astra-путь только editor-only) плюс неподтверждённое engine-поведение фиксированного магазина по CMD2-6; минимальное следующее разрешение — Шаг 1 (read-only engine proof) и Шаг 2 (bounded input-routing script).
