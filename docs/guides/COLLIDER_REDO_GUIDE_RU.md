# Переделка коллайдеров аттачментов и магазинов (Blender + EBT) — ARMST Weapons

> Гайд по восстановлению коллайдеров в **29 используемых** FBX, которые сейчас **без коллайдеров**.
> Способ: **Blender GUI + Enfusion Blender Tools (EBT)**. Хедлесс-«хирургия» FBX запрещена — она ломает валидность коллайдеров и GUID-ссылки материалов.

---

## 0. Зачем это нужно

Из вики BI (`Weapon Optic Creation`):

> Accessories should have collider with two collision layers — **Weapon & FireGeo**.
> **Weapon** — физическое взаимодействие (столкновения с объектами).
> **FireGeo** — коллизии с пулями и **определение инвентарных действий**. *«Если вы не видите действий в игре — проверьте, что у предмета правильный Layer Preset».*
> Также: **Model Geometry** в `RigidBody` нужен, чтобы предмет можно было **подобрать с земли**.

Вывод: **нет коллайдера/слоя → нет контекста взаимодействия** (нельзя подобрать, прицепить, отцепить). Это же объясняет жалобу по L85 carry handle.

---

## 1. Правила (обязательные)

| Что | Требование |
|---|---|
| Слои коллайдера | Либо **один** `UCX`/`UBX` с пресетом **`WeaponFire`**, либо **два**: простой `UCX` с `Weapon` + подробный `UTM` с `FireGeo` |
| Имена объектов | `UCX_<имя>`, `UBX_<имя>`, `UTM_<имя>`, `USP_`, `UCS_`, `UCL_` — **без** Blender-суффиксов `.001`, `.022` |
| Game Material | `weapon_metal.gamemat`, `weapon_plastic.gamemat`, `weapon_wood.gamemat` (чтобы аттачмент не «ловил» каждую пулю) |
| Origin / Transform | корректные; при необходимости **Apply Transform** (Scale = 1, Rotation = 0) |
| RigidBody в префабе | `ModelGeometry 1` (иначе подобрать с земли нельзя) |

---

## 2. Предпосылки (критично!)

1. **Arma Reforger Workbench запущен** и аддон загружен.
   EBT берёт списки **Layer Preset** и **Game Material** из живого Workbench по сокету
   (`core/collider_cache.py` → `workbench.call_function(..., "LayerPresets", {})`).
   Без подключённого Workbench списки будут **пустыми**.
2. **Blender запущен в обычном режиме (GUI)** — **без** `--factory-startup` (иначе PySide6/EBT не поднимается).
3. EBT включён: `Edit → Preferences → Add-ons → EnfusionBlenderTools` (путь: `%APPDATA%\Blender Foundation\Blender\4.5\scripts\addons\EnfusionBlenderTools`).

---

## 3. Список FBX (29) — используемые меши без коллайдера

Список построен **по факту использования**: для каждого префаба берётся `MeshObject → Object` и проверяется наличие коллайдера в FBX. Неиспользуемые дубликаты исключены.

**Магазины**
```
Assets/Mag_12g/MagazineWell12ga.fbx
Assets/Mag_12g/MagazineWell12ga_blue.fbx
Assets/Weapons_NATO/HKG3/Hk3_Mag.fbx
Assets/Weapons_NATO/HKG36/HKG36_mag.fbx
Assets/Weapons_NATO/L1A1/L1A1_Mag.fbx
Assets/Weapons_NATO/L1A1/L1A1_Mag_big.fbx
Assets/Weapons_NATO/Sig SG 550/mag_sig550.fbx
Assets/Weapons_RUS/9a91/9a91_Magazine.fbx
Assets/Weapons_RUS/Apb/APB_magazine.fbx
Assets/Weapons_RUS/Groza/Groza_mag.fbx
Assets/Weapons_RUS/Kedr/Kedr_magazine.fbx
Assets/Weapons_RUS/TT/TT_magazines.fbx
Assets/Weapons_RUS/VAL/val_magazine.fbx
Assets/Weapons_RUS/VSS/vss_magazine.fbx
Assets/Weapons_RUS/akm/akm_magazine.fbx
Assets/Weapons_RUS/sok94/SOK_94_magazine.fbx
Assets/Weapons_RUS/sr2/SR2_mag.fbx
```

