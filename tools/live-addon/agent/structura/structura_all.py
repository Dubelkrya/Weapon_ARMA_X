# -*- coding: utf-8 -*-
r"""
Весь конвейер одной командой (запускать в Blender, Workbench запущен):

    exec(open(r"C:\Users\yshky\structura_all.py", encoding="utf-8").read())

Шаги:
  1. structura_interior.py    — порталы (окна + двери) и BOXVOL
  2. structura_bsp_shell.py   — BSP-оболочка стен с проёмами
  3. structura_export.py      — экспорт FBX/XOB через API EBT
  4. structura_fix_materials.py --apply — MatLightPortal + локальные .emat
  5. structura_bsp_meta.py --apply      — GenerateBSP 1 / ForceCreatePortals 0

После этого — реимпорт модели в Workbench (вручную).
"""

import os
import sys

try:
    BASE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE = r"C:\Users\yshky"

STEPS = [
    ("structura_interior.py", None),
    ("structura_bsp_shell.py", None),
    ("structura_export.py", None),
    ("structura_fix_materials.py", ["--apply"]),
    ("structura_bsp_meta.py", ["--apply"]),
]


def run(name, argv):
    path = os.path.join(BASE, name)
    print("\n" + "#" * 70)
    print("### %s" % name)
    print("#" * 70)
    if argv is not None:
        sys.argv = [path] + argv
    g = {"__name__": "__main__", "__file__": path}
    exec(compile(open(path, encoding="utf-8").read(), path, "exec"), g)


for _name, _argv in STEPS:
    run(_name, _argv)

print("\n" + "#" * 70)
print("### КОНВЕЙЕР ЗАВЕРШЁН — теперь реимпорт модели в Workbench")
print("#" * 70)
