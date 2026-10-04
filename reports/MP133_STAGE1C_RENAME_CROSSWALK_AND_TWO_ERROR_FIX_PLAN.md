# MP-133 Astra — Stage 1C: crosswalk переименований и план исправления двух ошибок

Статус: **T4B_STAGE1C_RENAME_CROSSWALK_AND_TWO_ERROR_FIX_PLAN**
Дата: 2026-10-04
Задание: Issue #34 [#5983304667](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5983304667); контекст [#5983290002](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5983290002), [#5983226050](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5983226050).
Исполнитель: ordinary T4b agent. **Режим: READ-ONLY.** Живой аддон и `labs/` не изменялись; Phase B — только предложение.
Защищено: native bolt/rack (`RackBoltAnim → Reload.ReloadActionBolt → P/W_MP133_Reload_Bolt.anm`, cmd1, `Weapon_Rack_Bolt`), fire/idle/inspection, tube, десять ANM + importer meta.

---

## 0. Preflight (выполнен)

- Workbench и все писатели: **закрыты** (процессов `Workbench/Reforger/Arma/Enfusion` нет). Проверено до чтения.
- Addon: `ARMSTMP133T4B_InstalledMagProbe`, ID `ARMSTMP133T4BInstalledMag`, GUID `B1C2D3E4F5061728`.
- Git: `t4b/installed-mag-probe` @ `181cff8`.
- Live-файлы перезаписаны Workbench **2026-10-04 21:53:50**; live ≠ `labs`/`03d8621`/`181cff8`.

Live SHA-256 (21:53:50):

| Файл | SHA-256 (12) | Размер |
|---|---|---|
| `MP133_Astra.ast` | `4268AE569718` | 1130 |
| `MP133_Astra.agf` | `CD7FF61DC200` | 33734 |
| `MP133_Astra_player.asi` | `F87EFFDFD1E9` | 14403 |
| `MP133_Astra_weapon.asi` | `47FBA70B7BB8` | 4835 |
| `MP133_Astra.agr` | `424632CFB784` | 2414 |
| `MP133_Astra.aw` | `D1057448BD1B` | 984 |

---

## 1. Точные две ошибки

**Ошибка 1 (GUI владельца):**
`Graph InsertShell: Invalid source 'AstraShell.InsertShell' in 'Source'.`
- Сайт: `ShellReloadSTM` состояние `InsertShell` (`agf` L28, `Child "InsertShell"`) → узел `AnimSrcNodeSource InsertShell` (`agf` L119).
- **На диске сейчас иное значение:** `agf` L121 `Source "Reload.InsertShell1"` (лишний суффикс `1`). То есть `AstraShell.InsertShell` — это состояние in-memory/устаревшего графа, а live-файл содержит другую, но **тоже невалидную** строку: строки AST `InsertShell1` не существует (в AST есть `InsertShell`). Корректная форма `Reload.InsertShell` присутствует в том же файле (L321, `InsertMagAnim`).
- Дополнительно: **коллизия имён** — состояние называется `InsertShell` (L28) и узел-источник тоже `InsertShell` (L119); суффикс `1` выглядит как артефакт авто-дизамбигуации редактора.

**Ошибка 2 (GUI владельца):**
`Graph MagReloadSTM Expr 'Start Time': Unknown anim 'Reload.Erc.Reload_InsertMag' (character 18).`
- Сайт: `agf` L347, переход `MagReloadSTM.RemoveMag → InsertMag`:
  `StartTime "GetEventTime(anim.Reload.Erc.Reload_InsertMag, \"BlendIn\")"`.
- AST-группа `Reload` больше **не объявляет** `Reload_InsertMag` (переименована/удалена), поэтому именованный anim-поиск не разрешается.

Обе ошибки — **нарушение ссылочной целостности**, внесённое переименованием нативных строк; ни одна из них не является «ошибкой фазы Astra» как таковой.

---

## 2. Crosswalk переименований (labs `181cff8` → live `21:53:50`)

AST `Reload` группа: удалены `Reload_InsertMag`, `Reload_RemoveMag`, `Safety`; остались `StartReload`, `GrabShell`, `InsertShell`, `CheckContinue`, `EndReload` (+ прочие native). Чистое следствие: три нативные идентичности **поглощены** именами Astra-фаз.

