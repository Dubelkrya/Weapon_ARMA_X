# MP-133 Astra — Stage 1E: post-save integrity audit (bindings survive)

Статус: **STAGE1E_POST_SAVE_BINDINGS_PASS_OWNER_ANIMATION_GATE**
Дата: 2026-10-04
Задание: Issue #34 [#5983499406](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5983499406) (owner authorization), база [#5983436009](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5983436009).
Режим: **READ-ONLY**. Живой аддон и `labs/` не изменялись; опубликован только этот отчёт.
Проверяемый источник: published `88fa374` на `t4b/installed-mag-probe`.

---

## 0. Preflight

- Workbench/редактор/игра и все писатели: **полностью закрыты** (`Get-Process` по `Workbench|Reforger|Arma|Enfusion` — пусто) на момент проверки. Ранее, во время первого прохода, редактор был активен (PID 2936, `Enfusion Workbench - ARMST MP133 T4B Installed Mag Probe`) — тогда проверка была остановлена; владелец закрыл его.
- Addon: `ARMSTMP133T4B_InstalledMagProbe`, ID `ARMSTMP133T4BInstalledMag`, GUID `B1C2D3E4F5061728`.
- Git: `t4b/installed-mag-probe` @ `88fa374`.

---

## 1. Live vs `88fa374`

| Файл | live SHA-256 (16) | labs `88fa374` | Итог |
|---|---|---|---|
| `MP133_Astra.ast` | `C95CF76EAF026A23` | same | **идентичен** |
| `MP133_Astra_player.asi` | `DC9C51052944FBE3` | same | **идентичен** |
| `MP133_Astra_weapon.asi` | `6D966498E1460BDF` | same | **идентичен** |
| `MP133_Astra.agf` | `9C948816C0816D7F` | `163C2EB360F20F68` | отличается — см. §2 |
| `MP133_Astra.agr` | `424632CFB784CCDE` | `6C08181FF2E5E846` | отличается — давняя Workbench-нормализация |
| `MP133_Astra.aw` | `D1057448BD1B2160` | `4A4BF5A5E93CA5E1` | отличается — давняя Workbench-нормализация |

Все live-граф-файлы имеют mtime `2026-10-04 22:16:33` (сохранение владельца).

---

## 2. Характер расхождения AGF (точно, без логических изменений)

Diff `labs 88fa374 → live 22:16:33` содержит **только**:
- изменённые координаты `EditorPos` у узлов Astra-ветки (`AstraShellErcG`, `ShellReloadSTM` и его состояний, пяти `Astra*` source-узлов) — раскладка на канвасе редактора;
- нормализацию отступов у вставленных Stage 1D строк (6 → 5 пробелов) для `SafetyPose` / `SemiPose` / `AutoPose` / `InsertMagAnim` / `RemoveMagAnim`.

Ни одного изменения в `Source`, `Child`, `Group`, `Column`, `StartCondition`, `StartTime` нет. Семантические проверки (§4) подтверждают идентичность логики.

---

## 3. Пять фаз Astra (Erc; Pne не назначен)

| Фаза | Player ASI | Weapon ASI | Pne |
|---|---|---|---|
| StartReload | `{FCB314232D355753}…/P_Astra_StartReload.anm` | `{979C9964AD7956F5}…/W_Astra_StartReload.anm` | отсутствует |
| GrabShell | `{1D4C14261EFC54DB}…/P_Astra_GrabShell.anm` | `{E6534D7B659C59E5}…/W_Astra_GrabShell.anm` | отсутствует |
| InsertShell | `{D3868FB32BF75DEE}…/P_Astra_InsertShell.anm` | `{090759CC560C55F2}…/W_Astra_InsertShell.anm` | отсутствует |
| CheckContinue | `{36BCB6296CAE5334}…/P_Astra_CheckContinue.anm` | `{5B6872625F3454A4}…/W_Astra_CheckContinue.anm` | отсутствует |
| EndReload | `{D1B33891A663548D}…/P_Astra_EndReload.anm` | `{008B42BF7C535275}…/W_Astra_EndReload.anm` | отсутствует |

