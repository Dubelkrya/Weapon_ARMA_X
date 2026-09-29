# -*- coding: utf-8 -*-
"""
Structura export — экспорт FBX через внутренний API EBT с validation_level=CRITICAL (Permisive).

Нужен потому, что оператор ebt.export_fbx валится на строгой проверке (short edges / non-manifold /
non-convex у BSP и LOD), а параметр validation_level через оператор не доезжает.

ЗАПУСК: Blender GUI (EBT загружен, Workbench запущен) -> Scripting -> Run Script.
Файл перезаписывается по пути FBX_PATH (сначала делается бэкап .bak).
"""

import os
import io
import re
import sys
import shutil
import pathlib
import traceback

import bpy

sys.path.insert(0, r"C:\Users\yshky")
from structura_target import ADDON_ROOT, FBX_PATH, DATA_DIR

def log(m):
    print("[EXP] " + m)

def register_existing_materials():
    """Проставить material.ebt_resource_name из .emat.meta аддона.
    Без этого EBT считает материалы незарегистрированными и отказывается экспортировать
    (Exporting would overwrite existing materials)."""
    name_re = re.compile(r'Name\s+"(\{[0-9A-Fa-f]{16}\}[^"]+\.emat)"')
    index = {}
    for dp, dns, fns in os.walk(ADDON_ROOT):
        for fn in fns:
            if not fn.endswith(".emat.meta"):
                continue
            p = os.path.join(dp, fn)
            try:
                t = io.open(p, "r", encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            m = name_re.search(t)
            if not m:
                continue
            res = m.group(1)                      # {GUID}Assets/.../X.emat
            base = os.path.basename(res.split("}")[-1])
            if base.lower().endswith(".emat"):
                base = base[:-5]
            index[base] = res
    log("индекс материалов (.emat.meta): %d" % len(index))
    # приоритет: материалы ТЕКУЩЕГО здания (иначе по имени подтянутся из соседнего модуля)
    n_own = 0
    if DATA_DIR and os.path.isdir(DATA_DIR):
        for fn in os.listdir(DATA_DIR):
            if not fn.endswith(".emat.meta"):
                continue
            try:
                t = io.open(os.path.join(DATA_DIR, fn), "r", encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            m = name_re.search(t)
            if not m:
                continue
            res = m.group(1)
            base = os.path.basename(res.split("}")[-1])
            if base.lower().endswith(".emat"):
                base = base[:-5]
            index[base] = res
            n_own += 1
    log("материалов текущего здания: %d" % n_own)
    # ВАЖНО: игровые материалы (Common/Materials/dummyvolume.emat, _SharedMaterials/Portals/...)
    # через мост EBT НЕ резолвятся ("Resource not found") — экспорт падает.
    # Поэтому работаем через локальные .emat аддона (как в 97-50_Panelka).
    game = {}
    index.update(game)
    log("игровых материалов в индексе: %d" % len(game))
    n = 0
    missed = []
    for mat in bpy.data.materials:
        name = mat.name
        # имя из индекса — ПЕРЕУСТАНАВЛИВАЕМ всегда: на материале мог остаться
        # неверный ebt_resource_name от прошлых прогонов (игровой путь -> Resource not found)
        res = index.get(name) or index.get(re.sub(r"\.\d{3}$", "", name))
        if res:
            try:
                mat.ebt_resource_name = res
                # ВАЖНО: без непустого ebt_enfusion_shader_type EBT вызывает
                # create_new_material(), который ОБНУЛЯЕТ ebt_resource_name,
                # после чего EBT пытается пересоздать .emat и падает на
                # "Material creation attempted an overwrite ...". Поэтому ставим тип.
                try:
                    if not mat.ebt_enfusion_shader_type:
                        mat.ebt_enfusion_shader_type = "MatPBRBasic"
                except Exception:
                    pass
                n += 1
            except Exception as e:
                missed.append("%s (%s)" % (name, e))
            continue
        try:
            if mat.ebt_resource_name:
                n += 1
                continue
        except Exception:
            continue
        missed.append(name)
    log("зарегистрировано материалов: %d" % n)
    if missed:
        log("НЕ найдены в метах (%d): %s" % (len(missed), ", ".join(missed[:20])))
    for mat in bpy.data.materials:
        try:
            r = mat.ebt_resource_name
        except Exception:
            continue
        if r:
            log("   %-42s -> %s" % (mat.name, r))

def main():
    if not os.path.exists(FBX_PATH):
        log("! файла нет: %s" % FBX_PATH)
        return
    register_existing_materials()
    # Целевые переопределения ресурсов материалов (json env: имя -> "{GUID}.../X.emat").
    # Восстанавливает АВТОРСКОЕ назначение, когда в Data здания лежит одноимённая
    # заглушка, а исходная .xob.meta ссылалась на общий материал другого модуля
    # (пример: Modul_5 Shipfer/Found/Roof -> Modul_2). Применяются ПОСЛЕ register,
    # т.е. имеют приоритет. Сами .emat файлы не меняются.
    ov_src = os.environ.get("STRUCTURA_MAT_OVERRIDES", "")
    if ov_src:
        import json as _json
        try:
            overrides = _json.loads(ov_src)
        except Exception as e:
            log("! STRUCTURA_MAT_OVERRIDES не json: %s" % e)
            overrides = {}
        n_ov = 0
        for name, res in overrides.items():
            mat = bpy.data.materials.get(name)
            if mat is None:
                continue
            try:
                mat.ebt_resource_name = res
                try:
                    if not mat.ebt_enfusion_shader_type:
                        mat.ebt_enfusion_shader_type = "MatPBRBasic"
                except Exception:
                    pass
                log("override: %s -> %s" % (name, res))
                n_ov += 1
            except Exception as e:
                log("! override %s: %s" % (name, e))
        log("переопределено материалов: %d" % n_ov)
    before = os.path.getmtime(FBX_PATH)
    # бэкап
    bak = FBX_PATH + ".bak"
    try:
        if not os.path.exists(bak):
            shutil.copy2(FBX_PATH, bak)
            log("бэкап: %s" % bak)
    except Exception as e:
        log("! бэкап не сделан: %s" % e)

    try:
        from EnfusionBlenderTools.core.fbx import fbx_io
        from EnfusionBlenderTools.core import validation
    except Exception as e:
        log("! не импортируется API EBT: %s" % e)
        traceback.print_exc()
        return

    sev = validation.base.ValidationSeverity.CRITICAL
    settings = fbx_io.FBXExportSettings(
        export_as_single_simple_collider=False,
        force_guid_usage=False,
        update_surface_materials=False,
        global_scale=1.0,
        validation_level=sev,
    )
    objs = list(bpy.context.scene.objects)
    log("объектов к экспорту: %d" % len(objs))
    try:
        fbx_io.export_objects(pathlib.Path(FBX_PATH), objs, settings)
    except Exception as e:
        log("! экспорт упал: %s" % e)
        traceback.print_exc()
        return

    after = os.path.getmtime(FBX_PATH)
    if after > before:
        log("OK: exported %s  (%.1f КБ)" % (FBX_PATH, os.path.getsize(FBX_PATH) / 1024.0))
    else:
        log("! файл НЕ перезаписан (mtime не изменился)")

main()
