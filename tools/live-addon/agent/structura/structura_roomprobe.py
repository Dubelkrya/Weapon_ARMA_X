# -*- coding: utf-8 -*-
r"""
Карта свободного расстояния по объёму: для каждой точки сетки — минимум из 4 лучей
(±X, ±Y) до первой поверхности. Внутри стены ~0, в центре комнаты — метры.

    blender.exe -b --factory-startup --python structura_roomprobe.py -- <fbx> [z] [step]

Печать: '#' = <0.15 м (стена), 0..9 = 0.0..0.9 м, '+' = >0.9 м.
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
STEP = float(rest[2]) if len(rest) > 2 else 0.25
LIM = 2.0

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX)

lod = None
for o in bpy.data.objects:
    if o.type == "MESH" and "lod0" in o.name.lower():
        lod = o
        break
bm = bmesh.new()
bm.from_mesh(lod.data)
bm.transform(lod.matrix_world)
tree = BVHTree.FromBMesh(bm)

# интерьер берём по коллайдерам Room*, если они есть
xs = [v.co.x for v in bm.verts]
ys = [v.co.y for v in bm.verts]
X0, X1 = min(xs), max(xs)
Y0, Y1 = min(ys), max(ys)
print("LOD0:", lod.name, " габарит x %.2f..%.2f y %.2f..%.2f" % (X0, X1, Y0, Y1))

DIRS = [Vector((1, 0, 0)), Vector((-1, 0, 0)), Vector((0, 1, 0)), Vector((0, -1, 0))]


def free(p):
    best = LIM
    for d in DIRS:
        h = tree.ray_cast(p, d, LIM)
        if h and h[0]:
            best = min(best, (h[0] - p).length)
    return best


cols = []
x = X0 + STEP / 2
while x <= X1:
    cols.append(x)
    x += STEP

print()
print("карта свободного расстояния при z=%.2f, шаг %.2f" % (Z, STEP))
print("      " + "".join(("%d" % (i % 10)) if i % 5 == 0 else " " for i in range(len(cols))))
y = Y1 - STEP / 2
while y >= Y0:
    row = "%6.2f" % y
    for cx in cols:
        v = free(Vector((cx, y, Z)))
        if v < 0.15:
            row += "#"
        elif v > 0.9:
            row += "+"
        else:
            row += "%d" % int(v * 10)
    print(row)
    y -= STEP

# кандидаты в перегородки: линии, где много '#' подряд
print()
print("=== линии с большим числом '#' (кандидаты в стены) ===")
y = Y1 - STEP / 2
while y >= Y0:
    cnt = sum(1 for cx in cols if free(Vector((cx, y, Z))) < 0.15)
    if cnt >= max(3, len(cols) // 6):
        print("   y=%6.2f  стен %3d из %3d" % (y, cnt, len(cols)))
    y -= STEP
for cx in cols:
    cnt = 0
    y = Y1 - STEP / 2
    while y >= Y0:
        if free(Vector((cx, y, Z))) < 0.15:
            cnt += 1
        y -= STEP
    if cnt >= 3:
        print("   x=%6.2f  стен %3d" % (cx, cnt))