`W CheckContinue` больше **не** указывает на `W_Astra_StartReload` — прежнее misbinding исправлено. Дубликатов ключей ASI нет (`Pdups=[]`, `Wdups=[]`).

---

## 4. Штатные источники и граф

- Native `Safety` / `Reload_InsertMag` / `Reload_RemoveMag` — присутствуют для **Erc и Pne** с нативными клипами (`p/w_rfl_ak74_erc_safety`, `P/W_MP133_Reload_Inject`, `P/W_MP133_Reload_Rem`).
- **`ReloadActionBolt` → P/W `P_MP133_Reload_Bolt.anm` / `W_MP133_Reload_Bolt.anm` — без изменений**; `RackBoltAnim → Source "Reload.ReloadActionBolt"` цел (cmd1, `Weapon_Rack_Bolt`).
- AST: группа `Reload` — 22 анимации, дубликатов нет; присутствуют `Safety`, `Reload_InsertMag`, `Reload_RemoveMag`, `ReloadActionBolt` и пять distinct-фаз.
- AGF: `unresolved Sources = []`; `Reload.InsertShell1 = 0`; `AstraShell.* = 0`; `GetEventTime(anim.Reload.Erc.Reload_InsertMag, "BlendIn") = 1`; узел `AstraInsertShell` есть, `Child "AstraInsertShell"` корректен; `InsertMagAnim → Reload.Reload_InsertMag`, `RemoveMagAnim → Reload.Reload_RemoveMag`; `SafetyPose/SemiPose/AutoPose → Reload.Safety`; `GroupSelect Reload/Erc` на месте.

---

## 5. Защищённые ресурсы

- Защищённый набор **90 файлов** (всё, кроме четырёх правленых граф-файлов): `PROTECTED_FILES_UNCHANGED=1` (сравнение с манифестом начала Stage 1D).
- Десять `ANM` + десять импортерских `.anm.meta`: **checked=20, changed=0** (mtime 18:58, оригинальные).
- Скрипты, G3B2, bridge prefab (`{29AAFC302B134E27}`), `.agr/.aw` по существу не менялись.

---

## 6. Разделение уровней доказательства

- **OWNER GUI PASS (reported):** Workbench загрузил Stage 1D с нулём красных ошибок; назначения сохранились (скриншот).
- **VERIFIED ON-DISK PASS (this report, read-only):** все пять пар P/W Astra, нативные строки, `Reload_Bolt`, разрешаемость графа, целостность ANM/meta и защищённого набора — подтверждены по файлам.
- **Семь legacy warnings** `Missing Group Select` относятся к прежним нативным pose/finger/bolt-узлам, **вне** scope Astra, отдельно и в этом отчёте не переоценивались.
- **Heads-up:** индикатор green/gray редактора не является доказательством корректного клипа (в прошлых прогонах зелёная ячейка W `CheckContinue` была перепривязана). Здесь корректность подтверждена **по GUID на диске**, а не по цвету.

---

## 7. Границы и следующий шаг

Ничего не исправлялось и не перезаписывалось; `labs/` не менялся (Workbench-нормализация не «подтягивалась» в Git). Опубликован только отчёт.

Дальше — **за владельцем**: один ручной animation-only цикл `ASTRA_ShellRequest` в редакторе, наблюдение порядка `StartReload → GrabShell → InsertShell → CheckContinue → EndReload`, ветки повтора `CheckContinue → GrabShell`, завершения/прерывания и P/W-синхронизации; фиксировать фактические состояния/ошибки. Если безопасный animation-only триггер недоступен — сообщить блокер и предложить non-mutating способ проверки, не запуская gameplay-перезарядку. Обычный R/CMD5 и G3B2/ammo-записи — по-прежнему запрещены.
