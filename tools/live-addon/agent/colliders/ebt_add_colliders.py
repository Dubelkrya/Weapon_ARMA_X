# -*- coding: utf-8 -*-
"""
EBT Add Colliders — скрипт для Blender GUI (Enfusion Blender Tools).

ЗАПУСК
  Blender GUI (БЕЗ --factory-startup!) -> вкладка "Scripting" -> Open -> этот файл -> Run Script.
  Workbench должен быть ЗАПУЩЕН и аддон загружен: EBT берёт списки Layer Preset и Game Material
  из живого Workbench по сокету. Без этого импорт/экспорт EBT и назначение материала работать не будут.

РЕЖИМЫ
  MODE = "current"  — обработать ТЕКУЩУЮ сцену (рекомендуется для проверки на ОДНОМ файле).
  MODE = "batch"    — пройти по списку FILES: очистить сцену -> import -> коллайдеры -> export.

ЧТО ДЕЛАЕТ (на каждый меш)
  1) создаёт коллайдер: выпуклую оболочку (V-HACD, COLLIDER="vhacd") или бокс (COLLIDER="box");
  2) ставит объекту свойство "usage" = LAYER_PRESET;
  3) назначает Game Material (если удалось получить из Workbench);
  4) в batch-режиме — экспортирует FBX через ebt.export_fbx (перед этим делает бэкап).

БЕЗОПАСНОСТЬ
  * DRY_RUN=True по умолчанию — НА ДИСК ничего не пишется (экспорт пропущен). Коллайдеры в сцене
    всё равно создаются (это не разрушительно, файл не меняется) — их можно осмотреть/подправить.
    Для экспорта поставь DRY_RUN=False.
  * Каждый FBX перед перезаписью копируется в BACKUP_DIR.
  * Лог: %TEMP%\\ebt_add_colliders.log

ВАЖНО
  * КОЛЛАЙДЕР ДЕЛАЕТСЯ НА ВЫДЕЛЕННЫЕ объекты (если ничего не выделено — на все меши сцены, с предупреждением).
    Всегда проверяйте, что выделен именно нужный меш (а не служебный/высокополигональный).
  * LOD-копии (имена вида *_LOD1) пропускаются.
  * Имена без Blender-суффиксов .001/.022 — скрипт их убирает.
"""

import os
import re
import time
import shutil
import datetime
import traceback

import bpy

SCRIPT_VERSION = "v9-2026-09-22"

# ============================ НАСТРОЙКИ ============================
MODE = os.environ.get("EBT_COLL_MODE", "current")            # "current" | "batch"
DRY_RUN = os.environ.get("EBT_COLL_DRY", "1") == "1"          # True -> на диск ничего не пишется

