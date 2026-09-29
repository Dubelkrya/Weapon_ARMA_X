# -*- coding: utf-8 -*-
"""headless-проверка: импортировать FBX и измерить ориентацию нормалей LOD-мешей."""
import bpy
import bmesh
import sys
from mathutils import Vector

paths = []
args = sys.argv
if "--" in args:
    paths = args[args.index("--") + 1:]


def measure(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    try:
        bpy.ops.import_scene.fbx(filepath=path)
    except Exception as e:
        print("IMPORT-FAIL %s: %s" % (path, e))
        return
    print("=" * 80)
    print("FILE:", path)
    for o in sorted(bpy.data.objects, key=lambda x: x.name):
        if o.type != "MESH":
            continue
        n = o.name.lower()
        if not ("lod" in n and "lod0" in n) and "lod0" not in n:
            continue
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.transform(o.matrix_world)
        closed = all(e.is_manifold for e in bm.edges) if len(bm.edges) else False
        vol = None
        try:
            vol = bm.calc_volume(signed=True)
        except Exception:
            pass
        c = Vector((0.0, 0.0, 0.0))
        for v in bm.verts:
            c += v.co
        if len(bm.verts):
            c /= float(len(bm.verts))
        out = tot = 0
        for f in bm.faces:
            d = f.calc_center_median() - c
            if d.length < 1e-6:
                continue
            tot += 1
            if f.normal.dot(d) > 0:
                out += 1
        print("  %-46s det=%+0.3f замкнут=%-3s объём=%-10s наружу %d/%d" % (
            o.name, o.matrix_world.to_3x3().determinant(),
            "да" if closed else "нет",
            ("%+.3f" % vol) if vol is not None else "-", out, tot))
        bm.free()


for p in paths:
    measure(p)
