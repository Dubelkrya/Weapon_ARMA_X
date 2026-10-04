# MP-133 Astra — Native Reload reuse audit & plan (Stage 1B Phase A)

Статус: **T4B_ASTRA_REUSE_BLOCKED_NEEDS_OWNER_DECISION**
Дата: 2026-10-04
Авторизация: Issue #34 [#5983170542](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5983170542) (Phase A read-only + bounded Phase B).
Исполнитель: ordinary T4b agent. Режим: **read-only** (Phase B не выполнялась).
Живой аддон: `ARMSTMP133T4B_InstalledMagProbe` (ID `ARMSTMP133T4BInstalledMag`); не изменялся.
Branch/HEAD: `t4b/installed-mag-probe` @ `03d8621`.

---

## 0. Итог одной строкой

Существующий граф **уже** встраивает Astra в основной маршрут `IdleReloadSTM` (нативный CMD1 rack сохранён и gate-ится), поэтому «второй системы» строить не нужно. Единственный фактический блокер — Workbench не регистрирует 3 из 5 новых строк `Reload.Erc.<Phase>` (и одну переназначает на неверный клип). Безопасного повторного использования существующих нативных источников не существует: каждый подходящий уже разрешённый источник либо обслуживается защищённым нативным потребителем, либо несёт нативные `Weapon_*Magazine`-события. → **Решение владельца**, правки не вносились.

---

## 1. Холодный старт: фактическое состояние

- **Workbench ЗАПУЩЕН** (`ArmaReforgerWorkbenchSteamDiag`, PID 13336). Возможны несохранённые буферы владельца → по правилу задания `STOP on ambiguous owner write state`. Phase B невозможна.
- Последняя правка Workbench: **2026-10-04 21:29:56** (после коммита `03d8621`) — сохранение владельца перезаписало live-файлы.
- Addon ID/GUID корректны: `ARMSTMP133T4BInstalledMag` / `B1C2D3E4F5061728`.
- ANM и `.anm.meta`: mtime 18:58, **не менялись** (импорт владельца цел).
- `.ast` и `.agf` live == Git `labs` (03d8621); `.agr`/`.aw` отличаются от snapshot только Workbench-нормализацией (вне Stage 1B).

Live-хэши (post-owner-save 21:29:56):

| Файл | live SHA-256 (первые 12) | vs labs 03d8621 |
|---|---|---|
| `MP133_Astra.ast` | `CF0141ECCA3F` | equal |
| `MP133_Astra.agf` | `1EA851EE13DA` | equal |
| `MP133_Astra.agr` | `424632CFB784` | differs (normalization) |
| `MP133_Astra.aw` | `D1057448BD1B` | differs (normalization) |
| `MP133_Astra_player.asi` | `084359EC7CD6` | differs (rows stripped) |
| `MP133_Astra_weapon.asi` | `FEEAC8D8264D` | differs (rows stripped + misassigned) |

---

## 2. Что показал post-save diff (главное доказательство)

Сравнение `labs` (мой in-place патч `03d8621`, все пять строк корректны) → live (сохранение владельца):

**P ASI** — удалены ровно три блока: `Reload.Erc.StartReload`, `Reload.Erc.GrabShell`, `Reload.Erc.InsertShell`. Остались корректные `Reload.Erc.CheckContinue → P_Astra_CheckContinue.anm` и `Reload.Erc.EndReload → P_Astra_EndReload.anm`.

**W ASI** — удалены те же три блока, НО дополнительно:

```
Reload.Erc.CheckContinue → "{979C9964AD7956F5}.../W_Astra_StartReload.anm"   ← НЕВЕРНЫЙ клип
Reload.Erc.EndReload     → "{008B42BF7C535275}.../W_Astra_EndReload.anm"     ← верный
```

то есть зелёная (по GUI) ячейка W `CheckContinue` фактически указывает на **чужой** клип `W_Astra_StartReload`; `W_Astra_CheckContinue.anm` (`{5B6872625F3454A4}`) в live не используется вовсе. Это подтверждает сообщение владельца о «смещении» назначений.

**Вывод:** индикатор green/gray в редакторе **не доказывает правильность** привязки. Live-состояние содержит артефакт редактора (прунинг + misassignment), а не просто отсутствие строк.

Что НЕ является причиной (проверено, read-only):

| Признак | StartReload | GrabShell | InsertShell | CheckContinue | EndReload |
|---|---|---|---|---|---|
| P/W `#numFrames` совпадают | 6/6 | 32/32 | 75/75 | 6/6 | 6/6 |
| Meta SourceProfile P/W | `A_UpperbodyADD_AllUp` / `A_Weapon_MagRelease_All` (одинаково у всех) | | | | |
| AST `Reload` содержит имена | да | да | да | да | да |
| AGF `Source "Reload.<Phase>"` | да | да | да | да | да |
| ASI строка была при `03d8621` | да | да | да | да | да |

