# -*- coding: utf-8 -*-
r"""
BSP-оболочка здания — ОДНО замкнутое тело (стены + пол + потолок + перегородки с проёмами).

Перегородки определяются ПРОБИВКОЙ ЛУЧАМИ ПО ОБЪЁМУ (а не по коллайдерам/сокетам):
на сетке считаем свободное расстояние (4 луча ±X ±Y до первой поверхности);
линии, где почти везде "стена" — это перегородки. Внутренние порталы-двери
подтягиваются на ближайшую такую линию (их оси и позиции из сокетов бывают смещены).

Почему одно тело: этот билд движка роняет сборку ("Build failed"), если BSP
состоит из нескольких соприкасающихся объектов.
"""

import os
import sys

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, r"C:\Users\yshky")
try:
    from structura_target import DUMMY_NAME, DUMMY_KEY
except Exception:
    DUMMY_NAME = "dummyvolume_D3975B51F51E6BD5"
    DUMMY_KEY = "dummyvolume"

PART_T = 0.15
OVERLAP = 0.05
CUT_DEPTH = 0.30
MARGIN = 0.06
MIN_SLAB = 0.03

PROBE_THR = 0.35        # "стена" если свободное расстояние меньше
PROBE_FRAC = 0.45       # доля линии, которая должна быть стеной
PROBE_STEP = 0.05       # шаг поиска линий
PROBE_U = 0.20          # шаг точек вдоль линии

# Перегородки поперёк X (блок в средней полосе) не моделируем: на их стыках с
# Y-стенами булево объединение даёт незамкнутую топологию, и движок BSP отвергает.
# Для света/звука важнее наружная оболочка + порталы в проёмах.
USE_X_PARTITIONS = False


def log(m):
    print("[SHELL] " + m)


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


BOX_FACES = [(0, 3, 2), (0, 2, 1), (4, 5, 6), (4, 6, 7),
             (0, 1, 5), (0, 5, 4), (3, 7, 6), (3, 6, 2),
             (0, 4, 7), (0, 7, 3), (1, 2, 6), (1, 6, 5)]


def box_verts(bmin, bmax):
    x0, y0, z0 = bmin.x, bmin.y, bmin.z
    x1, y1, z1 = bmax.x, bmax.y, bmax.z
    return [Vector(v) for v in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                                (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]


def new_obj(name, verts, faces, mat=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if mat is not None:
        ob.data.materials.append(mat)
    return ob


def add_box(name, bmin, bmax, mat=None):
    return new_obj(name, box_verts(bmin, bmax), BOX_FACES, mat)


def bool_op(target, other, op):
    mod = target.modifiers.new(op.lower(), "BOOLEAN")
    mod.operation = op
    mod.object = other
    try:
        mod.solver = "EXACT"
    except Exception:
        pass
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)


def weld_and_tri(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.02)
    try:
        bmesh.ops.dissolve_degenerate(bm, dist=0.02, edges=bm.edges[:])
    except Exception:
        pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.02)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


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
    log("   %-12s %s" % (ob.name, "ГОДНО ✓" if not bad else ("ОШИБКА: " + ", ".join(bad))))
    if bad:
        try:
            for e in BV.get_non_manifold_edges(bm)[:8]:
                c = (e.verts[0].co + e.verts[1].co) * 0.5
                log("      незамкнутое ребро: (%.3f %.3f %.3f) len=%.4f faces=%d"
                    % (c.x, c.y, c.z, e.calc_length(), len(e.link_faces)))
            for v in [v for v in bm.verts if not v.is_manifold][:6]:
                log("      non-manifold вершина: (%.3f %.3f %.3f)" % (v.co.x, v.co.y, v.co.z))
        except Exception as e:
            log("      (детали: %s)" % e)
    bm.free()
    return not bad


def tidy_names():
    for me in list(bpy.data.meshes):
        if me.users == 0:
            bpy.data.meshes.remove(me)
    objs = [o for o in bpy.data.objects if o.type == "MESH" and o.data is not None]
    for i, o in enumerate(objs):
        try:
            o.data.name = "__tmp_%d__" % i
        except Exception:
            pass
    for o in objs:
        try:
            o.data.name = o.name
        except Exception:
            pass
    log("имена мешей выровнены по объектам (%d)" % len(objs))