ADDON_ROOT = r"C:\Users\yshky\OneDrive\Документы\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons"
REL_FILES = [                    # 29 ИСПОЛЬЗУЕМЫХ мешей без коллайдера (проверено по префабам)
    r"Assets\Mag_12g\MagazineWell12ga.fbx",
    r"Assets\Mag_12g\MagazineWell12ga_blue.fbx",
    r"Assets\Weapons_NATO\HKG3\Hk3_Mag.fbx",
    r"Assets\Weapons_NATO\HKG36\HKG36_Plank.fbx",
    r"Assets\Weapons_NATO\HKG36\HKG36_mag.fbx",
    r"Assets\Weapons_NATO\HKG36\Plank_Pika.fbx",
    r"Assets\Weapons_NATO\L1A1\L1A1_Mag.fbx",
    r"Assets\Weapons_NATO\L1A1\L1A1_Mag_big.fbx",
    r"Assets\Weapons_NATO\Sig SG 550\mag_sig550.fbx",
    r"Assets\Weapons_RUS\9a91\9a91_Magazine.fbx",
    r"Assets\Weapons_RUS\9a91\9a91_supprender.fbx",
    r"Assets\Weapons_RUS\AK74m\ak74m_acs.fbx",
    r"Assets\Weapons_RUS\AK74m\ak74m_acs2.fbx",
    r"Assets\Weapons_RUS\Aek_971\aek971.fbx",
    r"Assets\Weapons_RUS\Ak_105\Ak_105.fbx",
    r"Assets\Weapons_RUS\Apb\APB_magazine.fbx",
    r"Assets\Weapons_RUS\Groza\GROZA.fbx",
    r"Assets\Weapons_RUS\Groza\Groza_mag.fbx",
    r"Assets\Weapons_RUS\Kedr\Kedr_magazine.fbx",
    r"Assets\Weapons_RUS\TT\TT_magazines.fbx",
    r"Assets\Weapons_RUS\VAL\val_magazine.fbx",
    r"Assets\Weapons_RUS\VSS\vss_magazine.fbx",
    r"Assets\Weapons_RUS\akm\akm_magazine.fbx",
    r"Assets\Weapons_RUS\akm\akm_stock.fbx",
    r"Assets\Weapons_RUS\sok94\SOK_94_magazine.fbx",
    r"Assets\Weapons_RUS\sr2\SR2_mag.fbx",
    r"Assets\addons\Dovetail\AKDovetailMount.fbx",
    r"Assets\addons\Dovetail\coll.fbx",
    r"Assets\addons\stocks\STOCK_SMALL.fbx",
]
FILES = [os.path.join(ADDON_ROOT, p) for p in REL_FILES]
ONLY = [x.strip().lower() for x in os.environ.get("EBT_COLL_ONLY", "").split(",") if x.strip()]
EXTRA_FILES = [x.strip() for x in os.environ.get("EBT_COLL_FILES", "").split(";") if x.strip()]
EXPORT_VALIDATION = os.environ.get("EBT_COLL_VALIDATION", "CRITICAL")  # "CRITICAL"(Permisive) | "ERROR"(Normal)
MESH_CLEANUP = os.environ.get("EBT_COLL_CLEANUP", "1") == "1"   # merge by distance + пересчёт нормалей
CLEANUP_MERGE_DIST = 0.0001     # 0.1 мм: убирает рёбра короче 0.03 мм (порог EBT), визуально незаметно
AUTO_SMOOTH = os.environ.get("EBT_COLL_SMOOTH", "1") == "1"     # Shade Auto Smooth после чистки

LAYER_PRESET = "WeaponFire"      # "WeaponFire" (один коллайдер) либо "Weapon" (+ отдельный "FireGeo")
GAME_MATERIAL_ENUM_KEY = "Weapon Metal"   # ключ enum EBT; "" -> не трогать материал
COLLIDER = os.environ.get("EBT_COLL_TYPE", "box")            # "box" (UBX, вписан в габариты) | "vhacd" (выпуклая оболочка из меша)
BOX_SCALE = 1.0                  # множитель габаритов куба (напр. 0.9 — чуть меньше меша)
SINGLE_BOX = True                # True — один куб на весь FBX (для моделей из нескольких частей)
FIX_EXISTING_COLLIDERS = os.environ.get("EBT_COLL_FIX", "0") == "1"   # True (режим current) — не создавать, а починить имеющиеся коллайдеры
HULLS = 1                        # число выпуклых оболочек для V-HACD (1 = цельный коллайдер)

BACKUP_DIR = r"C:\Users\yshky\OneDrive\Документы\ARMST_Backups\ARMST-PLATFORM---Weapons\colliders_new"
LOG_PATH = os.path.join(os.environ.get("TEMP", "."), "ebt_add_colliders.log")

COLLIDER_PREFIXES = ("UCX_", "UBX_", "USP_", "UCS_", "UCL_", "UTM_", "BSP_", "OCC_")
# ==================================================================

def log(msg):
    line = "%s  %s" % (datetime.datetime.now().strftime("%H:%M:%S"), msg)
    print("[EBT-COLL] " + line)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def is_collider(name):
    return name.startswith(COLLIDER_PREFIXES)