**Аттачменты**
```
Assets/addons/Dovetail/AKDovetailMount.fbx
Assets/addons/Dovetail/coll.fbx
Assets/addons/stocks/STOCK_SMALL.fbx
Assets/Weapons_NATO/HKG36/HKG36_Plank.fbx
Assets/Weapons_NATO/HKG36/Plank_Pika.fbx
Assets/Weapons_RUS/9a91/9a91_supprender.fbx
Assets/Weapons_RUS/AK74m/ak74m_acs.fbx
Assets/Weapons_RUS/AK74m/ak74m_acs2.fbx
Assets/Weapons_RUS/akm/akm_stock.fbx
```

**Оружие (корпус)**
```
Assets/Weapons_RUS/Aek_971/aek971.fbx
Assets/Weapons_RUS/Ak_105/Ak_105.fbx
Assets/Weapons_RUS/Groza/GROZA.fbx
```

> У `Assets/addons/SUSAT/Susat.fbx` коллайдер уже сделан (`UBX_Susat`).
> Эталон структуры: `Assets/Weapons_NATO/L86/L86.fbx` (`UCX_body`, `UTM_Weapon`).

---

## 4. Скрипт-помощник (автоматизация)

Файл: **`agent/colliders/ebt_add_colliders.py`** (в аддоне).

Запуск: Blender GUI (без `--factory-startup`) → вкладка **Scripting** → Open → `ebt_add_colliders.py` → **Run Script**.

Что делает на каждый меш: создаёт коллайдер (V-HACD «выпуклая оболочка» или бокс), ставит свойство объекта **`usage`** = `WeaponFire`, пытается назначить Game Material, убирает суффиксы `.001/.022`.

Настройки в шапке скрипта:

| Параметр | Значение |
|---|---|
| `MODE` | `"current"` — обработать текущую сцену; `"batch"` — пройти по 29 файлам (import → коллайдеры → export) |
| `DRY_RUN` | `True` (по умолчанию) — только план, ничего не пишет |
| `LAYER_PRESET` | `"WeaponFire"` или `"Weapon"` |
| `COLLIDER` | `"box"` (UBX, **по умолчанию** — вписан в габариты меша) или `"vhacd"` (выпуклая оболочка) |
| `BOX_SCALE` | множитель габаритов куба (`1.0` = точно по мешу) |
| `SINGLE_BOX` | `True` — **один куб на весь FBX** (нужно, когда модель состоит из нескольких мешей, напр. `ak74m`) |
| `FIX_EXISTING_COLLIDERS` | `True` (режим `current`) — не создавать, а **починить уже имеющиеся** коллайдеры (usage + материал + имена) |
| `EXPORT_VALIDATION` | `"CRITICAL"` (Permisive — не падать на `near-zero volume`/`short edges`) или `"ERROR"` (Normal) |
| `MESH_CLEANUP` | `True` — перед экспортом: merge by distance ≤ 0.1 мм (убирает рёбра < 0.03 мм) + пересчёт нормалей |
| `AUTO_SMOOTH` | `True` — Shade Auto Smooth (30°) после чистки |
| `HULLS` | число оболочек (1 = цельный коллайдер) |
| `BACKUP_DIR` | куда копировать FBX перед перезаписью |

> Для оптики и небольших аттачментов достаточно **одного UBX** (куб по габаритам меша) с пресетом `WeaponFire` — это дешевле V-HACD-оболочки и прямо разрешено вики BI.

**Порядок безопасной работы:**
1. Импортируйте **один** FBX через EBT (`File → Import → Import FBX (EBT)`).
2. Выделите нужный меш.
3. `MODE="current"`, `DRY_RUN=True` → Run Script → посмотрите лог (`%TEMP%\ebt_add_colliders.log`).
4. Убедитесь, что коллайдер создан там, где надо → `DRY_RUN=False` → Run Script.
5. Экспорт: `File → Export → Export FBX (EBT)` (или `MODE="batch"`).
6. Только после успешной проверки на одном файле — переходите к `MODE="batch"`.

> ⚠️ В batch-режиме обрабатываются **все меши сцены** — если в FBX есть служебные/высокополигональные объекты, сделайте их коллайдеры вручную (режим `current` + выделение).

---