def expand_inward(a, b, o0, o1, t=OVERLAP):
    for ax in ("x", "y", "z"):
        if getattr(a, ax) > getattr(o0, ax) + 1e-6:
            setattr(a, ax, getattr(a, ax) - t)
        if getattr(b, ax) < getattr(o1, ax) - 1e-6:
            setattr(b, ax, getattr(b, ax) + t)


def slab_ok(a, b):
    return (b.x - a.x > MIN_SLAB) and (b.y - a.y > MIN_SLAB) and (b.z - a.z > MIN_SLAB)


# ------------------------- пробивка объёма лучами -------------------------
def make_free(tree):
    dirs = [Vector((1, 0, 0)), Vector((-1, 0, 0)), Vector((0, 1, 0)), Vector((0, -1, 0))]
    lim = 2.0

    def free(p):
        best = lim
        for d in dirs:
            h = tree.ray_cast(p, d, lim)
            if h and h[0]:
                best = min(best, (h[0] - p).length)
        return best
    return free


def find_wall_segments(free, axis, lo, hi, u0, u1, z,
                       step=0.05, ustep=0.20, thr=0.25, min_span=1.2, edge=0.6):
    """Отрезки стен вдоль линий: (coord, u_start, u_end).
    Линии, у которых 'стена' доходит до краёв, отбрасываются (это наружные стены)."""
    raw = []
    v = lo
    while v <= hi:
        pat = []
        u = u0
        while u <= u1:
            p = Vector((u, v, z)) if axis == "y" else Vector((v, u, z))
            pat.append(free(p) < thr)
            u += ustep
        idx = [i for i, x in enumerate(pat) if x]
        if len(idx) >= 3:
            a, b = idx[0], idx[-1]
            span = (b - a + 1) * ustep
            touch = (u0 + a * ustep <= u0 + edge) or (u0 + b * ustep >= u1 - edge)
            if span >= min_span and not touch:
                raw.append((v, u0 + a * ustep, u0 + b * ustep))
        v += step
    # кластеризация по coord
    raw.sort()
    groups = []
    for v, a, b in raw:
        if groups and v - groups[-1][-1][0] <= step * 2.5:
            groups[-1].append((v, a, b))
        else:
            groups.append([(v, a, b)])
    out = []
    for g in groups:
        coord = sum(x[0] for x in g) / len(g)
        a = min(x[1] for x in g)
        b = max(x[2] for x in g)
        out.append((coord, a, b))
    return out