def is_lod(name):
    # ловим и "_LOD1", и "Susat LOD0" (пробел), и "LOD0"
    return re.search(r"(?:^|[ _])LOD\d*$", name, re.IGNORECASE) is not None

def strip_blender_suffix(name):
    return re.sub(r"\.\d{3}$", "", name)

def deselect_all():
    for o in list(bpy.context.selected_objects):
        o.select_set(False)

def assign_game_material(obj):
    """Назначить Game Material коллайдеру. Молча выходим, если Workbench недоступен."""
    if not GAME_MATERIAL_ENUM_KEY:
        return
    try:
        from EnfusionBlenderTools.core.collider_cache import ColliderSetupCache
        from EnfusionBlenderTools.core.materials.material_io import create_game_material

        key_to_name = ColliderSetupCache.enum_key_to_material_name()
        mat_name = key_to_name.get(GAME_MATERIAL_ENUM_KEY)
        if not mat_name:
            log("    ! Game Material '%s' не найден (Workbench не подключён?) — назначьте вручную" % GAME_MATERIAL_ENUM_KEY)
            return
        mat = bpy.data.materials.get(mat_name)
        if mat is None:
            mat = create_game_material(GAME_MATERIAL_ENUM_KEY, mat_name)
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        log("    material -> %s" % mat_name)
    except Exception as e:
        log("    ! материал не назначен (%s) — назначьте вручную в EBT" % e)

def _world_bounds(objs):
    """Мировые границы (minx,miny,minz,maxx,maxy,maxz) по всем объектам."""
    import mathutils
    xs, ys, zs = [], [], []
    for o in objs:
        mw = o.matrix_world
        for c in o.bound_box:
            v = mw @ mathutils.Vector(c)
            xs.append(v.x); ys.append(v.y); zs.append(v.z)
    if not xs:
        return None
    return (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))


def make_box(name, bounds, like_obj=None):
    """Создать UBX-куб по мировым границам (учитывает масштаб/родителей)."""
    import mathutils
    minx, miny, minz, maxx, maxy, maxz = bounds
    size = mathutils.Vector((max(0.001, (maxx - minx)) * BOX_SCALE,
                             max(0.001, (maxy - miny)) * BOX_SCALE,
                             max(0.001, (maxz - minz)) * BOX_SCALE))
    center = mathutils.Vector(((minx + maxx) / 2.0,
                               (miny + maxy) / 2.0,
                               (minz + maxz) / 2.0))

    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.active_object
    obj.name = "UBX_" + name
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.dimensions = size            # мировые габариты

    # в ту же коллекцию, что и исходный меш
    if like_obj is not None:
        try:
            col = like_obj.users_collection[0]
            for c in list(obj.users_collection):
                c.objects.unlink(obj)
            col.objects.link(obj)
        except Exception:
            pass

    # запечь масштаб (чистый трансформ для экспорта)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    log("    box dims: %.4f x %.4f x %.4f" % (size.x, size.y, size.z))
    return obj


def remove_existing_colliders(objs=None):
    """Удалить ВСЕ коллайдеры в сцене (идемпотентность повторного запуска)."""
    for o in list(bpy.data.objects):
        if o.type == "MESH" and is_collider(o.name):
            n = o.name
            bpy.data.objects.remove(o, do_unlink=True)
            log("    (удалён прежний коллайдер %s)" % n)


def _biggest_name(objs):
    """Имя самого крупного по объёму bbox меша — для имени коллайдера."""
    best, bestv = None, -1.0
    for o in objs:
        b = _world_bounds([o])
        v = (b[3] - b[0]) * (b[4] - b[1]) * (b[5] - b[2])
        if v > bestv:
            bestv, best = v, o.name
    return best or "collider"


