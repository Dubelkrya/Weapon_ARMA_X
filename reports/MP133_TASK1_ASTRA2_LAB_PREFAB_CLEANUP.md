# MP-133 Task #1 — ASTRA2 lab cleanup (canonical prefab + obsolete prefab removal)

Статус: **ASTRA2_LAB_CLEANUP_PREPARED_WB_OPEN_STOP**
Дата: 2026-10-05
Задание: Issue #34 [#6000357139](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6000357139).
Режим: **read-only аудит + staged план**. **Live не изменялся** (write gate); на момент аудита Workbench был открыт, на момент записи отчёта — закрыт. Применение ждёт **явного разрешения владельца** (см. §6).

---

## 1. Инвентарь `Prefabs/Test/` (до)

| Prefab | GUID | Назначение/история | Inbound refs | Runtime dep? | Вердикт |
|---|---|---|---|---|---|
| `ARMST_T4B_AstraRebuild_TestWeapon.et` | `{B9E884F7E642E292}` | **канонический** lab MP-133 | Tube3Mag (mag), — | да (текущий тест) | **KEEP / repoint** |
| `ARMST_T4B_G3B2_Tube3Mag.et` | `{CD8091A2B3C4D5E6}` | фиксированная труба (dependency) | canonical prefab (MagazineTemplate) | да | **KEEP** |
| `ARMST_T4B_AstraV2_Bridge_TestWeapon.et` | `{29AAFC302B134E27}` | bridge AstraV2 | нет | нет | **DELETE** |
| `ARMST_T4B_G3B1_DonorDevice.et` | `{1A2B3C4D5E6F7081}` | G3B1 donor device | нет | нет | **DELETE** |
| `ARMST_T4B_G3B1_DonorMag.et` | `{C4D5E6F708192A3B}` | G3B1 donor mag | нет | нет | **DELETE** |
| `ARMST_T4B_G3B2_InventoryWide_TestWeapon.et` | `{233445566778899A}` | G3B2 OFF fixture | нет | нет | **DELETE** |
| `ARMST_T4B_G3B2_InventoryWide_WriteOn_TestWeapon.et` | `{78899AABBCDDEEFF}` | G3B2 WRITE-ON fixture | нет | нет | **DELETE** |
| `ARMST_T4B_G4A_OptionB_TestWeapon.et` | `{33918685A521E45A}` | G4A OptionB fixture | нет | нет | **DELETE** |
| `ARMST_T4B_TestWeapon.et` | `{C2D3E4F506172839}` | старый базовый lab | нет (только комментарий) | нет | **DELETE** |
| `ARMST_T4B_W3_CopiedWorkspace_TestWeapon.et` | `{E3693DABB8153C27}` | W3 copied-workspace | нет | нет | **HOLD** — live ≠ labs: незакоммиченная правка Workbench (rule 8) |

**Reference audit (read-only, вся папка addons):**
- ни один кандидат не ссылается из другого prefab/script/config (кроме собственного `.meta`);
- `resourceDatabase.rdb` перечисляет все (это **генерируемая** БД, не runtime-зависимость — пересоберётся Workbench);
- `ARMST_T4B_InstalledMagProbe.c` упоминает `ARMST_T4B_TestWeapon` **только в комментарии** (не код);
- **нет** placements в `.layer`/`.ent` ни в T4B, ни в других аддонах.

→ 7 из 8 кандидатов безопасны для удаления (вместе с их `.et.meta`). **W3 — исключение (HOLD)**: в live он переписан Workbench и указывает на `Assets/Weapons_RUS/Mp_133/Workspace/Lab_MP133.*`, тогда как committed labs-зеркало ещё указывает на `Assets/MP133_AstraShellGraph/MP133_Astra.*`. Это **незакоммиченная работа владельца** (rule 8) → удалять только после явного подтверждения (или сначала закоммитить live-состояние).

---

## 2. Канонический prefab — old → ASTRA2 (staged)

`ARMST_T4B_AstraRebuild_TestWeapon.et` сейчас ссылается на **старый** набор (root-путь `MP133_Astra.*`, фактически ресурсы в `old_pa/`):

| Поле | Было (old) | Стало (ASTRA2) |
|---|---|---|
| `AnimGraph` | `{7E087CCCBFB67045}…/MP133_Astra.agr` | `{AF2491EDB3449EED}…/MP133_Astra2.agr` |
| weapon `AnimInstance` | `{4CF7F797EC1FCA0E}…/MP133_Astra_weapon.asi` | `{5F61684997C53048}…/MP133_Astra2_weapon.asi` |
| injection `AnimGraph` | `{7E087CCCBFB67045}…/MP133_Astra.agr` | `{AF2491EDB3449EED}…/MP133_Astra2.agr` |
| player `AnimInstance` | `{B7A966A6741EAEE2}…/MP133_Astra_player.asi` | `{A43FF9780FC454A4}…/MP133_Astra2_player.asi` |