Источник данных на диске корректен во всех пяти случаях; различие возникает только в момент принятия/сериализации инстанса Workbench. Root cause **UNPROVEN**; это не отсутствующий ANM и не расхождение длительностей P/W.

---

## 3. Эффективный маршрут и команды (SOURCE, `MP133_Astra.agf` + `MP133_V3_RELOAD_GRAPH_AUDIT.md`)

```
MasterControl
 └─ IdleReloadSTM
     ├─ Idle ──(ASTRA_ShellRequest && ASTRA_ShellEligible && !Stop && !FireStop && !Firing
     │          && WeaponInspectionState==0 && Stance==0 && !IsCommand(CMD_Weapon_Reload))──▶ AstraShell
     │     └─ AstraShell (Child AstraShellErcG: Group "Reload"/Column "Erc") ─▶ ShellReloadSTM
     │          StartReload → GrabShell → InsertShell → CheckContinue → {repeat | EndReload}
     │          └─ AstraShell ──RemainingTimeLess──▶ AstraWaitRelease ──!ASTRA_ShellRequest──▶ Idle
     └─ Idle ──((!ASTRA_ShellRequest || cmd==1) && IsCommand(CMD_Weapon_Reload)
                && !inRange(cmd,7,9) && cmd != -2)──▶ Buffer3 ──▶ Reload
           └─ WeaponReloadStanceSTM ─ Erc_Cro(Stance 0/1)→ReloadErcCroG | Pne(Stance 2)→ReloadPneG
                └─ WeaponReloadSTM (по CMD_Weapon_Reload)
                     cmd1→ReloadActionBolt(rack) | cmd2→NoMagReload | cmd3→NoMagNoBullet→Bolt
                     cmd4→MagReload→MagReloadSTM | cmd5→MagNoBullet→MagReloadSTM→Bolt | cmd6→RemoveMag
```

Факты:
- Astra-ветка **уже** встроена в основной `IdleReloadSTM` (не отдельная система); native CMD1 rack сохранён и при `ASTRA_ShellRequest` остаётся доступным (`|| cmd==1`), а cmd2–6 при активном запросе подавляются.
- Astra-путь ограничен `Stance == 0` (стоя) и `Column "Erc"`; `Pne` (лёжа) для shell-фаз не предусмотрен.
- `MagReloadSTM` — только `RemoveMag`/`InsertMag` (2 состояния); пять фаз в него не помещаются.
- Команды 7/8/9 veto на входе; cmd 10 проходит вход, но состояния нет.

---

## 4. Reuse-матрица существующих строк `Reload` (Erc/Pne)

Метки: **KEEP** = не трогать; **REUSE-CANDIDATE** = потенциально повторно использовать; **UNSAFE-REUSE** = делать нельзя; **UNKNOWN**.

| Строка AST (`Reload.*`) | Нативный потребитель | P / W клип (GUID) | Авторские события клипа | Pne? | Вывод |
|---|---|---|---|---|---|
| `ReloadActionBolt` | cmd1 rack (нативный short-R) | `P_MP133_Reload_Bolt` / `W_MP133_Reload_Bolt` | `Weapon_EnableFire`, `Weapon_Rack_Bolt` | да | **KEEP** (защищено) |
| `Reload_InsertMag` | cmd 2/3/4/5 (вставка магазина) | `P_MP133_Reload_Inject` / `W_MP133_Reload_Inject` | `Weapon_SpawnMagazine`, `Weapon_AttachMagazine`, `Weapon_MagRelease` | да | **UNSAFE-REUSE** (whole-mag attach) |
| `Reload_RemoveMag` | cmd 4/5/6 (извлечение магазина) | `P_MP133_Reload_Rem` / `W_MP133_Reload_Rem` | `Weapon_MagRelease`, `Weapon_DetachMagazine`, `Weapon_DespawnMagazine` | да | **UNSAFE-REUSE** (despawn tube) |
| `Fire`, `Trigger` | fire/queue | AK74 fire/trigger | fire | да | **KEEP** |
| `Idle`, `Idle_finger` | idle | | | да | **KEEP** |
| `Safety`, `Sight` | safety/sight | | | да | **KEEP** |
| `Switch_Mode_*`, `IKOffset`, `Finger_trigger_*`, `BoltPose` | mode/IK/finger | | | да | **KEEP** |
| Astra `StartReload` | Astra ShellReloadSTM | `P/W_Astra_StartReload` | `ASTRA_Shell_StartReload_P/W` | нет (Erc only) | **REUSE-CANDIDATE** (не регистрируется) |
| Astra `GrabShell` | Astra ShellReloadSTM | `P/W_Astra_GrabShell` | `ASTRA_Shell_GrabShell_P/W` | нет | **REUSE-CANDIDATE** |
| Astra `InsertShell` | Astra ShellReloadSTM | `P/W_Astra_InsertShell` | `ASTRA_Shell_InsertShell_P/W`, `ASTRA_ShellInsertCommit_P/W` | нет | **REUSE-CANDIDATE** |
| Astra `CheckContinue` | Astra ShellReloadSTM | `P/W_Astra_CheckContinue` | `ASTRA_Shell_CheckContinue_P/W` | нет | разрешается (но W live привязан неверно) |
| Astra `EndReload` | Astra ShellReloadSTM | `P/W_Astra_EndReload` | `ASTRA_Shell_EndReload/Stop/ReturnReady_P/W` | нет | разрешается корректно |