def make_collider(mesh_obj):
    """Создать коллайдер для одного меша."""
    remove_existing_colliders([mesh_obj])
    deselect_all()
    mesh_obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_obj

    if COLLIDER == "box":
        b = _world_bounds([mesh_obj])
        c = make_box(mesh_obj.name, b, mesh_obj)
        c["usage"] = LAYER_PRESET
        log("    collider: %s   usage=%s   (box)" % (c.name, LAYER_PRESET))
        assign_game_material(c)
        return [c]

    before = set(bpy.data.objects.keys())
    props = bpy.context.scene.ebt_colliders_vhacd_properties
    props.convex_hulls_count = HULLS
    bpy.ops.ebt.collider_vhacd()

    created = [bpy.data.objects[n] for n in bpy.data.objects.keys() if n not in before]
    for c in created:
        clean = strip_blender_suffix(c.name)
        if clean != c.name:
            c.name = clean
        c["usage"] = LAYER_PRESET
        log("    collider: %s   usage=%s" % (c.name, LAYER_PRESET))
        assign_game_material(c)
    if not created:
        log("    ! коллайдер не создан для %s" % mesh_obj.name)
    return created


def cleanup_mesh(obj):
    """Merge by distance (убирает короткие рёбра) + пересчёт нормалей + авто-сглаживание."""
    if not MESH_CLEANUP or obj.type != "MESH":
        return
    try:
        deselect_all()
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.remove_doubles(threshold=CLEANUP_MERGE_DIST)
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        log("    cleanup: %s (merge<=%.3f мм + normals)" % (obj.name, CLEANUP_MERGE_DIST * 1000))
        if AUTO_SMOOTH:
            try:
                import math
                bpy.ops.object.shade_auto_smooth(angle=math.radians(30.0))
                log("    auto-smooth: %s" % obj.name)
            except Exception as e:
                log("    (auto-smooth пропущен: %s)" % e)
    except Exception as e:
        log("    ! cleanup не удался для %s: %s" % (obj.name, e))
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def make_single_collider(objs, name_hint=None):
    """Один куб на весь набор мешей (для моделей из нескольких частей)."""
    remove_existing_colliders(objs)
    for o in objs:
        cleanup_mesh(o)
        b1 = _world_bounds([o])
        if b1:
            log("      mesh %-30s dims %.4f x %.4f x %.4f" % (o.name, b1[3] - b1[0], b1[4] - b1[1], b1[5] - b1[2]))
    b = _world_bounds(objs)
    if b is None:
        return []
    # имя коллайдера: имя FBX (или самого крупного меша), без Blender-суффиксов .NNN
    name = strip_blender_suffix(name_hint) if name_hint else _biggest_name(objs)
    main = bpy.data.objects.get(_biggest_name(objs))
    c = make_box(name, b, main)
    c["usage"] = LAYER_PRESET
    log("    collider: %s   usage=%s   (единый куб, мешей %d)" % (c.name, LAYER_PRESET, len(objs)))
    if max(c.dimensions) > 3.0:
        log("    ! ВНИМАНИЕ: габарит %.2f м — подозрительно много, проверьте меши выше" % max(c.dimensions))
    assign_game_material(c)
    return [c]

def ensure_linked(objs):
    """Если объект ни к какой коллекции не привязан — привязать к коллекции сцены."""
    sc = bpy.context.scene.collection
    n = 0
    for o in objs:
        try:
            if not o.users_collection:
                sc.objects.link(o)
                n += 1
        except Exception:
            pass
    if n:
        log("    подвязано к сцене объектов: %d" % n)


def targets():
    """Кого обрабатывать. LOD-копии пропускаем ТОЛЬКО если есть не-LOD меши."""
    def mesh_only(o):
        return o.type == "MESH" and not is_collider(o.name)

    def base(o):
        return mesh_only(o) and not is_lod(o.name)

    sel = list(bpy.context.selected_objects)
    s_base = [o for o in sel if base(o)]
    if s_base:
        return s_base, True
    s_mesh = [o for o in sel if mesh_only(o)]
    if s_mesh:
        return s_mesh, True
    a_base = [o for o in bpy.data.objects if base(o)]
    if a_base:
        return a_base, False
    return [o for o in bpy.data.objects if mesh_only(o)], False

