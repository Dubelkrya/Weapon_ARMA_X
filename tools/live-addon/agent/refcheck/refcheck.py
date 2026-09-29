# -*- coding: utf-8 -*-
"""
refcheck — проверка ссылок {GUID}path в аддоне ARMST Weapons.

Использование (Python из Blender или любой Python 3):
    python refcheck.py            # только отчёт
    python refcheck.py --map      # сначала перестроить карту ванильных ресурсов из .rdb

Карта ванильных ресурсов строится из файлов resourceDatabase.rdb игры
(<Arma Reforger>/addons/data/resourceDatabase.rdb и addons/core/...).

Классы ссылок:
  ADDON-OK     — GUID есть в метах аддона и путь совпадает
  ADDON-PATH   — GUID есть в метах аддона, путь отличается        (надо чинить путь)
  VANILLA-OK   — путь есть в ванили, GUID совпадает
  VANILLA-GUID — путь есть в ванили, GUID ДРУГОЙ                  (надо чинить GUID)
  UNRESOLVED   — не найдено в карте (может быть движковым ресурсом, зависимостью мода
                 или реально висячей ссылкой — карта .rdb неполная)
"""
import os, re, io, sys, json, glob, struct, collections

ADDON = os.environ.get("ARMST_ADDON", r"C:\Users\yshky\OneDrive\Документы\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons")
GAME = os.environ.get("ARMA_GAME", r"C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger")
MAP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vanilla_map.json")

NAME_RE = re.compile(r'Name\s+"\{([0-9A-Fa-f]{16})\}([^"]*)"')
REF_RE = re.compile(r'"\{([0-9A-Fa-f]{16})\}([^"]*)"')
EXTS = ('.meta', '.et', '.conf', '.emat', '.c', '.layer', '.ent', '.gproj')
# движковые конфиги: их нет в .rdb, ссылки на них нормальны
SKIP_PREFIX = ("Configs/System/ResourceTypes/",)
MARK = bytes([6, 0, 0, 0, 0, 0])
ML = 6


def rel(p):
    return os.path.relpath(p, ADDON).replace("\\", "/")


def read(p):
    with io.open(p, "r", encoding="utf-8", errors="surrogateescape", newline="") as f:
        return f.read()


def build_vanilla_map():
    p2g, g2p = {}, {}
    for rdb in glob.glob(os.path.join(GAME, "**", "*.rdb"), recursive=True):
        d = open(rdb, "rb").read()
        J, pos = [], 0
        while True:
            j = d.find(MARK, pos)
            if j < 0:
                break
            J.append(j); pos = j + 1
        for i in range(1, len(J)):
            j = J[i]
            if j - 1 < 0 or d[j - 1] != 0:
                continue
            start = J[i - 1] + ML + 8 + 4 + 4 + 4
            if start > j - 1:
                continue
            raw = d[start:j - 1]
            if len(raw) < 3:
                continue
            L = struct.unpack_from("<I", d, start - 4)[0]
            if L != len(raw) + 1:
                continue
            try:
                path = raw.decode("ascii")
            except Exception:
                continue
            if "/" not in path:
                continue
            g = "%016X" % struct.unpack_from("<Q", d, j + ML)[0]
            p2g.setdefault(path, g); g2p.setdefault(g, path)
    io.open(MAP_PATH, "w", encoding="utf-8").write(json.dumps({"path2guid": p2g, "guid2path": g2p}))
    print("карта ванильных ресурсов: %d записей -> %s" % (len(p2g), MAP_PATH))
    return p2g


def addon_map():
    g2p = {}
    for dp, dns, fns in os.walk(ADDON):
        if os.sep + "agent" + os.sep in dp + os.sep:
            continue
        for fn in fns:
            if not fn.endswith(".meta"):
                continue
            mp = os.path.join(dp, fn); res = mp[:-5]
            if not os.path.exists(res):
                continue
            m = NAME_RE.search(read(mp))
            if m:
                g2p[m.group(1).upper()] = rel(res)
    return g2p


def main():
    if "--map" in sys.argv or not os.path.exists(MAP_PATH):
        v_p2g = build_vanilla_map()
    else:
        v_p2g = json.load(io.open(MAP_PATH, "r", encoding="utf-8"))["path2guid"]

    g2p = addon_map()
    cnt = collections.Counter()
    samples = collections.defaultdict(list)
    unresolved = collections.Counter()

    for dp, dns, fns in os.walk(ADDON):
        if os.sep + "agent" + os.sep in dp + os.sep:
            continue
        for fn in fns:
            if not fn.endswith(EXTS):
                continue
            p = os.path.join(dp, fn)
            for g, path in REF_RE.findall(read(p)):
                if not path or (("/" not in path) and ("." not in path)):
                    continue
                if path.startswith(SKIP_PREFIX):
                    continue
                g = g.upper()
                if g in g2p:
                    if g2p[g].lower() == path.lower():
                        cnt["ADDON-OK"] += 1
                    else:
                        cnt["ADDON-PATH"] += 1
                        if len(samples["ADDON-PATH"]) < 10:
                            samples["ADDON-PATH"].append("{%s}%s -> %s  (%s)" % (g, path, g2p[g], rel(p)))
                elif path in v_p2g:
                    if v_p2g[path].upper() == g:
                        cnt["VANILLA-OK"] += 1
                    else:
                        cnt["VANILLA-GUID"] += 1
                        if len(samples["VANILLA-GUID"]) < 10:
                            samples["VANILLA-GUID"].append("{%s}%s -> {%s}%s  (%s)" % (g, path, v_p2g[path], path, rel(p)))
                else:
                    cnt["UNRESOLVED"] += 1
                    unresolved[(g, path)] += 1

    print("мет аддона: %d   ванильных записей: %d" % (len(g2p), len(v_p2g)))
    for k in ("ADDON-OK", "ADDON-PATH", "VANILLA-OK", "VANILLA-GUID", "UNRESOLVED"):
        print("  %-13s %d" % (k, cnt[k]))
    for k in ("ADDON-PATH", "VANILLA-GUID"):
        if samples[k]:
            print("\n=== %s ===" % k)
            for s in samples[k]:
                print("   " + s)
    if unresolved:
        print("\n=== UNRESOLVED (уникальных %d) — требуют ручной проверки ===" % len(unresolved))
        for (g, path), n in unresolved.most_common(40):
            print("   x%-3d {%s}%s" % (n, g, path))


if __name__ == "__main__":
    main()
