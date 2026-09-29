# -*- coding: utf-8 -*-
"""
Structura interior v3 — BSP по помещениям + BOXVOL + порталы.

Порядок:
  1) удалить старые PRT_*, BOXVOL_*, BSP_*
  2) ПОРТАЛЫ: сканирование 4 стен -> 6 проёмов (окна/наружная дверь), нормаль внутрь
  3) BSP: 4 полые оболочки по помещениям (стены+пол+потолок) с вырезанными проёмами:
       - наружные проёмы (из шага 2)
       - внутренние двери (по сокетам Socket_Door_*, стандарт 0.9 x 2.0)
     Помещения: Room1 / Room2 / Room3, причём Room3 делится на «маленькую» и «коридор»
     по стене, где стоит Socket_Door_01.
  4) BOXVOL_01: объём интерьера

ЗАПУСК: Blender GUI -> Scripting -> Run Script (сцена с импортированным зданием).
"""

import bpy
from mathutils import Vector, Matrix

# ----------------------------- НАСТРОЙКИ -----------------------------
DRY_RUN = False
WALL_T = 0.15            # толщина стен BSP-оболочки
DOOR_W, DOOR_H = 0.90, 2.00   # стандартный проём внутренней двери
# Внутренние дверные порталы: по-стеночный BSP (structura_bsp_simple.py) делает
# сквозной проём в перегородке + один портал. Требует BSP_PARTITIONS=1 (по умолчанию).
DO_INTERIOR_DOORS = True
CLEANUP_LODS = True      # merge by distance у LOD-мешей (убирает short edges)

OUT = 0.6
OPEN_MIN = 0.5
STEP = 0.05
MIN_W, MAX_W = 0.35, 3.00
MIN_H, MAX_H = 0.35, 2.80

DUMMY_KEY = "dummyvolume"
DUMMY_NAME = "dummyvolume_D3975B51F51E6BD5"
PORTAL_MAT = "PRT_195x72"
# ---------------------------------------------------------------------

def log(m):
    print("[INT] " + m)

def usage_of(o):
    for k in o.keys():
        if k.lower() == "usage":
            try:
                return o[k]
            except Exception:
                return None
    return None

def world_bbox(objs):
    xs = []; ys = []; zs = []
    for o in objs:
        for c in o.bound_box:
            p = o.matrix_world @ Vector(c)
            xs.append(p.x); ys.append(p.y); zs.append(p.z)
    if not xs:
        return None, None
    return Vector((min(xs), min(ys), min(zs))), Vector((max(xs), max(ys), max(zs)))

def get_dummy():
    m = bpy.data.materials.get(DUMMY_NAME)
    if m is None:
        try:
            from EnfusionBlenderTools.core.materials.material_io import create_game_material
            m = create_game_material(DUMMY_KEY, DUMMY_NAME)
        except Exception as e:
            log("! dummyvolume: %s" % e)
    return m

# ---------------------------- геометрия ----------------------------
def triangulate_obj(obj):
    try:
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()
    except Exception as e:
        log("    ! триангуляция: %s" % e)

def cleanup_mesh(obj, merge=0.0001):
    """merge by distance у LOD-меша (убирает short edges).
    ВАЖНО: recalc_face_normals здесь НЕ вызываем — меш дома не замкнут,
    Blender выбирает ориентацию произвольно и выворачивает часть стен."""
    try:
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=merge)
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()
        log("    cleanup: %s (merge<=%.2f мм)" % (obj.name, merge * 1000))
    except Exception as e:
        log("    ! cleanup %s: %s" % (obj.name, e))

