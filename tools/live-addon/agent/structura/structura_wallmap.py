# -*- coding: utf-8 -*-
r"""
Карта стен модели: сетка точек в интерьере; точка внутри стены -> '#'.

    blender.exe -b --factory-startup --python structura_wallmap.py -- <fbx> [z]

Печатает ASCII-карту (строки = Y, столбцы = X) + найденные плоскости стен.
"""

import bpy
import bmesh
import sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree

args = sys.argv
rest = args[args.index("--") + 1:] if "--" in args else []
FBX = rest[0]
Z = float(rest[1]) if len(rest) > 1 else 1.5

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX)

lod = None
for o in bpy.data.objects:
    if o.type == "MESH" and "lod0" in o.name.lower():
        lod = o
        break
print("LOD0:", lod.name if lod else "(нет)")
bm = bmesh.new()
bm.from_mesh(lod.data)
bm.transform(lod.matrix_world)
tree = BVHTree.FromBMesh(bm)

xs = [v.co.x for v in bm.verts]
ys = [v.co.y for v in bm.verts]
zs = [v.co.z for v in bm.verts]
X0, X1 = min(xs), max(xs)
Y0, Y1 = min(ys), max(ys)
print("габарит: x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f" % (X0, X1, Y0, Y1, min(zs), max(zs)))

STEP = 0.15
D = 0.09
dirs = [Vector((1, 0, 0)), Vector((-1, 0, 0)), Vector((0, 1, 0)), Vector((0, -1, 0))]


def is_wall(p):
    n = 0
    for d in dirs:
        h = tree.ray_cast(p, d, D)
        if h and h[0]:
            n += 1
    return n >= 2


print()
print("карта стен при z=%.2f  ('#'=стена, '.'=воздух, ' '=вне дома)" % Z)
hdr = "      "
x = X0
cols = []
while x <= X1:
    cols.append(x)
    x += STEP
for i, cx in enumerate(cols):
    hdr += ("|" if i % 10 == 0 else " ")
print(hdr)
y = Y1
while y >= Y0:
    row = "%6.2f" % y
    for cx in cols:
        p = Vector((cx, y, Z))
        inside_bbox = (X0 - 0.1 <= cx <= X1 + 0.1) and (Y0 - 0.1 <= y <= Y1 + 0.1)
        if not inside_bbox:
            row += " "
        else:
            row += "#" if is_wall(p) else "."
    print(row)
    y -= STEP

# плоскости стен по X и по Y (где много '#' подряд)
print()
print("=== доли стен по линиям (для поиска перегородок) ===")
for axis in ("y", "x"):
    vals = cols if axis == "x" else None
    # по Y: пройдём по y и посчитаем долю '#' при фиксированном y
    if axis == "y":
        y = Y1
        while y >= Y0:
            cnt = sum(1 for cx in cols if is_wall(Vector((cx, y, Z))))
            if cnt > 3:
                print("   y=%6.2f  стен %3d из %3d" % (y, cnt, len(cols)))
            y -= STEP
    else:
        for cx in cols:
            cnt = 0
            y = Y1
            while y >= Y0:
                if is_wall(Vector((cx, y, Z))):
                    cnt += 1
                y -= STEP
            if cnt > 3:
                print("   x=%6.2f  стен %3d" % (cx, cnt))