AGF-потребители (изменены владельцем):
| Старый Source | Новый Source (live) | Узел/потребитель |
|---|---|---|
| `Reload.Safety` | `Reload.StartReload` | `SafetyPose` (L136), `SemiPose` (L504), `AutoPose` (L509) |
| `Reload.Reload_InsertMag` | `Reload.InsertShell` | `InsertMagAnim` (L321) — native cmd2/3/4/5 |
| `Reload.Reload_RemoveMag` | `Reload.GrabShell` | `RemoveMagAnim` (L377) — native cmd4/5/6 |
| `Reload.InsertShell` | `Reload.InsertShell1` | `AnimSrcNodeSource InsertShell` (L121) ← **ошибка 1** |
| `Reload.ReloadActionBolt` | без изменений | `RackBoltAnim` (L357) — **защищено, корректно** |

ASI P/W (переименования с сохранением **нативных** ресурсов):
| Строка ASI (old→new) | P ресурс | W ресурс |
|---|---|---|
| `Reload_InsertMag` → `InsertShell` (Erc+Pne) | `{2E4A565E1D442CEA}...P_MP133_Reload_Inject.anm` | `{45B1772B8AFEAE47}...W_MP133_Reload_Inject.anm` |
| `Reload_RemoveMag` → `GrabShell` (Erc+Pne) | `{1A0174AF80728E7E}...P_MP133_Reload_Rem.anm` | `{FBC8FA7934FA4394}...W_MP133_Reload_Rem.anm` |
| `Safety` → `StartReload` (Erc+Pne) | `{877B9A1CF838AD9A}...p_rfl_ak74_erc_safety.anm` | `{60C8F1C1BEAA74D8}...w_rfl_ak74_erc_safety.anm` |
| `ReloadActionBolt` | `{2E4A565E1D442CE9}...P_MP133_Reload_Bolt.anm` | `{45B1772B8AFEAE46}...W_MP133_Reload_Bolt.anm` (**сохранён**) |
| `CheckContinue` | `{36BCB6296CAE5334}...P_Astra_CheckContinue.anm` ✔ | `{979C9964AD7956F5}...W_Astra_StartReload.anm` ✘ **misbinding** |
| `EndReload` | `{D1B33891A663548D}...P_Astra_EndReload.anm` ✔ | `{008B42BF7C535275}...W_Astra_EndReload.anm` ✔ |

**Осиротевшие импортированные клипы (больше нигде не используются):** `P_Astra_StartReload`, `P_Astra_GrabShell`, `P_Astra_InsertShell`, `W_Astra_GrabShell`, `W_Astra_InsertShell`, `W_Astra_CheckContinue`, а также `W_Astra_StartReload` (он подменён в слоте W `CheckContinue`). То есть «зелёные» `StartReload/GrabShell/InsertShell` играют **нативные/AK74** клипы, а не клипы Astra.

Замечание про «зелёный»: `InsertShell`/`GrabShell` играют `Reload_Inject`/`Reload_Rem`, несущие `Weapon_Spawn/Attach/Detach/DespawnMagazine`; `StartReload` играет AK74 safety. Зелёный цвет = строка сериализована, **не** = верный клип и **не** = безопасно для фиксированной трубы.

---

## 3. Root cause (в пределах доказанного)

1. **Ссылочная целостность native Reload нарушена переименованием:** `GetEventTime(anim.Reload.Erc.Reload_InsertMag,…)` (L347) и иные потребители ссылаются на удалённые AST-имена → ошибка 2.
2. **Коллизия имён/артефакт сериализации:** state `InsertShell` и source-узел `InsertShell`, `Source "Reload.InsertShell1"` → ошибка 1.
3. **Совместные идентичности:** `Reload.StartReload/GrabShell/InsertShell` теперь обслуживают **и** native-потребителей (`SafetyPose/SemiPose/AutoPose`, `InsertMagAnim`, `RemoveMagAnim`, cmd2–6), **и** `ShellReloadSTM`. Одним именем нельзя одновременно отдать нативный клип и клип Astra.
4. Механизм, по которому persistence сработал именно после переименования (**занятие существующей идентичности строки**), согласуется с тем, что новые AST-строки Workbench ранее вычищал. Точный механизм редактора — **UNPROVEN**.

---

## 4. Минимальное исправление (Phase B — ПРЕДЛОЖЕНИЕ, файлы не менялись)

