# MP-133 Task #1 — AstraRebuild: реестр ресурсов и owner-GUI регистрация GUID

Статус: **STAGED_NOT_REGISTERED** (staged clean AGF готов; новые GUID — owner Workbench)
Задание: Issue #34 [#5984054477](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5984054477) (A: очистка orphan-нод; B: owner GUI дублирование).
База: `t4b/installed-mag-probe`.

---

## 0. Сделано в этом шаге (A)

Staged NEW AGF `labs/.../Assets/MP133_AstraRebuild/MP133_Astra.agf` очищен от legacy mag-swap orphan-нод:
удалены `WeaponReloadSTM`, `MagReloadSTM`, `WeaponReloadStanceSTM`, `InsertMagAnim`, `RemoveMagAnim`, `ReloadErcCroG`, `ReloadPneG` и устаревший `Blend T 1` (закрытый набор — внешних ссылок нет).

Проверка зависимостей/статическая (PASS):
- все 8 имён legacy = 0; `Blend T 1` = 0;
- сохранены `ReloadRouteSTM` (`Bolt→RackBoltAnim` CMD1, `Shell→AstraShellErcG→ShellReloadSTM`), `ReloadActionBolt`, 5 Astra источников; `ASTRA_ShellRequest` = 0;
- 0 неразрешённых `Child`/`FromState`/`ToState`; скобки 275/275.
- Оригинальный `Assets/MP133_AstraShellGraph` байт-идентичен (не менялся).

---

## 1. Что нужно от владельца (B) — только GUI в Workbench

Workbench выдаёт **уникальные** GUID только при собственной регистрации/дублировании; вручную GUID не изготавливаем.

1. Открыть проект T4b (`ARMSTMP133T4B_InstalledMagProbe`), **не** запускать игру.
2. Продублировать в `Assets/MP133_AstraRebuild/` ровно **6** ресурсов из `Assets/MP133_AstraShellGraph/`:
   - `MP133_Astra.aw`, `MP133_Astra.agr`, `MP133_Astra.agf`, `MP133_Astra.ast`, `MP133_Astra_player.asi`, `MP133_Astra_weapon.asi`.
   - **НЕ** дублировать 10 imported ANM/`.anm.meta` (они переиспользуются по ссылке) и не трогать оригинальную папку.
3. Запустить **register/reimport** новой копии тестового префаба: `Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et` — Workbench создаст его `.meta`/GUID.
4. Убедиться, что Workbench присвоил новые GUID (Resource Browser) и корректно переписал внутренние ссылки; **сохранить и ПОЛНОСТЬЮ закрыть Workbench**.
5. Прислать: список новых GUID для 6 ресурсов + префаба, либо скрин Resource Browser.

**STOP**, если Workbench не может безопасно дублировать связанный набор — не создавать дубликаты вручную.

---

## 2. Реестр ссылок (что должно быть связано после регистрации)

Источник → цель (после назначения новых GUID):

| Ресурс (новый) | Ссылается на |
|---|---|
| `Assets/MP133_AstraRebuild/MP133_Astra.aw` | AST (new), AGR (new), W ASI (new), P ASI (new) |
| `…/MP133_Astra.agr` | AST (new), AGF (new) |
| `…/MP133_Astra_player.asi` | AST (new) + 5 P Astra ANM (**исходные GUID, по ссылке**) |
| `…/MP133_Astra_weapon.asi` | AST (new) + 5 W Astra ANM (**исходные GUID, по ссылке**) |
| `Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et` | AGR (new) + W ASI (new) + P ASI (new) |

Исходные 10 ANM-ссылок (сохраняются намеренно, не дублируются):
`P/W_Astra_StartReload|GrabShell|InsertShell|CheckContinue|EndReload` (GUID: `FCB314232D355753`/`979C9964AD7956F5`, `1D4C14261EFC54DB`/`E6534D7B659C59E5`, `D3868FB32BF75DEE`/`090759CC560C55F2`, `36BCB6296CAE5334`/`5B6872625F3454A4`, `D1B33891A663548D`/`008B42BF7C535275`).

---

## 3. Следующий шаг агента (C, после owner-регистрации)

Используя **фактические** новые GUID из Workbench и актуальные live-файлы:
1. Перенести очищенный staged `MP133_Astra.agf` в `Assets/MP133_AstraRebuild/` (только новый AGF).
2. Прописать новые GUID в новые `.aw/.agr/.asi` и в новый тестовый префаб (`AnimGraph/AnimInstance/AnimInjection`), сохранив исходные ANM-ссылки.
3. Проверить уникальность GUID, замкнутость ссылок, отсутствие legacy-нод, сохранность CMD1/остального графа.
4. Синхронизировать принятые live-файлы в `Weapon_ARMA_X/labs/`, коммит/push, отчёт.

**Владелец:** открыть новый `MP133_AstraRebuild.aw` — ноль новых красных ошибок, 10 P/W строк назначены; animation-only preview одного цикла. Игровой R/CMD4/5 — только после отдельного решения по физической замене `Tube3` (engine-level UNRESOLVED).

Статус до регистрации: **STAGED_NOT_REGISTERED**. Целевой: `TASK1_ASTRAREBUILD_REGISTERED_NO_LEGACY_MAG_NODES_OWNER_ANIMATION_GATE`.
