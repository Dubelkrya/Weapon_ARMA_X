# -*- coding: utf-8 -*-
r"""
BSP: граница занятого объёма по неравномерной сетке (по-стеночный предикат).

Предикат материала (рекомендация Enfusion, без ловушки «весь воздух»):
    solid(p) = floor_or_ceiling(p)  OR  any( inside(wall) AND NOT inside(any opening of THAT wall) )

Стены: наружные (кольцо) + перегородки (по стыкам коллайдеров Room_*), каждая со своими
проёмами. Межкомнатная дверь = один сквозной проём + один портал. Грани — только на
границе материал<->воздух, общий индекс вершины на узел (ix,iy,iz). Без Boolean/вокселя.
"""

import os
import sys

import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0, r"C:\Users\yshky")
try:
    from structura_target import DUMMY_NAME, DUMMY_KEY
except Exception:
    DUMMY_NAME = "dummyvolume_D3975B51F51E6BD5"
    DUMMY_KEY = "dummyvolume"

EPS = 0.05
PART_T = 0.20
DO_PARTITIONS = os.environ.get("BSP_PARTITIONS", "1") == "1"
FILLER = os.environ.get("BSP_FILLER", "1") == "1"


def log(m):
    print("[GRID] " + m)


def usage_of(o):
    for k in o.keys():
        if k.lower() == "usage":
            try:
                return o[k]
            except Exception:
                return None
    return None