## 5. Порядок действий вручную (на каждый FBX)

1. **Импорт**: `File → Import → Enfusion FBX` (`ebt.import_fbx`) — файл из аддона.
   (Или открыть рабочую сцену EBT, если она уже настроена под проект.)
2. Выделить **меш** (объект с геометрией).
3. **Добавить коллайдер**: `Add → EBT Objects → Collider →` нужный тип
   (или правый клик по объекту → `Edit EBT Objects → Collider → …`):
   - `Box (UBX)` — `ebt.collider_ubx`
   - `Convex (UCX)` — `ebt.collider_ucx`
   - `Sphere (USP)` — `ebt.collider_usp`
   - `Capsule (UCS)` — `ebt.collider_ucs`
   - `Cylinder (UCL)` — `ebt.collider_ucl`
   - `Triangle Mesh (UTM)` — `ebt.collider_utm`
   - `ebt.collider_vhacd` («Generate UCX Collider», панель `N → Enfusion Tools → Collider Tools`) — выпуклая оболочка из меша.
4. В параметрах операции задать:
   - **Layer Preset** → `WeaponFire` (один коллайдер) **или** `Weapon` (первый) + `FireGeo` (второй).
   - **Game Material** → `Weapon Metal` (для металла) / `Weapon Plastic` / `Weapon Wood`.
   Пресет пишется в свойство объекта **`usage`**, коллайдеры складываются в коллекцию **`Colliders`**.
5. **Имя** объекта привести к `UCX_<имя>` / `UBX_<имя>` / `UTM_<имя>` (убрать `.001`, `.022`).
6. **Трансформ**: `Object → Apply → All Transforms` (Scale 1, Rotation 0), origin — на месте.
7. **Экспорт**: `ebt.export_fbx` (НЕ `export_scene.fbx` — только EBT сохраняет GUID-ссылки материалов).
8. Повторить для следующего файла.

---

## 6. Справочник EBT (по коду аддона)

| Что | Значение |
|---|---|
| Операторы | `ebt.collider_ubx`, `ebt.collider_ucx`, `ebt.collider_usp`, `ebt.collider_ucs`, `ebt.collider_ucl`, `ebt.collider_utm`, `ebt.collider_vhacd` |
| Свойства операции | `layer_preset_item` (Layer Preset), `game_material_item` (Game Material) |
| Где хранится слой | custom property объекта **`usage`** |
| Коллекция коллайдеров | **`Colliders`** |
| Импорт/экспорт | `ebt.import_fbx`, `ebt.export_fbx` |
| Меню | `Add → EBT Objects → Collider`; правый клик → `Edit EBT Objects → Collider` |
| Панель V-HACD | `3D Viewport → N → Enfusion Tools → Collider Tools` |
| Источник пресетов | живой Workbench (`LayerPresets`, `GetGameMaterials`) |

---

## 7. Проверка и реимпорт

1. После экспорта — реимпорт ресурса в Workbench:
   либо **вручную** (Resource Browser → Reimport), либо через **RWTK-мост** (`bridge.reimport`, запрос в `%USERPROFILE%\...\profile\RWTKBridge\inbox`).
2. В логе Workbench не должно быть `Wrong GUID/name … AssignedMaterial` / `Material file not found` по этим мешам.
3. Проверить в игре: предмет **подбирается с земли** и показывает контекст (Attach / Detach / Pick up).

---

## 8. Чек-лист (копировать на каждый файл)

- [ ] FBX импортирован через `ebt.import_fbx`
- [ ] коллайдер добавлен (UBX/UCX/UTM/USP…)
- [ ] Layer Preset = `WeaponFire` **или** `Weapon` + `FireGeo`
- [ ] Game Material = `weapon_metal` (или plastic/wood)
- [ ] имя без `.001/.022`
- [ ] Apply Transform выполнен
- [ ] экспорт через `ebt.export_fbx`
- [ ] реимпорт в Workbench выполнен
- [ ] в логе нет ошибок материалов
- [ ] в игре есть взаимодействие

---

## 9. Бэкапы

Оригиналы (до правок): `…\ARMST_Backups\ARMST-PLATFORM---Weapons\colliders_fbx\` — исторический бэкап FBX.
Перед любым экспортом делайте копию текущего FBX туда же (или полагайтесь на git-историю аддона).