---

## 5. Ответ на вопрос «решит ли повторное использование уже разрешённого source ID?»

Да, формально это уберёт `Invalid source`, но **не безопасно**:

- Подставить вместо `Reload.StartReload` уже разрешённый `Reload.ReloadActionBolt` → источник зарегистрируется, но клип не тот и, главное, **native cmd1 rack уже потребляет эту строку** (общий потребитель) → конфликт.
- Подставить `Reload.Reload_InsertMag` / `Reload.Reload_RemoveMag` для `InsertShell` / `GrabShell` → источник зарегистрируется, но клипы несут `Weapon_Spawn/Attach/Detach/DespawnMagazine`, которые движок исполняет как **смену физического магазина** → разрушительно для фиксированной трубы (подтверждено нативно: cmd5 даёт `3/3→10/10`).
- Это «прячет» ошибку, ломая/рискуя нативными потребителями. **Не предлагается как исправление.**

Следовательно, безопасного прямого повторного использования существующих разрешённых источников для трёх падающих фаз **не существует**.

---

## 6. Почему интеграция заблокирована (HARD STOP)

1. **Ambiguous owner write state:** Workbench запущен; live ASI содержит артефакт сохранения (прунинг + misassignment). Любая полевая правка сейчас может быть перезаписана буфером редактора.
2. **Нет безопасного reuse-mapping** (§5): любой кандидат нарушает защищённого нативного потребителя или исполняет нативные magazine-события.
3. **Регистрация новых строк не поддаётся ручной правке:** три строки снова удалены, одна переназначена; root cause не доказан.
4. **Общие потребители неопределённы:** перенацеливание GroupSelect/источников уже один раз дало частичный результат (5→3), но не устранило проблему; дальнейшее «слепое» переименование запрещено.

Условия HARD STOP из задания выполнены → **правки не вносились**, публикуется матрица и план.

---

## 7. Два явных пути

- **Путь 1 (разрешённый, сохраняет натив):** Astra-ветка как сейчас — native CMD1 rack нетронут, cmd2–6 при `ASTRA_ShellRequest` подавлены, `ShellReloadSTM` (5 фаз) остаётся внутри основного `IdleReloadSTM`; prerequisite — регистрация пяти новых `Reload.Erc.<Phase>` строк в Workbench. Prone (Pne) для shell-фаз документируется как **неподдерживаемый**.
- **Путь 2 (НЕ авторизован):** переиспользовать/перепрофилировать `Reload_InsertMag`/`Reload_RemoveMag` (cmd 4/5/6) под shell-логику. Требует изменения native command routing / физических операций с магазином и снятия whole-mag семантики → HARD STOP, отдельное решение и ревью владельца.

---

## 8. Erc / Pne политика

`Erc` = стоя/присед, `Pne` = лёжа — это **колонки стойки**, а не фазы. Astra-ветка использует `Group "Reload"`, `Column "Erc"`, `Stance == 0`. Валидных prone shell-клипов нет; `Pne`-строки для shell-фаз не добавлялись и не должны молча подменяться старыми mag-swap клипами. Prone-поведение → **documented unsupported**.

---

## 9. Минимальный план следующего шага (для владельца)

1. Закрыть Workbench, сохранив/осознанно отменив буферы, затем сообщить точное состояние обеих ASI (это снимет `ambiguous owner write state`).
2. Отдельный узкий диагностический вопрос: **почему Workbench не регистрирует новые строки `Reload.Erc.<Phase>`, хотя AST-имена и ASI-строки корректны на диске** — через штатный UI редактора (добавление анимации в группу `Reload` средствами редактора), а не ручную правку текста. Сравнить с уже разрешёнными `CheckContinue`/`EndReload`.
3. Если регистрация через UI сработает — оставить текущую Astra-ветку (Путь 1) без нового reuse нативных клипов; если нет — зафиксировать как ограничение редактора/импорта и вернуться к обсуждению.
4. Не переиспользовать native mag-клипы, не менять CMD1/CMD5, не переимпортировать клипы, не создавать второй аддон/workspace.

Итоговый запрос решения: **`T4B_ASTRA_REUSE_BLOCKED_NEEDS_OWNER_DECISION`** — какой из двух путей разрешить и подтвердить закрытие Workbench для чистого состояния.

---

## 10. Сохранность и границы

В ходе Phase A выполнены только чтения файлов и Git. Живой аддон, Git `labs`, десять ANM и `.anm.meta`, скрипты, G3B2, bridge prefab, production/Core/worlds — **не изменялись**. Единственное опубликованное изменение — этот отчёт в knowledge-репозитории. Phase B не запускалась.
