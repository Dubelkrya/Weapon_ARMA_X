# -*- coding: utf-8 -*-
"""headless: направление нормалей стен — что видно изнутри комнаты и снаружи."""
import bpy
import bmesh
import sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree

args = sys.argv
paths = args[args.index("--") + 1:] if "--" in args else []


def check(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path)
    lod = None
    for o in bpy.data.objects:
        if o.type == "MESH" and "lod0" in o.name.lower():
            lod = o
            break
    if lod is None:
        print("нет lod0"); return
    bm = bmesh.new()
    bm.from_mesh(lod.data)
    bm.transform(lod.matrix_world)
    tree = BVHTree.FromBMesh(bm)
    print("FILE:", path)
    print("меш lod0: verts=%d faces=%d" % (len(bm.verts), len(bm.faces)))

    tests = [
        ("ИЗ КОМНАТЫ (0,0,1.5) -> +X (в стену)", Vector((0, 0, 1.5)), Vector((1, 0, 0))),
        ("ИЗ КОМНАТЫ (0,0,1.5) -> -X (в стену)", Vector((0, 0, 1.5)), Vector((-1, 0, 0))),
        ("ИЗ КОМНАТЫ (0,0,1.5) -> +Y (в стену)", Vector((0, 0, 1.5)), Vector((0, 1, 0))),
        ("ИЗ КОМНАТЫ (0,0,1.5) -> -Y (в стену)", Vector((0, 0, 1.5)), Vector((0, -1, 0))),
        ("СНАРУЖИ (3.5,0,1.5) -> -X (в дом)",   Vector((3.5, 0, 1.5)), Vector((-1, 0, 0))),
        ("СНАРУЖИ (-5.5,0,1.5) -> +X (в дом)",  Vector((-5.5, 0, 1.5)), Vector((1, 0, 0))),
        ("СНАРУЖИ (0,9,1.5) -> -Y (в дом)",     Vector((0, 9, 1.5)), Vector((0, -1, 0))),
        ("СНАРУЖИ (0,-9,1.5) -> +Y (в дом)",    Vector((0, -9, 1.5)), Vector((0, 1, 0))),
        ("СНАРУЖИ сверху (0,0,6) -> -Z",        Vector((0, 0, 6.0)), Vector((0, 0, -1))),
    ]
    for label, o, d in tests:
        hit = tree.ray_cast(o, d, 20.0)
        if not hit or not hit[0]:
            print("  %-38s попадания нет" % label)
            continue
        loc, nrm = hit[0], hit[1]
        dot = nrm.normalized().dot(d)
        # dot<0 -> нормаль смотрит НА наблюдателя (грань видна) — правильно для внутренней поверхности
        print("  %-38s точка (%6.2f %6.2f %6.2f)  dot=%+0.2f  %s" %
              (label, loc.x, loc.y, loc.z, dot,
               "ГРАНЬ ВИДНА (ок)" if dot < 0 else "ОТВЁРНУТА ОТ НАС ✗"))
    bm.free()


for p in paths:
    check(p)
