# -*- coding: utf-8 -*-
"""headless: где реально стены LOD0 и где порталы/коллайдеры."""
import bpy
import bmesh
import sys
from mathutils import Vector

args = sys.argv
paths = args[args.index("--") + 1:] if "--" in args else []


def run(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path)
    print("=" * 90)
    print("FILE:", path)

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

    def bounds(vs):
        xs = [v.co.x for v in vs]; ys = [v.co.y for v in vs]; zs = [v.co.z for v in vs]
        return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))

    allv = list(bm.verts)
    print("LOD0 всё           : x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f" % bounds(allv))
    band = [v for v in allv if 0.8 <= v.co.z <= 3.2]
    if band:
        print("LOD0 стены(z0.8-3.2): x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f" % bounds(band))

    # толщина стены по разрезу y=0 (внутри коридора) вдоль +X
    from mathutils.bvhtree import BVHTree
    tree = BVHTree.FromBMesh(bm)
    for label, org, d in (
        ("разрез (0,0,1.5) -> +X", Vector((0, 0, 1.5)), Vector((1, 0, 0))),
        ("разрез (0,0,1.5) -> -X", Vector((0, 0, 1.5)), Vector((-1, 0, 0))),
        ("разрез (0,3,1.5) -> +Y", Vector((0, 3, 1.5)), Vector((0, 1, 0))),
        ("разрез (0,-3,1.5) -> -Y", Vector((0, -3, 1.5)), Vector((0, -1, 0))),
    ):
        hits = []
        o = org.copy()
        for _ in range(8):
            h = tree.ray_cast(o, d, 30.0)
            if not h or not h[0]:
                break
            hits.append(h[0])
            o = h[0] + d * 0.01
        txt = ", ".join("%.2f" % (p - org).dot(d) for p in hits[:6])
        print("  %-24s поверхности на: %s" % (label, txt or "нет"))

    # порталы
    for o in sorted(bpy.data.objects, key=lambda x: x.name):
        if o.type == "MESH" and o.name.upper().startswith("PRT_") and o.name.upper() != "PRT_195X72":
            c = o.matrix_world.translation
            print("  %-8s центр (%.2f %.2f %.2f)" % (o.name, c.x, c.y, c.z))
    bm.free()


for p in paths:
    run(p)