def wb(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


def get_dummy():
    m = bpy.data.materials.get(DUMMY_NAME)
    if m is None:
        try:
            from EnfusionBlenderTools.core.materials.material_io import create_game_material
            m = create_game_material(DUMMY_KEY, DUMMY_NAME)
        except Exception as e:
            log("! dummyvolume: %s" % e)
    return m


def check_bsp(ob):
    from EnfusionBlenderTools.core.mesh import bmesh_validation as BV
    from EnfusionBlenderTools.modelqa.utils import (
        SMALL_FACE_THRESHOLD, SHORT_EDGE_THRESHOLD, COS_ANGLE_LIMIT)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.transform(ob.matrix_world)
    checks = [
        ("треугольники", not BV.is_not_triangulated(bm)),
        ("замкнут", not bool(BV.has_non_manifold_edges(bm))),
        ("manifold вершины", not bool(BV.has_non_manifold_vertices(bm))),
        ("без самопересечений", not bool(BV.has_self_intersecting_geometry(bm))),
        ("без тонких граней", not bool(BV.has_thin_faces(bm, COS_ANGLE_LIMIT))),
        ("без мелких граней", not bool(BV.has_small_faces(bm, SMALL_FACE_THRESHOLD))),
        ("без коротких рёбер", not bool(BV.has_short_edges(bm, SHORT_EDGE_THRESHOLD))),
        ("материал dummyvolume", [m.name for m in ob.data.materials if m] == [DUMMY_NAME]),
    ]
    bad = [n for n, ok in checks if not ok]
    log("   %-12s verts=%d faces=%d  %s" % (ob.name, len(bm.verts), len(bm.faces),
        "ГОДНО ✓" if not bad else ("ОШИБКА: " + ", ".join(bad))))
    if bad:
        try:
            for f in BV.get_small_faces(bm, SMALL_FACE_THRESHOLD)[:4]:
                c = f.calc_center_median()
                log("      мелкая грань: (%.3f %.3f %.3f)" % (c.x, c.y, c.z))
        except Exception:
            pass
    bm.free()
    return not bad


def room_walls(bounds, tol=0.6):
    """Перегородки: список (axis, v, perp0, perp1).
    axis='x' -> стена на x=v, тянется по Y [perp0..perp1];
    axis='y' -> стена на y=v, тянется по X [perp0..perp1].
    Диапазон = ОБЪЕДИНЕНИЕ перпендикулярных диапазонов двух смежных комнат
    (стена доходит до наружной/соседней перегородки, а не обрывается на пересечении —
    иначе в углу, где комнаты разной длины, остаётся зазор).
    Сегменты на одной плоскости сливаются — напр. горизонтальные стены на всю ширину."""
    raw = []
    n = len(bounds)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            a0, a1 = bounds[i]
            b0, b1 = bounds[j]
            if abs(a1.x - b0.x) <= tol and max(a0.y, b0.y) < min(a1.y, b1.y):
                v = (a1.x + b0.x) * 0.5
                raw.append(("x", v, min(a0.y, b0.y), max(a1.y, b1.y)))
            if abs(a1.y - b0.y) <= tol and max(a0.x, b0.x) < min(a1.x, b1.x):
                v = (a1.y + b0.y) * 0.5
                raw.append(("y", v, min(a0.x, b0.x), max(a1.x, b1.x)))
    clusters = []
    for (axis, v, p0, p1) in raw:
        for c in clusters:
            if c[0] == axis and abs(c[1] / c[2] - v) < 0.05:
                c[1] += v; c[2] += 1; c[3].append((p0, p1)); break
        else:
            clusters.append([axis, v, 1, [(p0, p1)]])
    out = []
    for (axis, v_sum, n, segs) in clusters:
        v = round(v_sum / n, 2)
        segs.sort()
        merged = [list(segs[0])]
        for (p0, p1) in segs[1:]:
            if p0 <= merged[-1][1] + 0.05:
                merged[-1][1] = max(merged[-1][1], p1)
            else:
                merged.append([p0, p1])
        for (p0, p1) in merged:
            out.append((axis, v, p0, p1))
    return out


def build_boundary(walls, filler=None):
    # walls: list of (x0,x1,y0,y1,z0,z1, [openings (x0,x1,y0,y1,z0,z1)])
    # filler: (i0, i1, zc, room_boxes) | None — solid-заполнитель вырезов:
    #   всё внутри габарита интерьера (i0..i1, z в [i0.z..zc]), не покрытое
    #   ни стеной, ни комнатой, считается сплошным телом (уступы, щели-полоски).
    Xs, Ys, Zs = set(), set(), set()
    for (x0, x1, y0, y1, z0, z1, openings) in walls:
        Xs.add(x0); Xs.add(x1); Ys.add(y0); Ys.add(y1); Zs.add(z0); Zs.add(z1)
        for o in openings:
            Xs.add(o[0]); Xs.add(o[1]); Ys.add(o[2]); Ys.add(o[3]); Zs.add(o[4]); Zs.add(o[5])
    if filler is not None:
        # границы комнат добавляем в сетку: иначе «вырезы» (уступы) не имеют
        # узлов сетки и не могут стать solid.
        for (r0, r1) in filler[3]:
            Xs.add(r0.x); Xs.add(r1.x); Ys.add(r0.y); Ys.add(r1.y)
            Zs.add(r0.z); Zs.add(r1.z)

    def snap(vals):
        return sorted(set(round(v / 0.02) * 0.02 for v in vals))

    Xs = snap(Xs); Ys = snap(Ys); Zs = snap(Zs)

    def solid(cx, cy, cz):
        for (x0, x1, y0, y1, z0, z1, openings) in walls:
            if x0 < cx < x1 and y0 < cy < y1 and z0 < cz < z1:
                for (ox0, ox1, oy0, oy1, oz0, oz1) in openings:
                    if ox0 < cx < ox1 and oy0 < cy < oy1 and oz0 < cz < oz1:
                        return False
                return True
        if filler is not None:
            i0, i1, zc, rooms = filler
            if i0.x < cx < i1.x and i0.y < cy < i1.y and i0.z < cz < zc:
                for (a, b) in rooms:
                    if a.x < cx < b.x and a.y < cy < b.y and a.z < cz < b.z:
                        return False
                return True
        return False

    vmap = {}
    verts = []

    def node(ix, iy, iz):
        k = (ix, iy, iz)
        if k not in vmap:
            vmap[k] = len(verts)
            verts.append(Vector((Xs[ix], Ys[iy], Zs[iz])))
        return vmap[k]

    quads = []
    nx, ny, nz = len(Xs) - 1, len(Ys) - 1, len(Zs) - 1

    def cs(ix, iy, iz):
        if ix < 0 or ix >= nx or iy < 0 or iy >= ny or iz < 0 or iz >= nz:
            return False
        return solid((Xs[ix] + Xs[ix + 1]) * 0.5, (Ys[iy] + Ys[iy + 1]) * 0.5, (Zs[iz] + Zs[iz + 1]) * 0.5)

    DIRS = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]

    def face(ix, iy, iz, dx, dy, dz):
        if dx == 1:
            a = node(ix + 1, iy, iz); b = node(ix + 1, iy + 1, iz)
            c = node(ix + 1, iy + 1, iz + 1); d = node(ix + 1, iy, iz + 1)
        elif dx == -1:
            a = node(ix, iy, iz); b = node(ix, iy, iz + 1)
            c = node(ix, iy + 1, iz + 1); d = node(ix, iy + 1, iz)
        elif dy == 1:
            a = node(ix, iy + 1, iz); b = node(ix + 1, iy + 1, iz)
            c = node(ix + 1, iy + 1, iz + 1); d = node(ix, iy + 1, iz + 1)
        elif dy == -1:
            a = node(ix, iy, iz); b = node(ix, iy, iz + 1)
            c = node(ix + 1, iy, iz + 1); d = node(ix + 1, iy, iz)
        elif dz == 1:
            a = node(ix, iy, iz + 1); b = node(ix + 1, iy, iz + 1)
            c = node(ix + 1, iy + 1, iz + 1); d = node(ix, iy + 1, iz + 1)
        else:
            a = node(ix, iy, iz); b = node(ix, iy + 1, iz)
            c = node(ix + 1, iy + 1, iz); d = node(ix + 1, iy, iz)
        quads.append((a, b, c, d))

    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                if not cs(ix, iy, iz):
                    continue
                for (dx, dy, dz) in DIRS:
                    if not cs(ix + dx, iy + dy, iz + dz):
                        face(ix, iy, iz, dx, dy, dz)

    return verts, quads


