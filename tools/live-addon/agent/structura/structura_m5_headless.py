# -*- coding: utf-8 -*-
r"""
HEADLESS-прогон конвейера Modul_5:
    меш (LOD0) -> комнаты BSP_Room_N (кластеризация) -> interior -> BSP.

    blender.exe -b --factory-startup --python structura_m5_headless.py -- [export]

Без "export" — только проверка в памяти. С "export" — пишет FBX (бэкап .bak)
и прописывает меты; дальше Workbench подхватит изменение сам.
"""

import os
import sys

import bpy

sys.path.insert(0, r"C:\Users\yshky")

# Modul_5: папка = House_Individual_Brus_Modul_5, но FBX называется иначе.
# structura_target читает эти env (см. structura_target.py).
os.environ["STRUCTURA_MODULE"] = "House_Individual_Brus_Modul_5"
os.environ["STRUCTURA_FBX_NAME"] = "House_Individual_Modul_5_Brus.fbx"

FBX5 = (r"C:\Users\yshky\OneDrive\Документы\My Games\ArmaReforgerWorkbench\addons\Arm_Structura"
        r"\Arm_Structura\Assets\Structures\Houses\House_Individual\House_Individual_Brus"
        r"\House_Individual_Brus_Modul_5\House_Individual_Modul_5_Brus.fbx")

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
DO_EXPORT = "export" in args


def run(name, argv=None):
    path = os.path.join(r"C:\Users\yshky", name)
    print("\n" + "#" * 70)
    print("### %s" % name)
    print("#" * 70)
    if argv is not None:
        sys.argv = [path] + argv
    g = {"__name__": "__main__", "__file__": path}
    exec(compile(open(path, encoding="utf-8").read(), path, "exec"), g)


print("[M5] fbx: %s" % FBX5)

bpy.ops.wm.read_factory_settings(use_empty=True)
try:
    bpy.ops.preferences.addon_enable(module="EnfusionBlenderTools")
    print("[M5] EBT включён")
except Exception as e:
    print("[M5] ! EBT: %s" % e)

bpy.ops.import_scene.fbx(filepath=FBX5)
print("[M5] объектов в сцене: %d" % len(bpy.data.objects))

# 0) комнаты из меша
import structura_rooms_mesh as rmg
lod = next((o for o in bpy.data.objects if o.type == "MESH" and "lod0" in o.name.lower()), None)
assert lod is not None, "нет LOD0"
rmg.build_rooms(lod, apply=True)

# 1) интерьер (порталы/проёмы/двери/BOXVOL)
run("structura_interior.py")

# 2) BSP
run("structura_bsp_simple.py")

if DO_EXPORT:
    # X_Room_* — вспомогательные боксы для сборки BSP; в экспорт не идут
    old = [o for o in bpy.data.objects if o.type == "MESH" and o.name.upper().startswith("X_ROOM")]
    for o in old:
        bpy.data.objects.remove(o, do_unlink=True)
    print("[M5] убрано вспомогательных комнат-боксов: %d" % len(old))

    # ВИЗУАЛЬНЫЕ материалы: локальные Shipfer/Found/Roof.emat в Data Modul_5 —
    # ЗАГЛУШКИ (только MaskMap+GlobalNMOMap, без текстурных слоёв), а исходная мета
    # авторов назначала эти слоты на ОБЩИЕ материалы Modul_2 (то же здание другой
    # планировки). Возвращаем авторское назначение на уровне меты/FBX; сами .emat
    # не трогаем. register_existing_materials() по basename подтянула локальные
    # файлы — здесь приоритетно переустанавливаем ресурс перед экспортом.
    mat_overrides = {
        "House_Individual_Modul_5_Shipfer": "{580B07B9E97B8826}Assets/Structures/Houses/House_Individual/"
            "House_Individual_Brus/House_Individual_Brus_Modul_2/Data/House_Individual_Modul_2_Shipfer.emat",
        "House_Individual_Modul_5_Found":   "{EC8B1EE463ECB990}Assets/Structures/Houses/House_Individual/"
            "House_Individual_Brus/House_Individual_Brus_Modul_2/Data/House_Individual_Modul_2_Found.emat",
        "House_Individual_Modul_5_Roof":    "{04D3C6CF1317AB54}Assets/Structures/Houses/House_Individual/"
            "House_Individual_Brus/House_Individual_Brus_Modul_2/Data/House_Individual_Modul_2_Roof.emat",
    }
    os.environ["STRUCTURA_MAT_OVERRIDES"] = __import__("json").dumps(mat_overrides)
    os.environ["STRUCTURA_MAT_ASSIGN_MAP"] = __import__("json").dumps(mat_overrides)

    # FBX-коллайдер UTM должен ссылаться на ИГРОВЫЕ материалы. Оригинальные
    # ссылки меты ({A88F...}Brus_INT.gamemat, {DA19...}Shipfer.gamemat) в аддоне
    # НЕ существуют — Workbench при импорте плодит для них новые GUID и материалы
    # на здании оказываются битыми. Берём ванильные gamemat, как у соседнего
    # Modul_4 (UTM_Wall -> wood, UTM_Shipfer -> concrete_100mm).
    # Иначе EBT-валидация CRITICAL "MaterialTypeMismatch" отклонит экспорт.
    # Ключи — оба состояния: исходные имена FBX и уже переименованные (из
    # предыдущего экспорта), чтобы повторный прогон был идемпотентным.
    utm_targets = {
        "House_Individual_Modul_5_Brus_INT":                    "wood_EA270CE454C419FD",
        "House_Individual_Modul_5_Brus_INT_A88F35F8749D6B33":   "wood_EA270CE454C419FD",
        "House_Individual_Modul_5_Shipfer":                     "concrete_100mm_FD7A84920F0FCABC",
        "House_Individual_Modul_5_Shipfer_DA1900A2A57E3C2A":    "concrete_100mm_FD7A84920F0FCABC",
    }
    changed = 0
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.upper().startswith("UTM_"):
            continue
        for i, m in enumerate(list(o.data.materials)):
            if m is None:
                continue
            dst = utm_targets.get(m.name)
            if not dst:
                continue
            nm = bpy.data.materials.get(dst) or bpy.data.materials.new(dst)
            if o.data.materials[i] is not nm:
                o.data.materials[i] = nm
                changed += 1
    print("[M5] коллайдер-материалы UTM -> игровые: %d слотов" % changed)

    run("structura_export.py")
    run("structura_fix_materials.py", ["--apply"])
    run("structura_bsp_meta.py", ["--apply"])
    print("\n[M5] ЭКСПОРТ СДЕЛАН — Workbench подхватит сам")
else:
    print("\n[M5] БЕЗ экспорта (проверка). Добавь аргумент export")