Сохранено без изменений: `ARMST_T4B_WeaponProbe`, `m_iT4BStartAmmo 2`, `MuzzleComponent`/`MagazineTemplate {CD8091A2B3C4D5E6}…/ARMST_T4B_G3B2_Tube3Mag.et`, класс `ARMST_T4B_AstraV2_WeaponAnimationComponent`, `BindingName "Weapon"`, `BindWithInjection 1`, наследование/модель/физмагазин.

Staged-файл: `Weapon_ARMA_X/artifacts/astra-rebuild/stageCleanup/ARMST_T4B_AstraRebuild_TestWeapon.et` (готов к применению после закрытия Workbench).

---

## 3. ASTRA resources (`Assets/MP133_AstraShellGraph_test/`)

- **Текущий ASTRA2:** `astra2.aw`, `MP133_Astra2.{agf,agr,ast}`, `MP133_Astra2_{player,weapon}.asi` (+ меты) — KEEP.
- **`old_pa/`:** `MP133_Astra.{agf,agr,ast}`, `MP133_AstraShellGraph_test.aw`, `MP133_Astra_{player,weapon}.asi` (+ меты). Их меты указывают путь на root, файлы лежат в `old_pa/` (GUID-resolve). Сейчас на них ссылается канонический prefab; после repoint станут **unreferenced**.
  - **В этой задаче НЕ удаляю** (по указанию: анимационные authoring-ресурсы не трогать без однозначного owner-intent). Оставляю как исторический донор; помечаю `unreferenced-after-repoint`.

---

## 4. Ошибки/предупреждения ASTRA2 lab

Известные `Missing Group Select`: `SafetyPose`, `SemiPose`, `AutoPose`, `SightPose`, `IdleFinger`, `BoltClosed` (источники `Source "Reload.Safety/Sight/Idle_finger/BoltPose"`).

**Аудит:** те же Pose-ноды с теми же `Source` присутствуют в **ORIGINAL** known-good AGF (L134/502/507/519/621/791). Значит, это **предсуществующие** warning'и, **не вызванные** cleanup'ом, и они есть в эталоне.

→ **Не исправляю** в этой задаче: доказанного правильного GroupSelect-обёртывания нет, а эталон имеет те же warning'и; спекулятивные dummy-ноды запрещены. Помечаю как `PRE_EXISTING_LEGACY_WARNINGS` (отдельная задача).

Прочих ASTRA2-специфичных ошибок, вызванных cleanup, не обнаружено (canonical prefab fix снимет dangling-ссылки на old-набор).

---

## 4b. Read-only proof (rule 7)

Сравнение live-addon ↔ committed labs-зеркало по игровым расширениям (`.et/.conf/.meta/.c/.layer`):

- сравнено файлов: **34**;
- изменено данным заданием: **0** → `GAMEPLAY_FILES_CHANGED_BY_CLEANUP=0`;
- предсуществующее расхождение live≠labs: **1** — `Prefabs/Test/ARMST_T4B_W3_CopiedWorkspace_TestWeapon.et` (незакоммиченная правка Workbench, **не** результат этого задания) → см. HOLD в §1;
- present-live-only (не зеркалируются в labs, в основном `.meta`): 32 — не игровые изменения.

Замечание: `python` в среде — заглушка Windows Store, поэтому `addon_path.py` / `check_repository_integrity.py` в этот раз **не запускались**; markdown-only изменение.

---

## 5. План применения (после закрытия Workbench + явного разрешения владельца)

1. Snapshot hashes (canonical prefab, Tube3Mag, ASTRA2 resources, V2 probe).
2. Применить staged canonical prefab (repoint old→ASTRA2).
3. Удалить 8 obsolete prefab'ов + их `.et.meta` (live + labs).
4. Проверки: canonical prefab содержит только ASTRA2 refs, ноль old `MP133_Astra.*`; Tube3 GUID/start ammo/WeaponProbe сохранены; ASTRA2 P ASI 5/5, W ASI 5/5; 10 ANM GUID неизменны; 9 legacy AGF-нод не вернулись; V2 probe без изменений; ноль dangling refs.
5. Sync в `labs/`, узкий commit.

**Заблокировано:** нет stale world/layer placements (проверено). `old_pa/` оставляю (не удаляю).

---

## 6. Статус

`ASTRA2_LAB_CLEANUP_PREPARED_WB_OPEN_STOP` — live не изменялся, план и staged canonical prefab готовы. Workbench сейчас закрыт, но **применение не начинаю до явного разрешения владельца** (gate из Issue #34).

Открытые вопросы к владельцу:
1. **W3**: подтвердить удаление, несмотря на незакоммиченную правку Workbench (или сначала закоммитить live-состояние). По умолчанию — **не удаляю**.
2. `old_pa/` — оставляю (не удаляю) в этой задаче.

После разрешения: применю §5 и выдам `ASTRA2_LAB_CLEANUP_OWNER_WB_VERIFY_PENDING`.
