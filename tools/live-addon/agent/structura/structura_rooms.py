# -*- coding: utf-8 -*-
"""Короткий вывод: мировые границы коллайдеров и LOD0 (для раскладки помещений)."""

import bpy
import mathutils

def wb(o):
    pts = [o.matrix_world @ mathutils.Vector(c) for c in o.bound_box]
    xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)

print("=" * 100)
print("%-40s %-30s %s" % ("объект", "мировые границы x/y/z", "размер"))
print("-" * 100)

objs = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("UTM_")]
lod = [o for o in bpy.data.objects if o.type == "MESH" and "lod0" in o.name.lower()]
for o in sorted(objs + lod, key=lambda x: x.name):
    x0, x1, y0, y1, z0, z1 = wb(o)
    print("%-40s x %7.2f..%7.2f  y %7.2f..%7.2f  z %6.2f..%6.2f   %5.2f x %5.2f x %5.2f" %
          (o.name, x0, x1, y0, y1, z0, z1, x1 - x0, y1 - y0, z1 - z0))
print("=" * 100)