def main():
    old = [o for o in bpy.data.objects if o.type == "MESH" and o.name.upper().startswith("BSP_")]
    for o in old:
        bpy.data.objects.remove(o, do_unlink=True)
    log("удалено старых BSP: %d" % len(old))

    cols = [o for o in bpy.data.objects if o.type == "MESH" and usage_of(o)]
    rooms = [o for o in cols if "room" in o.name.lower()]
    brus = [o for o in cols if "brus" in o.name.lower()]
    cell = [o for o in cols if "cell" in o.name.lower()]
    roof = [o for o in cols if "roof" in o.name.lower()]
    if not brus:
        log("! нет Brus")
        return

    i0 = Vector((1e9, 1e9, 1e9))
    i1 = Vector((-1e9, -1e9, -1e9))
    for o in rooms:
        a, b = wb(o)
        i0 = Vector((min(i0.x, a.x), min(i0.y, a.y), min(i0.z, a.z)))
        i1 = Vector((max(i1.x, b.x), max(i1.y, b.y), max(i1.z, b.z)))
    o0, o1 = wb(brus[0])
    if not rooms:
        i0, i1 = o0, o1

    if cell:
        zc = min(wb(c)[0].z for c in cell)
        src = "Celling"
    elif roof:
        zc = min(wb(c)[0].z for c in roof)
        src = "Roof"
    else:
        zc = i1.z
        src = "по комнатам"
    log("коллайдеры: x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f | Brus z %.2f..%.2f | потолок %.2f (%s)"
        % (i0.x, i1.x, i0.y, i1.y, i0.z, i1.z, o0.z, o1.z, zc, src))

    lod0 = next((o for o in bpy.data.objects if o.type == "MESH" and "lod0" in o.name.lower()), None)
    if lod0 is None:
        log("! нет LOD0")
        return
    zlo, zhi = i0.z + 0.4, zc - 0.4
    bm = bmesh.new()
    bm.from_mesh(lod0.data)
    bm.transform(lod0.matrix_world)
    tree = BVHTree.FromBMesh(bm)
    free = make_free(tree)

    xs, ys = [], []
    for v in bm.verts:
        if zlo <= v.co.z <= zhi:
            xs.append(v.co.x)
            ys.append(v.co.y)
    if not xs:
        log("! нет геометрии стен в z %.2f..%.2f" % (zlo, zhi))
        return
    wt = ((o0.x - i0.x) + (o1.x - i1.x) + (o0.y - i0.y) + (o1.y - i1.y)) / 4.0
    if wt <= 0.02:
        wt = 0.23
    e0 = Vector((min(xs), min(ys), o0.z))
    e1 = Vector((max(xs), max(ys), o1.z))
    o0, o1 = e0, e1
    i0, i1 = Vector((e0.x + wt, e0.y + wt, i0.z)), Vector((e1.x - wt, e1.y - wt, zc))
    log("оболочка по LOD0: x %.2f..%.2f y %.2f..%.2f | стена %.2f | интерьер x %.2f..%.2f y %.2f..%.2f"
        % (o0.x, o1.x, o0.y, o1.y, wt, i0.x, i1.x, i0.y, i1.y))

    # ---- ПРОБИВКА на трёх высотах: настоящая стена есть на всех ----
    zs = [i0.z + 0.6, (i0.z + zc) * 0.5, zc - 0.6]

    def probe_multi(axis, lo, hi, u0, u1):
        sets = [find_wall_segments(free, axis, lo, hi, u0, u1, z, edge=-1.0) for z in zs]
        for z, s in zip(zs, sets):
            log("   [%.2f] %s: %s" % (z, axis.upper(),
                ", ".join("%.2f(%.1f..%.1f)" % (v, a, b) for v, a, b in s) or "нет"))
        # координата считается стеной, если встретилась на >= 2 высотах
        merged = []
        for s in sets:
            for v, a, b in s:
                hit = None
                for m in merged:
                    if abs(m[0] - v) <= 0.35:
                        hit = m
                        break
                if hit is None:
                    merged.append([v, a, b, 1])
                else:
                    hit[1] = min(hit[1], a)
                    hit[2] = max(hit[2], b)
                    hit[3] += 1
        return [(m[0], m[1], m[2]) for m in merged if m[3] >= 2]

    ysegs = probe_multi("y", i0.y + 0.6, i1.y - 0.6, i0.x + 0.6, i1.x - 0.6)
    xsegs = probe_multi("x", i0.x + 0.6, i1.x - 0.6, i0.y + 0.6, i1.y - 0.6)

    # если отрезок доходит до края области сканирования — это стена на всю длину
    def extend(segs, u0, u1, lo, hi):
        out = []
        for v, a, b in segs:
            if a <= u0 + 0.30:
                a = lo
            if b >= u1 - 0.30:
                b = hi
            out.append((v, a, b))
        return out

    ysegs = extend(ysegs, i0.x + 0.6, i1.x - 0.6, i0.x, i1.x)
    xsegs = extend(xsegs, i0.y + 0.6, i1.y - 0.6, i0.y, i1.y)

    # подрезаем X-стены, чтобы они шли МЕЖДУ Y-стенами (от граней, не до центров)
    if ysegs:
        ylo = min(s[0] for s in ysegs)
        yhi = max(s[0] for s in ysegs)
        xsegs = [(v, max(a, ylo + PART_T / 2), min(b, yhi - PART_T / 2))
                 for v, a, b in xsegs if max(a, ylo + PART_T / 2) < min(b, yhi - PART_T / 2)]

    log("   итог по Y: %s" % (", ".join("y=%.2f x %.2f..%.2f" % s for s in ysegs) or "нет"))
    log("   итог по X: %s" % (", ".join("x=%.2f y %.2f..%.2f" % s for s in xsegs) or "нет"))
    bm.free()

    order = [
        ("Wall_Xmin", Vector((o0.x, o0.y, o0.z)), Vector((i0.x, o1.y, o1.z))),
        ("Wall_Xmax", Vector((i1.x, o0.y, o0.z)), Vector((o1.x, o1.y, o1.z))),
        ("Wall_Ymin", Vector((i0.x, o0.y, o0.z)), Vector((i1.x, i0.y, o1.z))),
        ("Wall_Ymax", Vector((i0.x, i1.y, o0.z)), Vector((i1.x, o1.y, o1.z))),
        ("Floor", Vector((i0.x, i0.y, o0.z)), Vector((i1.x, i1.y, i0.z))),
        ("Ceiling", Vector((i0.x, i0.y, zc)), Vector((i1.x, i1.y, o1.z))),
    ]
    for v, a, b in ysegs:
        order.append(("Part_y%.2f" % v, Vector((a, v - PART_T / 2, i0.z)),
                      Vector((b, v + PART_T / 2, zc))))
    if USE_X_PARTITIONS:
        for v, a, b in xsegs:
            order.append(("Part_x%.2f" % v, Vector((v - PART_T / 2, a, i0.z)),
                          Vector((v + PART_T / 2, b, zc))))
    else:
        xsegs = []
        log("   перегородки поперёк X не моделируются (USE_X_PARTITIONS=False)")

    # ---- порталы: наружные -> в толщу стены, внутренние -> на ближайшую перегородку ----
    portals = [o for o in bpy.data.objects if o.type == "MESH"
               and o.name.upper().startswith("PRT_") and not o.name.upper().startswith("PRT_195")]
    interior_names = set()
    cx = (o0.x + o1.x) * 0.5
    cy = (o0.y + o1.y) * 0.5
    for p in portals:
        mw = p.matrix_world.copy()
        n = Vector((mw[0][1], mw[1][1], mw[2][1])).normalized()
        c = mw.translation.copy()
        old_c = c.copy()
        moved = False
        outer = False
        if abs(n.x) > 0.5 and (c.x < o0.x + wt + 0.15 or c.x > o1.x - wt - 0.15):
            c.x = (o0.x + wt / 2.0) if c.x < cx else (o1.x - wt / 2.0)
            moved = True
            outer = True
        elif abs(n.y) > 0.5 and (c.y < o0.y + wt + 0.15 or c.y > o1.y - wt - 0.15):
            c.y = (o0.y + wt / 2.0) if c.y < cy else (o1.y - wt / 2.0)
            moved = True
            outer = True
        if not outer:
            interior_names.add(p.name)
        if not outer:
            # внутренняя дверь: тянем на ближайшую найденную перегородку
            best = None
            for v, a, b in ysegs:
                if not (a - 0.3 <= c.x <= b + 0.3):
                    continue
                d = abs(c.y - v)
                if best is None or d < best[0]:
                    best = (d, "y", v)
            for v, a, b in xsegs:
                if not (a - 0.3 <= c.y <= b + 0.3):
                    continue
                d = abs(c.x - v)
                if best is None or d < best[0]:
                    best = (d, "x", v)
            if best and best[0] < 1.0:
                d, ax, v = best
                if ax == "y":
                    c.y = v
                    # нормаль портала -> по Y
                    t = Vector((0, 1, 0)); nn = Vector((0, -1, 0)); u = Vector((0, 0, 1))
                    mw = p.matrix_world.copy()
                    mw[0][0], mw[1][0], mw[2][0] = t.x, t.y, t.z
                    mw[0][1], mw[1][1], mw[2][1] = nn.x, nn.y, nn.z
                    mw[0][2], mw[1][2], mw[2][2] = u.x, u.y, u.z
                else:
                    c.x = v
                    t = Vector((0, 1, 0)); nn = Vector((1, 0, 0)); u = Vector((0, 0, 1))
                    mw = p.matrix_world.copy()
                    mw[0][0], mw[1][0], mw[2][0] = t.x, t.y, t.z
                    mw[0][1], mw[1][1], mw[2][1] = nn.x, nn.y, nn.z
                    mw[0][2], mw[1][2], mw[2][2] = u.x, u.y, u.z
                moved = True
        if moved:
            mw.translation = c
            p.matrix_world = mw
            log("   %s: %s -> (%.3f %.3f %.3f)" % (p.name,
                ("%.3f" % getattr(old_c, "x" if abs(n.x) > 0.5 else "y")), c.x, c.y, c.z))

    # портал не должен вылезать ниже пола / выше потолка (иначе вырез режет перекрытие).
    # Пол/потолок при объединении раздуты на OVERLAP — держим зазор больше.
    CLEAR = OVERLAP + 0.25
    for p in portals:
        vs = [p.matrix_world @ v.co for v in p.data.vertices]
        zmin = min(v.z for v in vs)
        zmax = max(v.z for v in vs)
        dz = 0.0
        if zmin < i0.z + CLEAR:
            dz = (i0.z + CLEAR) - zmin
        if zmax + dz > zc - CLEAR:
            dz = (zc - CLEAR) - zmax
        if abs(dz) > 1e-6:
            mw = p.matrix_world.copy()
            mw.translation = mw.translation + Vector((0, 0, dz))
            p.matrix_world = mw
            log("   %s: по высоте сдвинут на %.3f (пол %.2f / потолок %.2f)" % (p.name, dz, i0.z, zc))

    # ---- вырезы ----
    cutters = []
    for p in portals:
        lx = max(abs(v.co.x) for v in p.data.vertices) + MARGIN
        lz = max(abs(v.co.z) for v in p.data.vertices) + MARGIN
        m = p.matrix_world
        c = m.translation.copy()
        t = Vector((m[0][0], m[1][0], m[2][0])).normalized()
        n = Vector((m[0][1], m[1][1], m[2][1])).normalized()
        u = Vector((m[0][2], m[1][2], m[2][2])).normalized()
        corners = [(-lx, -CUT_DEPTH, -lz), (lx, -CUT_DEPTH, -lz), (lx, CUT_DEPTH, -lz), (-lx, CUT_DEPTH, -lz),
                   (-lx, -CUT_DEPTH, lz), (lx, -CUT_DEPTH, lz), (lx, CUT_DEPTH, lz), (-lx, CUT_DEPTH, lz)]
        cutters.append(new_obj("cut_" + p.name,
                               [c + t * a + n * b + u * cc for (a, b, cc) in corners], BOX_FACES))
    log("порталов/вырезов: %d | кусков: %d" % (len(cutters), len(order)))

    mat = get_dummy()
    if mat is None:
        log("! нет dummyvolume")
        return
    for nm, a, b in order:
        expand_inward(a, b, o0, o1)

    log("--- объединение в одно тело ---")
    base = None
    made = 0
    for nm, a, b in order:
        if not slab_ok(a, b):
            log("   ! вырожденный кусок: %s" % nm)
            continue
        ob = add_box("part_" + nm, a, b, mat)
        made += 1
        if base is None:
            base = ob
            continue
        try:
            bool_op(base, ob, "UNION")
        except Exception as e:
            log("   ! union %s: %s" % (nm, e))
        bpy.data.objects.remove(ob, do_unlink=True)
    if base is None:
        log("! нечего объединять")
        return
    base.name = "BSP_Shell"
    log("   кусков %d, verts=%d faces=%d" % (made, len(base.data.vertices), len(base.data.polygons)))

    for cut in cutters:
        pname = cut.name[4:] if cut.name.startswith("cut_") else cut.name
        if pname in interior_names and not os.environ.get("SHELL_CUT_INTERIOR"):
            bpy.data.objects.remove(cut, do_unlink=True)
            continue
        if os.environ.get("SHELL_NO_CUTS"):
            bpy.data.objects.remove(cut, do_unlink=True)
            continue
        try:
            bool_op(base, cut, "DIFFERENCE")
        except Exception as e:
            log("   ! cut %s: %s" % (cut.name, e))
        try:
            bm2 = bmesh.new()
            bm2.from_mesh(base.data)
            nme = len([e for e in bm2.edges if not e.is_manifold])
            nv = len([v for v in bm2.verts if not v.is_manifold])
            bm2.free()
            log("   после %-14s non-manifold: рёбер %d, вершин %d" % (cut.name, nme, nv))
        except Exception:
            pass
        bpy.data.objects.remove(cut, do_unlink=True)
    if os.environ.get("SHELL_NO_CUTS"):
        log("   (SHELL_NO_CUTS: вырезы пропущены — диагностика)")

    weld_and_tri(base)
    base.data.materials.clear()
    base.data.materials.append(mat)

    tidy_names()
    ok = check_bsp(base)
    log("ИТОГ: %s" % ("тело годно ✓" if ok else "есть проблемы ✗"))
    log("---- done. Дальше: export -> meta -> реимпорт")


main()