def process_scene(name_hint=None):
    objs, explicit = targets()
    if not objs:
        log("  нет мешей для обработки.")
        log("  объекты в файле: " + ", ".join("%s(%s)" % (o.name, o.type) for o in bpy.data.objects))
        log("  -> либо импортируй FBX через EBT и выдели меш (режим current),")
        log("  -> либо поставь MODE=\"batch\" и запусти снова.")
        return
    if not explicit:
        log("  ВНИМАНИЕ: ничего не выделено — обрабатываю ВСЕ меши сцены (%d)" % len(objs))
    else:
        log("  выделено мешей: %d" % len(objs))
    try:
        if SINGLE_BOX:
            make_single_collider(objs, name_hint)
        else:
            for o in objs:
                log("  mesh: %s" % o.name)
                make_collider(o)
    except Exception as e:
        log("    ! ошибка: %s" % e)
        traceback.print_exc()

def clear_scene():
    # без bpy.ops — не зависит от контекста (надёжнее при запуске из Scripting/Console)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for coll in list(bpy.data.collections):
        bpy.data.collections.remove(coll)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.armatures, bpy.data.images, bpy.data.actions):
        for b in list(block):
            try:
                if b.users == 0:
                    block.remove(b)
            except Exception:
                pass

def backup(path):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    dst = os.path.join(BACKUP_DIR, os.path.basename(path))
    if os.path.exists(path):
        shutil.copy2(path, dst)
        log("  backup -> %s" % dst)

def _mesh_count():
    return len([o for o in bpy.data.objects if o.type == "MESH"])


def _try_export_operator(path):
    res = bpy.ops.ebt.export_fbx(filepath=path, validation_level=EXPORT_VALIDATION)
    return "FINISHED" in res, sorted(res)


def _try_export_api(path):
    """Прямой вызов внутреннего API EBT с явным validation_level (оператор его теряет)."""
    import pathlib as _pl
    from EnfusionBlenderTools.core.fbx import fbx_io
    from EnfusionBlenderTools.core import validation

    sev = getattr(validation.base.ValidationSeverity, EXPORT_VALIDATION,
                  validation.base.ValidationSeverity.CRITICAL)
    settings = fbx_io.FBXExportSettings(
        export_as_single_simple_collider=False,
        force_guid_usage=False,
        update_surface_materials=False,
        global_scale=1.0,
        validation_level=sev,
    )
    objs = []
    try:
        from EnfusionBlenderTools.ebt import ebt_utils
        objs = list(ebt_utils.LocalData.scene_objects)
    except Exception:
        objs = []
    if not objs:
        objs = list(bpy.context.scene.objects)
    fbx_io.export_objects(_pl.Path(path), objs, settings)
    return True


def _export_and_verify(path):
    """Экспорт FBX через EBT + проверка, что файл реально перезаписан.
    validation_level: ERROR (Normal) -> падать на near-zero volume / short edges;
    CRITICAL (Permisive) -> пропускать их."""
    for attempt in range(4):
        before = os.path.getmtime(path) if os.path.exists(path) else 0
        ok, res = _try_export_operator(path)
        if not ok:
            log("    ! оператор вернул %s — пробую прямой API EBT" % (res,))
            try:
                _try_export_api(path)
            except Exception as e:
                log("    ! API-экспорт тоже не сработал: %s" % e)
        for _ in range(16):                 # ждём до ~8 с
            time.sleep(0.5)
            if os.path.exists(path) and os.path.getmtime(path) > before:
                return True
        log("    экспорт не записал файл (попытка %d)..." % (attempt + 1))
    return False


