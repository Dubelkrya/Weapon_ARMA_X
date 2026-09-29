# -*- coding: utf-8 -*-
"""
Диагностика нормалей: для каждого меша показать
  det  — определитель мировой матрицы (<0 = зеркало, нормали перевернутся при экспорте)
  замк — замкнут ли меш (все рёбра manifold)
  объём — знаковый объём (>0 нормали наружу, <0 — внутрь); имеет смысл только для замкнутых
  наружу — сколько граней смотрят от центра меша

Запуск: Blender GUI -> Scripting -> Run Script.
"""

import bpy
import bmesh
from mathutils import Vector


def log(m):
    print("[NRM] " + m)


def main():
    log("%-44s %8s %6s %9s %10s" % ("объект", "det", "замк", "объём", "наружу"))
    for o in sorted(bpy.data.objects, key=lambda x: x.name):
        if o.type != "MESH":
            continue
        n = o.name.lower()
        if not ("lod" in n or "room" in n or n.startswith("prt_") or n.startswith("bsp_")):
            continue

        det = o.matrix_world.to_3x3().determinant()

        bm = bmesh.new()
        bm.from_mesh(o.data)

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

        log("%-44s %+8.3f %6s %9s %5d/%-5d" % (
            o.name, det, "да" if closed else "нет",
            ("%+.3f" % vol) if vol is not None else "-", out, tot))
        bm.free()

    # отдельно: матрицы порталов (правый базис?)
    log("")
    log("порталы: определитель локальной матрицы")
    for o in sorted(bpy.data.objects, key=lambda x: x.name):
        if o.type == "MESH" and o.name.upper().startswith("PRT_"):
            det = o.matrix_world.to_3x3().determinant()
            log("   %-12s det = %+0.3f  %s" % (o.name, det, "ок" if det > 0 else "ЗЕРКАЛО ✗"))


main()
