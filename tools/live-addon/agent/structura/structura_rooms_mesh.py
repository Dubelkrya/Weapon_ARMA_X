# -*- coding: utf-8 -*-
"""Modul_5: вывод комнат из меша (полоса стен, этаж внизу 0.39..3.55).

Алгоритм ``build_rooms(lod)``:
  1) вертикальные грани на полосе середины этажа -> плоскости стен + пролёты;
  2) слияние пар-граней одной стены (PLANE_MERGE) и фильтр коротких стен;
  3) ВНУТРЕННИЕ перегородки = плоскости, у которых суммарно закрыто
     SEP_RATIO поперечного размера (дверной пролёт не разрывает перегородку);
  4) сетка = крайние (наружные) плоскости + перегородки; ячейки разделены
     перегородкой, только если её протяжённость перекрывает ячейку;
  5) flood-fill -> компоненты воздуха -> прямоугольники-комнаты.

Комнаты получаются ОТДЕЛЬНЫМИ боксами на линиях капитальных стен даже там,
где их соединяет дверь: дверной пролёт позже вырезает find_interior_doors.

С ``--apply`` создаёт объекты X_Room_N (usage="BSPRoom") в сцене.
"""
import os
import sys
import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0, r"C:\Users\yshky")

FBX = (r"C:\Users\yshky\OneDrive\Документы\My Games\ArmaReforgerWorkbench\addons\Arm_Structura"
       r"\Arm_Structura\Assets\Structures\Houses\House_Individual\House_Individual_Brus"
       r"\House_Individual_Brus_Modul_5\House_Individual_Modul_5_Brus.fbx")

Z0, Z1 = 1.8, 2.6           # полоса стены (середина этажа)
SEG_GAP = 0.15              # стык сегментов вдоль одной стены
PLANE_MERGE = 0.25          # две грани одной стены
SPAN_RATIO = 0.35           # минимальный размах стены = доля поперечного размера
SEP_RATIO = 0.40            # перегородка, если закрыто >= этой доли поперечного размера
ROOM_DZ = (0.39, 3.55)      # z-диапазон комнат (пол..потолок этажа)
# "X_Room_N": содержит "_room" (фильтры комнат) и НЕ начинается с "BSP_"
# (в противном случае interior/bsp удаляют такой объект как старый результат).
ROOM_NAME = "X_Room_%d"
skip_mats = {"found", "floor", "roof", "shipfer", "floor_r", "ceiling", "ceall", "celling"}


def extract_planes(lod):
    """-> (xplanes: {x: [(y0,y1),..]}, yplanes: {y: [(x0,x1),..]})"""
    bm = bmesh.new()
    bm.from_mesh(lod.data)
    bm.transform(lod.matrix_world)
    bm.normal_update()
    xplanes, yplanes = {}, {}
    for f in bm.faces:
        if len(f.verts) < 3 or abs(f.normal.z) > 0.25:
            continue
        matname = ""
        try:
            matname = lod.data.materials[f.material_index].name.lower() or ""
        except Exception:
            matname = ""
        if any(s in matname for s in skip_mats):
            continue
        c = f.calc_center_median()
        if not (Z0 <= c.z <= Z1):
            continue
        xs = [v.co.x for v in f.verts]
        ys = [v.co.y for v in f.verts]
        n = f.normal
        if abs(n.x) > 0.5:
            key = round(c.x / 0.02) * 0.02
            xplanes.setdefault(key, []).append((min(ys), max(ys)))
        elif abs(n.y) > 0.5:
            key = round(c.y / 0.02) * 0.02
            yplanes.setdefault(key, []).append((min(xs), max(xs)))
    bm.free()
    return xplanes, yplanes


def merge_segs(segs, gap=SEG_GAP):
    out = []
    for (a, b) in sorted(segs):
        if out and a <= out[-1][1] + gap:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [(a, b) for (a, b) in out]


def walls_from(planes, log=print):
    """-> [(v, [(t0,t1),..])]  (слияние пар-граней одной стены)"""
    items = sorted((v, merge_segs(segs)) for v, segs in planes.items())
    walls = []
    for (v, segs) in items:
        if walls and abs(walls[-1][0] - v) <= PLANE_MERGE:
            pv, psegs = walls[-1]
            merged = merge_segs(psegs + segs, SEG_GAP * 3)
            n = len(segs)
            pv = (pv * len(psegs) + v * n) / (len(psegs) + n)
            walls[-1] = (round(pv / 0.02) * 0.02, merged)
        else:
            walls.append((v, segs))
    return walls


