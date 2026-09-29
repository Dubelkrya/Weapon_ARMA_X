# -*- coding: utf-8 -*-
r"""
headless-разбор модели: коллайдеры, сокеты, габариты стен LOD0, что уже оборудовано.
Запуск:
  blender.exe -b --factory-startup --python structura_inspect_model.py -- <путь к fbx>
"""

import bpy
import bmesh
import sys
from mathutils import Vector

args = sys.argv
paths = args[args.index("--") + 1:] if "--" in args else []


def run(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path)
    print("=" * 96)
    print("FILE:", path)

    lod0 = None
    for o in bpy.data.objects:
        if o.type == "MESH" and "lod0" in o.name.lower():
            lod0 = o
            break

    names = sorted(o.name for o in bpy.data.objects)
    pref = {}
    for o in bpy.data.objects:
        for p in ("UTM_", "Socket_", "PRT_", "BSP_", "BOXVOL_", "SPHVOL_", "OCC_"):
            if o.name.upper().startswith(p):
                pref.setdefault(p, []).append(o.name)
    print("--- объекты по префиксам ---")
    for p in ("UTM_", "Socket_", "PRT_", "BSP_", "BOXVOL_", "SPHVOL_", "OCC_"):
        v = pref.get(p, [])
        print("  %-9s %2d: %s" % (p, len(v), ", ".join(sorted(v))[:150]))
    print("  всего объектов: %d" % len(names))

    print("--- сокеты (мировые позиции) ---")
    for o in sorted(bpy.data.objects, key=lambda x: x.name):
        if o.name.startswith("Socket_"):
            c = o.matrix_world.translation
            print("  %-24s (%7.2f %7.2f %7.2f)" % (o.name, c.x, c.y, c.z))

    if lod0 is not None:
        bm = bmesh.new()
        bm.from_mesh(lod0.data)
        bm.transform(lod0.matrix_world)
        vs = [v.co for v in bm.verts]
        xs = [v.x for v in vs]; ys = [v.y for v in vs]; zs = [v.z for v in vs]
        print("--- LOD0 ---")
        print("  всё        : x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f" %
              (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
        # полоса стен: берём z между 25% и 75% высоты
        z0, z1 = min(zs), max(zs)
        lo = z0 + (z1 - z0) * 0.30
        hi = z0 + (z1 - z0) * 0.70
        band = [v for v in vs if lo <= v.z <= hi]
        if band:
            print("  стены      : x %.2f..%.2f  y %.2f..%.2f  (полоса z %.2f..%.2f)" %
                  (min(v.x for v in band), max(v.x for v in band),
                   min(v.y for v in band), max(v.y for v in band), lo, hi))
        bm.free()

    print("--- коллайдеры (габариты) ---")
    for o in sorted(bpy.data.objects, key=lambda x: x.name):
        if o.type == "MESH" and o.name.startswith("UTM_"):
            pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
            print("  %-42s x %7.2f..%7.2f y %7.2f..%7.2f z %6.2f..%6.2f" % (
                o.name, min(p.x for p in pts), max(p.x for p in pts),
                min(p.y for p in pts), max(p.y for p in pts),
                min(p.z for p in pts), max(p.z for p in pts)))


for p in paths:
    run(p)