def process_file(path):
    log("=== %s ===" % path)
    clear_scene()
    bpy.ops.ebt.import_fbx(filepath=path)
    # ждём появления мешей (импорт EBT может быть отложенным)
    for attempt in range(12):
        if _mesh_count():
            break
        time.sleep(0.5)
    meshes_data = [o for o in bpy.data.objects if o.type == "MESH"]
    meshes_scene = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    log("    imported: mesh(data)=%d  mesh(scene)=%d" % (len(meshes_data), len(meshes_scene)))
    if not meshes_data:
        log("    повтор импорта (первый не дал мешей)...")
        bpy.ops.ebt.import_fbx(filepath=path)
        for attempt in range(12):
            if _mesh_count():
                break
            time.sleep(0.5)
        meshes_data = [o for o in bpy.data.objects if o.type == "MESH"]
        log("    imported(2): mesh(data)=%d" % len(meshes_data))
    ensure_linked(meshes_data)
    if FIX_EXISTING_COLLIDERS:
        fix_existing_colliders()
    else:
        process_scene(os.path.splitext(os.path.basename(path))[0])
    if DRY_RUN:
        log("  DRY_RUN: экспорт пропущен (файл не изменён)")
        return
    backup(path)
    if _export_and_verify(path):
        log("  exported: %s" % path)
    else:
        log("  !!! ЭКСПОРТ НЕ УДАЛСЯ: %s" % path)
    if DRY_RUN:
        log("  DRY_RUN: экспорт пропущен (файл не изменён)")
        return
    backup(path)
    bpy.ops.ebt.export_fbx(filepath=path)
    log("  exported: %s" % path)

def fix_existing_colliders():
    """Починить УЖЕ имеющиеся коллайдеры в сцене: usage + Game Material + чистые имена."""
    n = 0
    for o in list(bpy.data.objects):
        if o.type != "MESH" or not is_collider(o.name):
            continue
        clean = strip_blender_suffix(o.name)
        if clean != o.name:
            o.name = clean
        o["usage"] = LAYER_PRESET
        assign_game_material(o)
        log("    fixed: %s   usage=%s" % (o.name, LAYER_PRESET))
        n += 1
    log("  починено коллайдеров: %d" % n)


def main():
    mode = "batch" if EXTRA_FILES else MODE
    log("======== start  %s  MODE=%s  DRY_RUN=%s  COLLIDER=%s  LAYER=%s  FIX=%s  VALIDATION=%s ========" % (SCRIPT_VERSION, mode, DRY_RUN, COLLIDER, LAYER_PRESET, FIX_EXISTING_COLLIDERS, EXPORT_VALIDATION))
    if mode == "batch":
        if not FILES:
            log("FILES пуст — заполните список путей и запустите снова")
            return
        files = FILES
        if EXTRA_FILES:
            files = EXTRA_FILES
            log("  EBT_COLL_FILES: обрабатываю только указанные (%d)" % len(files))
        elif ONLY:
            files = [f for f in FILES if os.path.basename(f).lower() in ONLY]
            log("  ОГРАНИЧЕНИЕ: только %d файлов (из %d)" % (len(files), len(FILES)))
        for f in files:
            try:
                process_file(f)
            except Exception as e:
                log("!!! %s : %s" % (f, e))
                traceback.print_exc()
    elif FIX_EXISTING_COLLIDERS:
        fix_existing_colliders()
        if not DRY_RUN:
            fbx = bpy.context.scene.ebt_xob_path.replace(".xob", ".fbx")
            if fbx and os.path.exists(fbx):
                backup(fbx)
                if _export_and_verify(fbx):
                    log("  exported: %s" % fbx)
                else:
                    log("  !!! ЭКСПОРТ НЕ УДАЛСЯ: %s" % fbx)
            else:
                log("  ! путь FBX неизвестен (ebt_xob_path=%r) — экспортируй вручную" % bpy.context.scene.ebt_xob_path)
    else:
        process_scene()
    log("======== done ========")

main()