def build_rooms(lod, apply=True, log=print):
    xplanes, yplanes = extract_planes(lod)
    log("сырых плоскостей: X=%d Y=%d" % (len(xplanes), len(yplanes)))

    xwalls = walls_from(xplanes, log)   # [(x, [(y0,y1),..])]
    ywalls = walls_from(yplanes, log)   # [(y, [(x0,x1),..])]

    def span(segs):
        return min(s[0] for s in segs), max(s[1] for s in segs)

    ymin = min(span(s)[0] for (_v, s) in xwalls)
    ymax = max(span(s)[1] for (_v, s) in xwalls)
    xmin = min(span(s)[0] for (_v, s) in ywalls)
    xmax = max(span(s)[1] for (_v, s) in ywalls)
    fy, fx = ymax - ymin, xmax - xmin
    log("футпринт x[%.2f..%.2f] y[%.2f..%.2f]" % (xmin, xmax, ymin, ymax))

    # фильтр коротких стен и границы-экстремумы
    xw = [(v, s) for (v, s) in xwalls if span(s)[1] - span(s)[0] >= SPAN_RATIO * fy]
    yw = [(v, s) for (v, s) in ywalls if span(s)[1] - span(s)[0] >= SPAN_RATIO * fx]
    xw.sort(key=lambda kv: kv[0])
    yw.sort(key=lambda kv: kv[0])
    x_ext = (xw[0][0], xw[-1][0])
    y_ext = (yw[0][0], yw[-1][0])

    def covered(segs, lo, hi):
        tot = 0.0
        for (a, b) in segs:
            a = max(a, lo)
            b = min(b, hi)
            if b > a:
                tot += b - a
        return tot / max(hi - lo, 1e-3)

    # внутренние перегородки: закрыто >= SEP_RATIO поперечного размера
    x_sep = [(v, s) for (v, s) in xw if x_ext[0] < v < x_ext[1]
             and covered(s, ymin, ymax) >= SEP_RATIO]
    y_sep = [(v, s) for (v, s) in yw if y_ext[0] < v < y_ext[1]
             and covered(s, xmin, xmax) >= SEP_RATIO]
    log("перегородки X (внутр.): %s" % ", ".join("%.2f" % v for (v, _s) in x_sep) or "нет")
    log("перегородки Y (внутр.): %s" % ", ".join("%.2f" % v for (v, _s) in y_sep) or "нет")

    XB = sorted([x_ext[0]] + [v for (v, _s) in x_sep] + [x_ext[1]])
    YB = sorted([y_ext[0]] + [v for (v, _s) in y_sep] + [y_ext[1]])
    nx, ny = len(XB) - 1, len(YB) - 1
    sepX = {v: s for (v, s) in x_sep}   # значения только из XB (внутренние)
    sepY = {v: s for (v, s) in y_sep}
    if nx < 1 or ny < 1:
        log("! сетка комнат пуста")
        return []

    def overlaps(segs, lo, hi):
        for (a, b) in segs:
            if b > lo and a < hi:
                return True
        return False

    def closed_h(ix, iy):   # граница между ячейками (ix,iy)->(ix+1,iy) при XB[ix+1]
        v = XB[ix + 1]
        s = sepX.get(v)
        return s is not None and overlaps(s, YB[iy], YB[iy + 1])

    def closed_v(ix, iy):   # граница между (ix,iy)->(ix,iy+1) при YB[iy+1]
        v = YB[iy + 1]
        s = sepY.get(v)
        return s is not None and overlaps(s, XB[ix], XB[ix + 1])

    comp = {}

    def flood(start):
        stack = [start]
        cid = start
        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in comp:
                continue
            comp[(cx, cy)] = cid
            if cx + 1 < nx and not closed_h(cx, cy):
                stack.append((cx + 1, cy))
            if cx - 1 >= 0 and not closed_h(cx - 1, cy):
                stack.append((cx - 1, cy))
            if cy + 1 < ny and not closed_v(cx, cy):
                stack.append((cx, cy + 1))
            if cy - 1 >= 0 and not closed_v(cx, cy - 1):
                stack.append((cx, cy - 1))
        return cid

    for ix in range(nx):
        for iy in range(ny):
            if (ix, iy) not in comp:
                flood((ix, iy))

    cells_by_comp = {}
    for (cell, cid) in comp.items():
        cells_by_comp.setdefault(cid, []).append(cell)

    rects = []
    log("\nкомнаты (боксы):")
    n = 0
    for cid, cells in sorted(cells_by_comp.items(), key=lambda kv: -len(kv[1])):
        xs = [XB[c[0]] for c in cells] + [XB[c[0] + 1] for c in cells]
        ys = [YB[c[1]] for c in cells] + [YB[c[1] + 1] for c in cells]
        r = (min(xs), max(xs), min(ys), max(ys))
        n += 1
        rects.append(r)
        log("   %s: x[%.2f..%.2f] y[%.2f..%.2f]  (%4.2f x %4.2f м, ячеек=%d)"
             % (ROOM_NAME % n, r[0], r[1], r[2], r[3], r[1] - r[0], r[3] - r[2], len(cells)))

    if apply:
        created = 0
        for r in rects:
            created += 1
            me = bpy.data.meshes.new(ROOM_NAME % created)
            me.from_pydata([(r[0], r[2], ROOM_DZ[0]), (r[1], r[2], ROOM_DZ[0]),
                            (r[1], r[3], ROOM_DZ[0]), (r[0], r[3], ROOM_DZ[0]),
                            (r[0], r[2], ROOM_DZ[1]), (r[1], r[2], ROOM_DZ[1]),
                            (r[1], r[3], ROOM_DZ[1]), (r[0], r[3], ROOM_DZ[1])],
                           [], [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4),
                                (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
            me.update()
            ob = bpy.data.objects.new(ROOM_NAME % created, me)
            bpy.context.scene.collection.objects.link(ob)
            ob["usage"] = "BSPRoom"
        log("создано комнат-объектов: %d" % created)
    return rects


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=FBX)
    lod = next((o for o in bpy.data.objects if o.type == "MESH" and "lod0" in o.name.lower()), None)
    assert lod is not None, "нет LOD0"
    build_rooms(lod, apply=("--apply" in sys.argv))


if __name__ == "__main__":
    main()