# -*- coding: utf-8 -*-
r"""
HEADLESS-прогон конвейера: Blender в фоне, без GUI.

    blender.exe -b --factory-startup --python structura_headless.py -- [export]

Без аргумента "export" экспорт НЕ делается (только интерьер + оболочка в памяти) —
безопасная проверка. С "export" дополнительно пишет FBX (с бэкапом .bak),
дальше Workbench подхватит изменение сам.
"""

import os
import sys

import bpy

sys.path.insert(0, r"C:\Users\yshky")
from structura_target import FBX_PATH, MODULE

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


print("[H] модуль: %s" % MODULE)
print("[H] fbx   : %s" % FBX_PATH)

bpy.ops.wm.read_factory_settings(use_empty=True)
try:
    bpy.ops.preferences.addon_enable(module="EnfusionBlenderTools")
    print("[H] EBT включён")
except Exception as e:
    print("[H] ! EBT: %s" % e)

bpy.ops.import_scene.fbx(filepath=FBX_PATH)
print("[H] объектов в сцене: %d" % len(bpy.data.objects))

run("structura_interior.py")
# BSP: "simple" (открытая коробка + Solidify), "voxel", "surface"
BSP_MODE = os.environ.get("BSP_MODE", "simple")
_bsp = {"simple": "structura_bsp_simple.py",
        "voxel": "structura_bsp_voxel.py",
        "surface": "structura_bsp_shell.py",
        "final": "structura_bsp_final.py"}.get(BSP_MODE, "structura_bsp_simple.py")
run(_bsp)

if DO_EXPORT:
    run("structura_export.py")
    run("structura_fix_materials.py", ["--apply"])
    run("structura_bsp_meta.py", ["--apply"])
    print("\n[H] ЭКСПОРТ СДЕЛАН — Workbench подхватит сам")
else:
    print("\n[H] БЕЗ экспорта (проверка). Добавь аргумент export, чтобы записать FBX")