### Вариант 1 — безопасный: вернуть нативные идентичности + distinct Astra-строки
Точные правки (для последующего отдельного одобрения):
- `MP133_Astra.ast` (группа `Reload`): добавить обратно `Reload_InsertMag`, `Reload_RemoveMag`, `Safety`; оставить `StartReload`, `GrabShell`, `InsertShell`, `CheckContinue`, `EndReload` как **отдельные** имена.
- `MP133_Astra.agf`: вернуть `SafetyPose/SemiPose/AutoPose` → `Source "Reload.Safety"`, `InsertMagAnim` → `Reload.Reload_InsertMag`, `RemoveMagAnim` → `Reload.Reload_RemoveMag`; `Expression` L347 вернётся к валидному `Reload_InsertMag`.
- `MP133_Astra.agf`: `AnimSrcNodeSource InsertShell` (L119) → `Source "Reload.InsertShell"`; при необходимости переименовать узел (например, `AstraInsertShell`), чтобы убрать коллизию с state `InsertShell`.
- Обе ASI: `Reload.Erc.<Phase>` для `StartReload/GrabShell/InsertShell` → импортированные `P/W_Astra_*.anm` (GUID `FCB314232D355753`/`979C9964AD7956F5`, `1D4C14261EFC54DB`/`E6534D7B659C59E5`, `D3868FB32BF75DEE`/`090759CC560C55F2`); W `CheckContinue` → `W_Astra_CheckContinue.anm` `{5B6872625F3454A4}`.
- Это форма состояния `03d8621`. **Риск:** Workbench ранее вычищал новые строки. Пока механизм не понят, Вариант 1 не гарантирует persistence → gate.

### Вариант 2 — только ссылочная заплатка (НЕ рекомендуется)
- L121 `Source "Reload.InsertShell1"` → `Source "Reload.InsertShell"`.
- L347 `anim.Reload.Erc.Reload_InsertMag` → `anim.Reload.Erc.InsertShell`.
- Обе ошибки исчезают, **но** фазы Astra остаются на нативных whole-mag клипах и делят идентичности с native → семантически неверно и небезопасно. Не предлагается как решение.

---

## 5. Конфликт и запрос решения (HARD STOP)

Корректная интеграция невозможна без ответа на один вопрос: **почему Workbench не сохраняет новые AST-строки, тогда как занятие существующей строковой идентичности сохраняется.** Пока это не разрешено, безопасный Вариант 1 упирается в persistence, а «минимальный» Вариант 2 отдаёт фазы Astra нативным клипам. Общие потребители (`InsertMagAnim`/`RemoveMagAnim`/`SafetyPose`, cmd2–6) делают прямое переименование небезопасным → требуется явное одобрение владельца.

Предлагаемый следующий шаг (owner-only, не агент): при закрытом Workbench и сохранённом/осознанно отменённом буфере — **один узкий UI-эксперимент**: добавить в группу `Reload` ровно **одну** новую distinct-строку штатным UI редактора (не ручной правкой текста), сохранить и проверить, сериализуется ли соответствующая ASI-строка после Save/Reopen. Это фальсифицируемо отвечает на вопрос о persistence. Результат определяет: применим Вариант 1 или нужен другой канал (импорт/регистрация).

---

## 6. Ворота приёмки владельца (после будущего патча)

1. Закрыть Workbench; один прогон: открыть existing T4b `MP133_Astra.aw`, пересобрать граф.
2. Обязательно: **ноль** Astra `Invalid source`; `Reload.StartReload/GrabShell/InsertShell/CheckContinue/EndReload` W/P указывают на **импортированные Astra** клипы и переживают Save + Reopen.
3. `Reload.ReloadActionBolt` / `RackBoltAnim` / cmd1 и событие `Weapon_Rack_Bolt` — без регресса.
4. Один ручной animation-only цикл `ASTRA_ShellRequest`; никаких native R/CMD5, никаких ammo-записей.

---

## 7. Сохранность

Только чтения. Живой аддон, `labs/`, десять ANM/meta, native bolt/fire/idle/inspection, Core/production/worlds, G3B2, bridge prefab — **не изменялись**. Единственное опубликованное изменение — этот отчёт.

---

## Приложение: снимок live-строк ASI (GUID → клип)

P: `CheckContinue→P_Astra_CheckContinue`; `EndReload→P_Astra_EndReload`; `InsertShell→P_MP133_Reload_Inject`; `GrabShell→P_MP133_Reload_Rem`; `StartReload→p_rfl_ak74_erc_safety`; `ReloadActionBolt→P_MP133_Reload_Bolt`.
W: `CheckContinue→W_Astra_StartReload` (misbound); `EndReload→W_Astra_EndReload`; `InsertShell→W_MP133_Reload_Inject`; `GrabShell→W_MP133_Reload_Rem`; `StartReload→w_rfl_ak74_erc_safety`; `ReloadActionBolt→W_MP133_Reload_Bolt`.