def main():
    old = [o for o in bpy.data.objects if o.type == "MESH" and o.name.upper().startswith("BSP_")]
    for o in old:
        bpy.data.objects.remove(o, do_unlink=True)
    log("удалено старых BSP: %d" % len(old))

    cols = [o for o in bpy.data.objects if o.type == "MESH" and usage_of(o)]

    def ends(o, *sfx):
        n = o.name.lower()
        return any(n.endswith(s) for s in sfx)

    rooms = [o for o in cols if "_room" in o.name.lower()]
    wall = [o for o in cols if ends(o, "_brus", "_wall")]
    cell = [o for o in cols if ends(o, "_celling", "_ceiling")]
    roof = [o for o in cols if ends(o, "_roof")]
    lod0 = next((o for o in bpy.data.objects if o.type == "MESH" and "lod0" in o.name.lower()), None)
    if lod0 is None or not rooms:
        log("! нет LOD0 или комнат")
        return

    i0 = Vector((1e9, 1e9, 1e9)); i1 = Vector((-1e9, -1e9, -1e9))
    for o in rooms:
        a, b = wb(o)
        i0 = Vector((min(i0.x, a.x), min(i0.y, a.y), min(i0.z, a.z)))
        i1 = Vector((max(i1.x, b.x), max(i1.y, b.y), max(i1.z, b.z)))
    room_bounds = [wb(o) for o in rooms]
    if cell:
        zc = min(wb(c)[0].z for c in cell)
    elif roof:
        zc = min(wb(c)[0].z for c in roof)
    else:
        zc = i1.z
    if wall:
        w0, w1 = wb(wall[0])
    else:
        # нет коллайдеров стены (Modul_5): внешний слой по габаритам комнат
        w0 = Vector((i0.x, i0.y, i0.z - 0.17))
        w1 = Vector((i1.x, i1.y, zc + 0.21))

    bm = bmesh.new()
    bm.from_mesh(lod0.data)
    bm.transform(lod0.matrix_world)
    zlo, zhi = i0.z + 0.4, zc - 0.4
    xs, ys = [], []
    for v in bm.verts:
        if zlo <= v.co.z <= zhi:
            xs.append(v.co.x); ys.append(v.co.y)
    if not xs:
        bm.free(); log("! нет стен LOD0"); return
    o0 = Vector((min(xs), min(ys), w0.z))
    o1 = Vector((max(xs), max(ys), w1.z))
    bm.free()
    log("оболочка x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f | интерьер x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f"
        % (o0.x, o1.x, o0.y, o1.y, o0.z, o1.z, i0.x, i1.x, i0.y, i1.y, i0.z, zc))

    portals = [o for o in bpy.data.objects if o.type == "MESH"
               and o.name.upper().startswith("PRT_") and not o.name.upper().startswith("PRT_195")]

    def portal_rect(p):
        c = p.matrix_world.translation
        lx = max(abs(v.co.x) for v in p.data.vertices)
        lz = max(abs(v.co.z) for v in p.data.vertices)
        n = Vector((p.matrix_world[0][1], p.matrix_world[1][1], p.matrix_world[2][1])).normalized()
        return c, n, lx, lz

    # --- перегородки (границы смежных комнат, с перпендикулярными диапазонами) ---
    rw = room_walls([wb(o) for o in rooms]) if DO_PARTITIONS else []
    py = sorted(set(v for (axis, v, _p0, _p1) in rw if axis == "y"))
    px = sorted(set(v for (axis, v, _p0, _p1) in rw if axis == "x"))
    log("перегородки Y: %s  X: %s" % (", ".join("%.2f" % v for v in py) or "нет",
                                      ", ".join("%.2f" % v for v in px) or "нет"))

    # --- стены и проёмы ---
    ext = {"Xmin": [], "Xmax": [], "Ymin": [], "Ymax": []}   # side -> [(y0,y1,z0,z1) | (x0,x1,z0,z1)]
    doors = []   # (cx, cy, cz, axis, hw_tangent, hh)

    def near_plane(v, planes):
        return any(abs(v - p) < 0.6 for p in planes)

    for p in portals:
        c, n, lx, lz = portal_rect(p)
        if abs(n.x) > 0.5:
            box = (c.y - lx + EPS, c.y + lx - EPS, c.z - lz + EPS, c.z + lz - EPS)
            if DO_PARTITIONS and near_plane(c.x, px):
                doors.append((c.x, c.y, c.z, "x", lx, lz))
            else:
                side = "Xmax" if c.x > (o0.x + o1.x) * 0.5 else "Xmin"
                ext[side].append(box)
        elif abs(n.y) > 0.5:
            box = (c.x - lx + EPS, c.x + lx - EPS, c.z - lz + EPS, c.z + lz - EPS)
            if DO_PARTITIONS and near_plane(c.y, py):
                doors.append((c.x, c.y, c.z, "y", lx, lz))
            else:
                side = "Ymax" if c.y > (o0.y + o1.y) * 0.5 else "Ymin"
                ext[side].append(box)

    walls = []
    walls.append((i0.x, i1.x, i0.y, i1.y, o0.z, i0.z, []))      # пол
    walls.append((i0.x, i1.x, i0.y, i1.y, zc, o1.z, []))        # потолок
    walls.append((o0.x, i0.x, o0.y, o1.y, o0.z, o1.z,
                  [(o0.x, i0.x, y0, y1, z0, z1) for (y0, y1, z0, z1) in ext["Xmin"]]))
    walls.append((i1.x, o1.x, o0.y, o1.y, o0.z, o1.z,
                  [(i1.x, o1.x, y0, y1, z0, z1) for (y0, y1, z0, z1) in ext["Xmax"]]))
    walls.append((i0.x, i1.x, o0.y, i0.y, o0.z, o1.z,
                  [(x0, x1, o0.y, i0.y, z0, z1) for (x0, x1, z0, z1) in ext["Ymin"]]))
    walls.append((i0.x, i1.x, i1.y, o1.y, o0.z, o1.z,
                  [(x0, x1, i1.y, o1.y, z0, z1) for (x0, x1, z0, z1) in ext["Ymax"]]))

    # перегородки
    for (axis, v, p0, p1) in rw:
        if axis == "y":   # горизонтальная стена y=v, тянется по X [p0..p1]
            opens = []
            for (dx, dy, dz, ax, dlx, dlz) in doors:
                if ax == "y" and abs(dy - v) < 0.6 and p0 <= dx <= p1:
                    opens.append((dx - dlx + EPS, dx + dlx - EPS,
                                  v - PART_T / 2, v + PART_T / 2,
                                  dz - dlz + EPS, dz + dlz - EPS))
            walls.append((p0, p1, v - PART_T / 2, v + PART_T / 2, i0.z, zc, opens))
            log("   Y-стена y=%.2f  x[%.2f..%.2f]  дверей: %d" % (v, p0, p1, len(opens)))
        else:             # вертикальная стена x=v, тянется по Y [p0..p1]
            opens = []
            for (dx, dy, dz, ax, dlx, dlz) in doors:
                if ax == "x" and abs(dx - v) < 0.6 and p0 <= dy <= p1:
                    opens.append((v - PART_T / 2, v + PART_T / 2,
                                  dy - dlx + EPS, dy + dlx - EPS,
                                  dz - dlz + EPS, dz + dlz - EPS))
            walls.append((v - PART_T / 2, v + PART_T / 2, p0, p1, i0.z, zc, opens))
            log("   X-стена x=%.2f  y[%.2f..%.2f]  дверей: %d" % (v, p0, p1, len(opens)))
    if DO_PARTITIONS:
        log("перегородок: %d, стен всего: %d" % (len(rw), len(walls)))
    else:
        log("перегородки выключены (BSP_PARTITIONS=0)")

    log("порталов: %d (наружных %d, дверей %d)" % (len(portals), len(portals) - len(doors), len(doors)))

    filler_data = None
    if FILLER and rooms:
        filler_data = (i0, i1, zc, room_bounds)
        log("заполнитель: вкл (%d комнат, вырез автоматически — solid)" % len(room_bounds))
    else:
        log("заполнитель: выкл")

    verts, quads = build_boundary(walls, filler_data)
    log("сетка: verts=%d quads=%d" % (len(verts), len(quads)))

    me = bpy.data.meshes.new("BSP_Shell")
    me.from_pydata([tuple(v) for v in verts], [], quads)
    me.update()
    ob = bpy.data.objects.new("BSP_Shell", me)
    bpy.context.scene.collection.objects.link(ob)

    bm2 = bmesh.new()
    bm2.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm2, faces=bm2.faces[:])
    bmesh.ops.triangulate(bm2, faces=bm2.faces[:])
    bm2.to_mesh(ob.data)
    bm2.free()
    ob.data.update()

    mat = get_dummy()
    if mat is not None:
        ob.data.materials.append(mat)
    check_bsp(ob)
    log("ИТОГ готов")


main()
