# -*- coding: utf-8 -*-
import os
import sys
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, r"C:\Users\yshky")

FBX5 = (r"C:\Users\yshky\OneDrive\Документы\My Games\ArmaReforgerWorkbench\addons\Arm_Structura"
        r"\Arm_Structura\Assets\Structures\Houses\House_Individual\House_Individual_Brus"
        r"\House_Individual_Brus_Modul_5\House_Individual_Modul_5_Brus.fbx")


def run(name):
    path = os.path.join(r"C:\Users\yshky", name)
    g = {"__name__": "__main__", "__file__": path}
    exec(compile(open(path, encoding="utf-8").read(), path, "exec"), g)


bpy.ops.wm.read_factory_settings(use_empty=True)
try:
    bpy.ops.preferences.addon_enable(module="EnfusionBlenderTools")
except Exception:
    pass
bpy.ops.import_scene.fbx(filepath=FBX5)

import structura_rooms_mesh as rmg
lod = next((o for o in bpy.data.objects if o.type == "MESH" and "lod0" in o.name.lower()), None)
rmg.build_rooms(lod, apply=True)

run("structura_interior.py")
run("structura_bsp_simple.py")

bsp = next((o for o in bpy.data.objects if o.name.upper().startswith("BSP_")), None)
print("\nBSP:", bsp.name if bsp else None)
if not bsp:
    sys.exit(1)
bm = bmesh.new()
bm.from_mesh(bsp.data)
bm.transform(bsp.matrix_world)

edge_faces = {}
for f in bm.faces:
    for e in f.edges:
        k = tuple(sorted((e.verts[0].index, e.verts[1].index)))
        edge_faces[k] = edge_faces.get(k, 0) + 1
bad = [(k, n) for k, n in edge_faces.items() if n != 2]
print("рёбер всего: %d, с !=2 гранями: %d" % (len(edge_faces), len(bad)))
for (k, n) in bad[:20]:
    v0 = bm.verts[k[0]].co; v1 = bm.verts[k[1]].co
    c = (v0 + v1) * 0.5
    print("  граней=%d  центр (%.3f %.3f %.3f)" % (n, c.x, c.y, c.z))

bv = BVHTree.FromBMesh(bm)


def crossings(p, axis):
    d = Vector((0.0, 0.0, 0.0)); d[axis] = 1.0
    o = Vector(p)
    total = 0
    for _ in range(400):
        loc, normal, idx, _dist = bv.ray_cast(o, d, 1e6)
        if loc is None:
            break
        total += 1
        o = loc + normal * 0.002 + d * 0.002
    return total


def classify(p):
    res = [crossings(p, a) % 2 for a in (0, 1, 2)]
    solid = sum(res) >= 2
    return "SOLID" if solid else "air", res


tests = [
    ("Room_2 (запад-юг) воздух:     x-3.0 y-5.0", (-3.0, -5.0, 1.8), "air"),
    ("Room_3 (восток-юг) воздух:    x 1.0 y-4.0", (1.0, -4.0, 1.8), "air"),
    ("Room_1 (север) воздух:        x 0.0 y 5.0", (0.0, 5.0, 1.8), "air"),
    ("перегородка X=-0.52 solid:    x-0.52 y-4.5", (-0.52, -4.5, 1.8), "SOLID"),
    ("X-перегородка хвост y=2.2:    x-0.52 y 2.2", (-0.52, 2.2, 1.8), "SOLID"),
    ("дверь в X=-0.52 air:          x-0.53 y-2.47", (-0.53, -2.47, 1.72), "air"),
    ("перегородка Y=2.26 solid:     x 0.0 y 2.26", (0.0, 2.26, 1.8), "SOLID"),
    ("Y-перегородка восток y=2.26:  x 1.8 y 2.26", (1.8, 2.26, 1.8), "SOLID"),
    ("дверь в Y=2.26 air:           x-2.59 y 2.21", (-2.59, 2.21, 1.72), "air"),
    ("зап. стена solid:             x-4.35 y 4.0", (-4.35, 4.0, 1.8), "SOLID"),
    ("вост. стена solid:            x 2.12 y 0.0", (2.12, 0.0, 1.8), "SOLID"),
    ("вост. окно air:               x 2.12 y-5.09", (2.12, -5.09, 1.97), "air"),
    ("юж. стена solid:              x 1.8 y-7.0", (1.8, -7.0, 1.8), "SOLID"),
    ("зап. окно air:                x-4.35 y 0.36", (-4.35, 0.36, 1.99), "air"),
    ("сев. стена solid:             x 0.0 y 7.2", (0.0, 7.2, 1.8), "SOLID"),
    ("пол solid:                    z 0.30", (0.0, 0.0, 0.30), "SOLID"),
    ("потолок solid:                z 3.70", (0.0, 0.0, 3.70), "SOLID"),
    ("чердак-воздух бокса нет (solid зона над zc): z 3.60", (0.0, 0.0, 3.60), "SOLID"),
]
print("\n-- точечные тесты (solid/воздух) Modul_5 --")
ok = 0
for name, p, want in tests:
    got, res = classify(p)
    mark = "OK " if got == want else "FAIL"
    ok += got == want
    print("  [%s] %-46s -> %-6s (xyz-чётность %s) ожидание: %s" % (mark, name, got, res, want))
print("итог: %d/%d" % (ok, len(tests)))
bm.free()