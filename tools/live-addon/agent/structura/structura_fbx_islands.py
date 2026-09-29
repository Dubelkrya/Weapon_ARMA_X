# -*- coding: utf-8 -*-
"""headless: разбить меш на связные острова и посчитать знаковый объём каждого.
Отрицательный объём у острова = его нормали смотрят ВНУТРЬ (вывернут)."""
import bpy
import bmesh
import sys
from mathutils import Vector

paths = []
args = sys.argv
if "--" in args:
    paths = args[args.index("--") + 1:]


def islands(bm):
    bm.faces.ensure_lookup_table()
    seen = set()
    out = []
    for f in bm.faces:
        if f.index in seen:
            continue
        stack = [f]
        seen.add(f.index)
        comp = []
        while stack:
            cur = stack.pop()
            comp.append(cur)
            for e in cur.edges:
                for nf in e.link_faces:
                    if nf.index not in seen:
                        seen.add(nf.index)
                        stack.append(nf)
        out.append(comp)
    return out


def volume_of(faces):
    """знаковый объём по теореме о дивергенции (триангулируя веером)"""
    v = 0.0
    for f in faces:
        vs = f.verts[:]
        for i in range(1, len(vs) - 1):
            a, b, c = vs[0].co, vs[i].co, vs[i + 1].co
            v += a.dot(b.cross(c)) / 6.0
    return v


def measure(path, only="lod0"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path)
    print("=" * 84)
    print("FILE:", path)
    for o in sorted(bpy.data.objects, key=lambda x: x.name):
        if o.type != "MESH" or only not in o.name.lower():
            continue
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.transform(o.matrix_world)
        comps = islands(bm)
        neg = 0
        tot_abs = 0.0
        neg_abs = 0.0
        rows = []
        for comp in comps:
            v = volume_of(comp)
            tot_abs += abs(v)
            if v < 0:
                neg += 1
                neg_abs += abs(v)
            c = Vector((0.0, 0.0, 0.0))
            for f in comp:
                for vt in f.verts:
                    c += vt.co
            if comp:
                c /= float(len(comp) * len(comp[0].verts))
            bb = [Vector((1e9, 1e9, 1e9)), Vector((-1e9, -1e9, -1e9))]
            for f in comp:
                for vt in f.verts:
                    bb[0] = Vector((min(bb[0].x, vt.co.x), min(bb[0].y, vt.co.y), min(bb[0].z, vt.co.z)))
                    bb[1] = Vector((max(bb[1].x, vt.co.x), max(bb[1].y, vt.co.y), max(bb[1].z, vt.co.z)))
            rows.append((v, len(comp), bb))
        rows.sort(key=lambda r: -abs(r[0]))
        print("  %-40s всего островов=%d  вывернутых=%d  (%.1f%% объёма)" %
              (o.name, len(comps), neg, 100.0 * neg_abs / tot_abs if tot_abs else 0.0))
        print("     крупнейшие острова:")
        for v, nf, bb in rows[:12]:
            print("       объём %+10.3f  граней %5d  x %6.2f..%6.2f y %6.2f..%6.2f z %6.2f..%6.2f  %s" %
                  (v, nf, bb[0].x, bb[1].x, bb[0].y, bb[1].y, bb[0].z, bb[1].z,
                   "ВЫВЕРНУТ" if v < 0 else ""))
        bm.free()


for p in paths:
    measure(p)