def add_box(name, bmin, bmax):
    x0, y0, z0 = bmin.x, bmin.y, bmin.z
    x1, y1, z1 = bmax.x, bmax.y, bmax.z
    verts = [Vector(v) for v in (
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
    faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj

def bool_diff(target, cutter):
    try:
        mod = target.modifiers.new("cut", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.object = cutter
        try:
            mod.solver = "EXACT"
        except Exception:
            pass
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except Exception as e:
        log("    ! boolean: %s" % e)
    finally:
        try:
            bpy.data.objects.remove(cutter, do_unlink=True)
        except Exception:
            pass

def make_room_shell(name, bmin, bmax, holes, step=0.5):
    """Оболочка помещения: тонкие ЗАМКНУТЫЕ плиты-тайлы (манифолд), ячейки внутри проёмов пропускаются."""
    verts = []
    faces = []

    def add_slab(cmin, cmax):
        x0, y0, z0 = cmin.x, cmin.y, cmin.z
        x1, y1, z1 = cmax.x, cmax.y, cmax.z
        i = len(verts)
        verts.extend([Vector(v) for v in (
            (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
            (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))])
        faces.extend([(i, i + 1, i + 2, i + 3), (i + 4, i + 7, i + 6, i + 5),
                      (i, i + 4, i + 5, i + 1), (i + 1, i + 5, i + 6, i + 2),
                      (i + 2, i + 6, i + 7, i + 3), (i + 3, i + 7, i + 4, i)])

    def in_hole(c):
        for (hmin, hmax) in holes:
            if hmin.x <= c.x <= hmax.x and hmin.y <= c.y <= hmax.y and hmin.z <= c.z <= hmax.z:
                return True
        return False

    dx = bmax.x - bmin.x; dy = bmax.y - bmin.y; dz = bmax.z - bmin.z
    ht = WALL_T / 2.0

    # стены перпендикулярные X
    ny = max(1, int(dy / step)); nz = max(1, int(dz / step))
    for x in (bmin.x, bmax.x):
        for iy in range(ny):
            y0 = bmin.y + dy * iy / ny; y1 = bmin.y + dy * (iy + 1) / ny
            for iz in range(nz):
                z0 = bmin.z + dz * iz / nz; z1 = bmin.z + dz * (iz + 1) / nz
                if in_hole(Vector((x, (y0 + y1) / 2, (z0 + z1) / 2))):
                    continue
                add_slab(Vector((x - ht, y0, z0)), Vector((x + ht, y1, z1)))

    # стены перпендикулярные Y
    nx = max(1, int(dx / step)); nz = max(1, int(dz / step))
    for y in (bmin.y, bmax.y):
        for ix in range(nx):
            x0 = bmin.x + dx * ix / nx; x1 = bmin.x + dx * (ix + 1) / nx
            for iz in range(nz):
                z0 = bmin.z + dz * iz / nz; z1 = bmin.z + dz * (iz + 1) / nz
                if in_hole(Vector(((x0 + x1) / 2, y, (z0 + z1) / 2))):
                    continue
                add_slab(Vector((x0, y - ht, z0)), Vector((x1, y + ht, z1)))

    # пол и потолок
    nx = max(1, int(dx / step)); ny = max(1, int(dy / step))
    for z in (bmin.z, bmax.z):
        for ix in range(nx):
            x0 = bmin.x + dx * ix / nx; x1 = bmin.x + dx * (ix + 1) / nx
            for iy in range(ny):
                y0 = bmin.y + dy * iy / ny; y1 = bmin.y + dy * (iy + 1) / ny
                if in_hole(Vector(((x0 + x1) / 2, (y0 + y1) / 2, z))):
                    continue
                add_slab(Vector((x0, y0, z - ht)), Vector((x1, y1, z + ht)))

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    mat = get_dummy()
    if mat is not None:
        obj.data.materials.append(mat)
    if "usage" in obj.keys():
        del obj["usage"]
    return obj

def cutter_from_portal(center, normal, tangent, hw, hh):
    """Коробка-вырез для наружного проёма (поперёк стены)."""
    up = Vector((0, 0, 1))
    d = WALL_T + 0.20
    cmin = center - tangent * hw - up * hh - normal * (d / 2)
    cmax = center + tangent * hw + up * hh + normal * (d / 2)
    return (Vector((min(cmin.x, cmax.x), min(cmin.y, cmax.y), min(cmin.z, cmax.z))),
            Vector((max(cmin.x, cmax.x), max(cmin.y, cmax.y), max(cmin.z, cmax.z))))

def cutter_from_socket(sock, rooms):
    """Коробка-вырез для внутренней двери по сокету (стена — ближайшая к сокету граница помещения)."""
    p = sock.matrix_world.translation.copy()
    best = None
    for (rmin, rmax) in rooms:
        if not (rmin.x - 0.6 <= p.x <= rmax.x + 0.6 and rmin.y - 0.6 <= p.y <= rmax.y + 0.6):
            continue
        dx = min(abs(p.x - rmin.x), abs(p.x - rmax.x))
        dy = min(abs(p.y - rmin.y), abs(p.y - rmax.y))
        if best is None or min(dx, dy) < best[0]:
            best = (min(dx, dy), dx <= dy)
    if best is None:
        return None
    _, along_x = best
    z0 = p.z - 0.2
    z1 = z0 + DOOR_H
    if along_x:      # стена перпендикулярна X -> проём тянется по Y
        return (Vector((p.x - WALL_T, p.y - DOOR_W / 2, z0)),
                Vector((p.x + WALL_T, p.y + DOOR_W / 2, z1)))
    else:
        return (Vector((p.x - DOOR_W / 2, p.y - WALL_T, z0)),
                Vector((p.x + DOOR_W / 2, p.y + WALL_T, z1)))

def room_walls(bounds, tol=0.6):
    """Перегородки: список (axis, v, perp0, perp1).
    axis='x' -> стена на x=v, тянется по Y [perp0..perp1];
    axis='y' -> стена на y=v, тянется по X [perp0..perp1].
    Диапазон = ОБЪЕДИНЕНИЕ перпендикулярных диапазонов двух смежных комнат,
    сегменты на одной плоскости сливаются."""
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

# ---------------------------- порталы ----------------------------
def cast(mesh, origin_w, dir_w, limit):
    mw = mesh.matrix_world
    inv = mw.inverted()
    o_l = inv @ origin_w
    d_l = inv.to_3x3() @ dir_w
    if d_l.length < 1e-9:
        return None
    d_l.normalize()
    hit, loc, _n, _i = mesh.ray_cast(o_l, d_l, distance=limit)
    if not hit:
        return None
    return ((mw @ loc) - origin_w).length

def is_open(mesh, point_on_wall, normal):
    origin = point_on_wall + normal * OUT
    d = cast(mesh, origin, -normal, OUT + 3.0)
    return (d is None) or (d > OUT + OPEN_MIN)

def wall_middle_offset(mesh, point, normal, tangent, offset=0.30):
    for s in (offset, -offset):
        p = point + tangent * s
        origin = p + normal * OUT
        d1 = cast(mesh, origin, -normal, OUT + 3.0)
        if d1 is None:
            continue
        o2 = origin + (-normal) * (d1 + 0.005)
        d2 = cast(mesh, o2, -normal, 1.5)
        if d2 is None:
            continue
        outer = OUT - d1
        inner = OUT - (d1 + 0.005 + d2)
        mid = (outer + inner) / 2.0
        if abs(mid) < 1.0:
            return mid, (outer - inner)
    return 0.0, 0.0

def scan_walls(mesh, walls, z0, z1):
    """walls: list of (normal, plane, tangent, u0, u1, name).
    Сканирует каждую стену сеткой рейкастов, кластеризует проёмы.
    Возвращает (center, normal, tangent, hw, hh, name, w, h)."""
    result = []
    for normal, plane, tangent, u0, u1, name in walls:
        nu = int((u1 - u0) / STEP) + 1
        nv = int((z1 - z0) / STEP) + 1
        grid = [[False] * nv for _ in range(nu)]
        for i in range(nu):
            u = u0 + i * STEP
            for j in range(nv):
                v = z0 + j * STEP
                p = tangent * u + Vector((0, 0, v))
                if normal.x != 0:
                    p.x = plane
                else:
                    p.y = plane
                grid[i][j] = is_open(mesh, p, normal)
        core = [[False] * nv for _ in range(nu)]
        for i in range(nu):
            for j in range(nv):
                if not grid[i][j]:
                    continue
                ok = True
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        a, b = i + di, j + dj
                        if 0 <= a < nu and 0 <= b < nv and not grid[a][b]:
                            ok = False
                core[i][j] = ok
        seen = [[False] * nv for _ in range(nu)]
        for i in range(nu):
            for j in range(nv):
                if not core[i][j] or seen[i][j]:
                    continue
                stack = [(i, j)]; seen[i][j] = True; cells = []
                while stack:
                    a, b = stack.pop(); cells.append((a, b))
                    for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        na, nb = a + da, b + db
                        if 0 <= na < nu and 0 <= nb < nv and core[na][nb] and not seen[na][nb]:
                            seen[na][nb] = True; stack.append((na, nb))
                i0 = max(0, min(c[0] for c in cells) - 1); i1 = min(nu - 1, max(c[0] for c in cells) + 1)
                j0 = max(0, min(c[1] for c in cells) - 1); j1 = min(nv - 1, max(c[1] for c in cells) + 1)
                w = (i1 - i0 + 1) * STEP
                h = (j1 - j0 + 1) * STEP
                if not (MIN_W <= w <= MAX_W and MIN_H <= h <= MAX_H):
                    continue
                cu = u0 + (i0 + i1) / 2.0 * STEP
                cv = z0 + (j0 + j1) / 2.0 * STEP
                center = tangent * cu + Vector((0, 0, cv))
                if normal.x != 0:
                    center.x = plane
                else:
                    center.y = plane
                mid, thick = wall_middle_offset(mesh, center, normal, tangent,
                                                offset=max(0.4, (w / 2.0) + 0.25))
                center = center + normal * mid
                result.append((center, normal, tangent, w / 2.0, h / 2.0, name, w, h))
                log("    %s: проём %.2f x %.2f м в (%.2f %.2f %.2f)  стена %.2f м" %
                    (name, w, h, center.x, center.y, center.z, abs(thick)))
    return result


def find_openings(mesh, bb_min, bb_max):
    walls = [
        (Vector((1, 0, 0)),  bb_max.x, Vector((0, 1, 0)), bb_min.y, bb_max.y, "+X"),
        (Vector((-1, 0, 0)), bb_min.x, Vector((0, 1, 0)), bb_min.y, bb_max.y, "-X"),
        (Vector((0, 1, 0)),  bb_max.y, Vector((1, 0, 0)), bb_min.x, bb_max.x, "+Y"),
        (Vector((0, -1, 0)), bb_min.y, Vector((1, 0, 0)), bb_min.x, bb_max.x, "-Y"),
    ]
    return scan_walls(mesh, walls, bb_min.z, bb_max.z)


def find_interior_doors(mesh, partitions, z0, z1):
    """Внутренние двери: сканируем плоскости перегородок (без сокетов).
    partitions: list of (axis, v, perp0, perp1) — как в room_walls."""
    walls = []
    for (axis, v, p0, p1) in partitions:
        if axis == "x":
            walls.append((Vector((1, 0, 0)), v, Vector((0, 1, 0)), p0, p1, "дверь"))
        else:
            walls.append((Vector((0, 1, 0)), v, Vector((1, 0, 0)), p0, p1, "дверь"))
    result = scan_walls(mesh, walls, z0, z1)
    # отсеять щели у торцов стен / узкие проёмы, которые не являются дверью
    return [r for r in result if r[6] >= 0.6 and r[7] <= 2.6]

def door_axis(mesh, p):
    """Ось нормали стены двери + высота замера внутри проёма.
    Ищем точку, откуда вдоль одной из осей 'свободно' дальше всего (сквозь проём)."""
    up = Vector((0, 0, 1))
    best = None
    for dh in (0.8, 1.2, 0.4, 1.6, 0.0):
        q = p + up * dh
        for nrm in (Vector((1, 0, 0)), Vector((0, 1, 0))):
            ds = [cast(mesh, q, nrm, 5.0), cast(mesh, q, -nrm, 5.0)]
            near = min([d for d in ds if d is not None] or [5.0])
            if best is None or near > best[0]:
                best = (near, nrm, dh)
    return best[1], best[2]


def portal_from_socket(sock, mesh):
    """Портал для двери по сокету (внутренние двери).
    Возвращает (center, normal, tangent, hw, hh, sock_name, w, h) или None."""
    p = sock.matrix_world.translation.copy()
    normal, dh = door_axis(mesh, p)
    tangent = Vector((0, 1, 0)) if abs(normal.x) > 0.5 else Vector((1, 0, 0))
    q = p + Vector((0, 0, dh))

    # ширина проёма (вдоль стены до рамы) на «свободной» высоте
    a = cast(mesh, q, tangent, 2.5)
    b = cast(mesh, q, -tangent, 2.5)
    w = (a + b) if (a is not None and b is not None) else DOOR_W
    if not (0.6 <= w <= 2.0):
        w = DOOR_W
    # высота: вверх до перемычки, вниз до пола
    up = cast(mesh, p, Vector((0, 0, 1)), 3.5)
    dn = cast(mesh, p, Vector((0, 0, -1)), 3.5)
    if up is not None and dn is not None and 1.6 <= (up + dn) <= 2.9:
        h = up + dn
        cz = p.z + (up - dn) / 2.0
    else:
        h = DOOR_H
        cz = p.z

    mid, thick = wall_middle_offset(mesh, p, normal, tangent,
                                    offset=max(0.8, w / 2.0 + 0.3))
    center = Vector((p.x, p.y, cz)) + normal * mid
    log("    %s: проём %.2f x %.2f м, ось %s, стена %.2f м, в толщу %.3f м" %
        (sock.name, w, h, "X" if abs(normal.x) > 0.5 else "Y", abs(thick), mid))
    return (center, normal, tangent, w / 2.0 + 0.05, h / 2.0 + 0.05, sock.name, w, h)


def make_portal(name, center, normal, tangent, hw, hh, mat):
    up = Vector((0, 0, 1))
    verts = [Vector((-hw, 0, -hh)), Vector((hw, 0, -hh)), Vector((hw, 0, hh)), Vector((-hw, 0, hh))]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    n_in = -normal
    # правый базис, иначе объект «зеркалится» и нормали выворачиваются при экспорте
    if tangent.dot(n_in.cross(up)) < 0:
        tangent = -tangent
    obj.matrix_world = Matrix((
        (tangent.x, n_in.x, up.x, center.x),
        (tangent.y, n_in.y, up.y, center.y),
        (tangent.z, n_in.z, up.z, center.z),
        (0.0, 0.0, 0.0, 1.0)))
    if mat is not None:
        obj.data.materials.append(mat)
    return obj

# ---------------------------- MAIN ----------------------------
def main():
    log("---- start  DRY_RUN=%s  WALL_T=%.2f" % (DRY_RUN, WALL_T))

    lod0 = next((o for o in bpy.data.objects if o.type == "MESH" and "lod0" in o.name.lower()), None)
    if lod0 is None:
        log("! LOD0-меш не найден"); return

    cols = [o for o in bpy.data.objects if o.type == "MESH" and usage_of(o)]

    def ends(o, *sfx):
        n = o.name.lower()
        return any(n.endswith(s) for s in sfx)

    # ВАЖНО: семейство называется "..._Brus", поэтому "brus" есть в имени ЛЮБОГО
    # коллайдера — фильтруем по СУФФИКСУ, а не по вхождению.
    wall_cols = [o for o in cols if ends(o, "_brus", "_wall")] or cols
    floor_cols = [o for o in cols if ends(o, "_floor")]
    cell_cols = [o for o in cols if ends(o, "_celling", "_ceiling")]
    roof_cols = [o for o in cols if ends(o, "_roof")]

    wmin, wmax = world_bbox(wall_cols)
    zf = world_bbox(floor_cols)[1].z if floor_cols else wmin.z
    if cell_cols:
        zc = world_bbox(cell_cols)[0].z
    elif roof_cols:
        zc = world_bbox(roof_cols)[0].z
    else:
        zc = wmax.z

    # границы для поиска проёмов — по LOD0 (коллайдеры могут быть смещены)
    band_lo, band_hi = zf + 0.4, zc - 0.4
    xs, ys = [], []
    for v in lod0.data.vertices:
        p = lod0.matrix_world @ v.co
        if band_lo <= p.z <= band_hi:
            xs.append(p.x)
            ys.append(p.y)
    if xs:
        bb_min = Vector((min(xs), min(ys), zf))
        bb_max = Vector((max(xs), max(ys), zc))
    else:
        bb_min, bb_max = wmin, wmax
    log("оболочка: bbox %.2f..%.2f  %.2f..%.2f  %.2f..%.2f" %
        (bb_min.x, bb_max.x, bb_min.y, bb_max.y, bb_min.z, bb_max.z))

    # 1) удалить старое (BOXVOL не трогаем — у здания может быть настроен свой)
    old = [o for o in bpy.data.objects if o.type == "MESH" and
           o.name.upper().startswith(("PRT_", "SPHVOL_", "BSP_"))]
    if old:
        log("удаляю старое: %d" % len(old))
        if not DRY_RUN:
            for o in old:
                bpy.data.objects.remove(o, do_unlink=True)

    # 1b) чистка LOD-мешей (short edges)
    if CLEANUP_LODS and not DRY_RUN:
        for o in bpy.data.objects:
            if o.type == "MESH" and "lod" in o.name.lower():
                cleanup_mesh(o)

    # 2) порталы (сначала — они дают наружные проёмы для BSP)
    mat = bpy.data.materials.get(PORTAL_MAT) or bpy.data.materials.new(PORTAL_MAT)
    log("сканирую стены...")
    openings = find_openings(lod0, bb_min, bb_max)
    log("найдено проёмов: %d" % len(openings))

    # 3) помещения
    rooms = []
    for o in cols:
        n = o.name.lower()
        if "room" in n:
            rmin, rmax = world_bbox([o])
            short = o.name.split("_")[-1] if o.name.split("_")[-1].isdigit() else o.name.split("_")[-2:][0]
            rooms.append((rmin, rmax, short))
    rooms.sort(key=lambda r: r[0].y)
    log("помещений-коллайдеров: %d -> %s" % (len(rooms), ", ".join(r[2] for r in rooms)))

    # Room3 делим по стене с Socket_Door_01 (если он внутри Room3)
    split = None
    sd1 = bpy.data.objects.get("Socket_Door_01")
    if sd1 is not None and rooms:
        p = sd1.matrix_world.translation
        for (rmin, rmax, nm) in rooms:
            if "room3" in nm.lower() and rmin.x - 0.5 <= p.x <= rmax.x + 0.5 and rmin.y - 0.5 <= p.y <= rmax.y + 0.5:
                split = (rmin, rmax, p.x)
    spaces = []
    for (rmin, rmax, nm) in rooms:
        if split and rmin is split[0] and rmax is split[1]:
            sx = split[2]
            spaces.append((Vector((rmin.x, rmin.y, rmin.z)), Vector((sx, rmax.y, rmax.z)), nm + "_small"))
            spaces.append((Vector((sx, rmin.y, rmin.z)), Vector((rmax.x, rmax.y, rmax.z)), nm + "_corridor"))
        else:
            spaces.append((rmin, rmax, nm))
    log("помещений для BSP: %d -> %s" % (len(spaces), ", ".join(s[2] for s in spaces)))

    # 4) BSP — строится отдельным скриптом structura_bsp_rooms.py (по правилам движка:
    #    триангуляция + замкнутость). Здесь больше не создаём.
    log("BSP не здесь — после этого скрипта запусти structura_bsp_rooms.py")

    # 5) BOXVOL — объём может называться BoxVol_01/BOXVOL_01, и после повторного
    #    экспорта мог размножиться в дубликаты. Оставляем один, лишние удаляем.
    if not DRY_RUN:
        vols = [o for o in bpy.data.objects
                if o.type == "MESH" and o.name.upper().startswith("BOXVOL")]
        if vols:
            boxvol = vols[0]
            boxvol.name = "BOXVOL_01"
            for dup in vols[1:]:
                log("удалён дубликат объёма: %s" % dup.name)
                bpy.data.objects.remove(dup, do_unlink=True)
            if len(boxvol.data.materials) == 0:
                m = get_dummy()
                if m is not None:
                    boxvol.data.materials.append(m)
                log("BOXVOL_01 уже есть — вернул материал dummyvolume")
            else:
                log("BOXVOL_01 уже есть — материал на месте")
        else:
            fcols = [o for o in cols if "floor" in o.name.lower() or "cell" in o.name.lower()]
            if fcols:
                fmin, fmax = world_bbox(fcols)
                bmin = Vector((fmin.x + 0.10, fmin.y + 0.10, bb_min.z))
                bmax = Vector((fmax.x - 0.10, fmax.y - 0.10, bb_max.z))
            else:
                bmin, bmax = bb_min, bb_max
            o = add_box("BOXVOL_01", bmin, bmax)
            m = get_dummy()
            if m is not None:
                o.data.materials.append(m)
            log("BOXVOL создан: %.2f x %.2f x %.2f" % (bmax.x - bmin.x, bmax.y - bmin.y, bmax.z - bmin.z))

    # 6) порталы — на КАЖДЫЙ проём: наружные окна/двери + внутренние двери
    if not DRY_RUN:
        specs = []
        for (center, normal, tangent, hw, hh, wall, w, h) in openings:
            specs.append(("стена " + wall, center, normal, tangent, hw, hh))

        if DO_INTERIOR_DOORS:
            door_sockets = [s for s in bpy.data.objects
                            if s.type == "EMPTY" and s.name.lower().startswith("socket_door")]
            if door_sockets:
                # по сокетам (Modul_1/2/3/5)
                for s in door_sockets:
                    sp = s.matrix_world.translation
                    # «уже покрыт» — по горизонтали (X/Y): сокет наружной двери стоит у пола,
                    # поэтому 3D-расстояние до центра проёма не работает
                    if any(Vector((sp.x - c.x, sp.y - c.y, 0.0)).length < 0.6
                           for (_n, c, _no, _t, _hw, _hh) in specs):
                        log("    %s: уже покрыт наружным проёмом — пропуск" % s.name)
                        continue
                    r = portal_from_socket(s, lod0)
                    if r is None:
                        log("    ! %s: портал не построен" % s.name)
                        continue
                    center, normal, tangent, hw, hh, _sn, _w, _h = r
                    specs.append(("дверь " + s.name, center, normal, tangent, hw, hh))
            else:
                # без сокетов — рейкаст внутренних перегородок (Modul_4)
                parts = room_walls([(rmin, rmax) for (rmin, rmax, _sn) in rooms])
                log("перегородок для рейкаста дверей: %d" % len(parts))
                for (axis, v, p0, p1) in parts:
                    log("    перегородка %s=%.2f [%.2f..%.2f]" % (axis.upper(), v, p0, p1))
                for r in find_interior_doors(lod0, parts, zf + 0.2, zc - 0.3):
                    center, normal, tangent, hw, hh, _name, _w, _h = r
                    if any(Vector((center.x - c.x, center.y - c.y, 0.0)).length < 0.6
                           for (_n, c, _no, _t, _hw, _hh) in specs):
                        continue
                    specs.append(("дверь", center, normal, tangent, hw + 0.05, hh + 0.05))

        for i, (what, center, normal, tangent, hw, hh) in enumerate(specs, 1):
            make_portal("PRT_%02d" % i, center, normal, tangent, hw, hh, mat)
        log("порталов создано: %d" % len(specs))
        for i, (what, center, normal, tangent, hw, hh) in enumerate(specs, 1):
            log("    PRT_%02d  %-22s (%.2f %.2f %.2f)  %.2f x %.2f м" %
                (i, what, center.x, center.y, center.z, hw * 2, hh * 2))

    log("---- done")

main()
