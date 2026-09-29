# -*- coding: utf-8 -*-
r"""
Structura — материалы здания в рабочее состояние (локальные .emat аддона).

Почему локальные: мост EBT не резолвит игровые ресурсы
  "Resource linked to material ... does not exist. {D3975B51F51E6BD5}Common/Materials/dummyvolume.emat"
и экспорт падает. Поэтому — как в 97-50_Panelka: свои .emat в Data\.

Что делает:
  1) PRT_195x72.emat -> класс MatLightPortal (вики: "material class must be set to MatLightPortal");
     если файла нет — создаёт его и .emat.meta со свежим GUID;
  2) dummyvolume_D3975B51F51E6BD5.emat — создаёт при отсутствии (MatPBRBasic);
  3) .xob.meta: MaterialAssigns -> локальные пути (по Name из .emat.meta).

Запуск: python structura_fix_materials.py [--apply]
"""

import os
import io
import re
import sys
import random
import shutil

sys.path.insert(0, r"C:\Users\yshky")
from structura_target import (BUILDING, DATA_DIR, META_PATH, BACKUP_ROOT, PORTAL_MAT,
                              DUMMY_NAME, ADDON_ROOT)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BACKUP = os.path.join(BACKUP_ROOT, "materials")

MATS = {
    PORTAL_MAT: "PRT_195x72.emat",
    DUMMY_NAME: "dummyvolume_D3975B51F51E6BD5.emat",
}

PORTAL_BODY = ('MatLightPortal {\n'
               ' ProjectionMap "{B4CC48A6C23A25F1}Assets/_SharedData/ProjectionMaps/A_window_195_EM.edds"\n'
               '}\n')
DUMMY_BODY = 'MatPBRBasic {\n}\n'

EMAT_META_TMPL = ('MetaFileClass {\n'
                  ' Name "{guid}{res}"\n'
                  ' Configurations {\n'
                  '  EMATResourceClass PC {\n'
                  '  }\n'
                  '  EMATResourceClass XBOX_ONE : PC {\n'
                  '  }\n'
                  '  EMATResourceClass XBOX_SERIES : PC {\n'
                  '  }\n'
                  '  EMATResourceClass PS4 : PC {\n'
                  '  }\n'
                  '  EMATResourceClass PS5 : PC {\n'
                  '  }\n'
                  '  EMATResourceClass HEADLESS : PC {\n'
                  '  }\n'
                  ' }\n'
                  '}\n')


def read(p):
    with io.open(p, "r", encoding="utf-8", errors="surrogateescape", newline="") as f:
        return f.read()


def write(p, t):
    with io.open(p, "w", encoding="utf-8", errors="surrogateescape", newline="") as f:
        f.write(t)


def backup(p):
    d = os.path.join(BACKUP, os.path.relpath(p, BUILDING).replace(os.sep, "__"))
    os.makedirs(BACKUP, exist_ok=True)
    if not os.path.exists(d):
        shutil.copy2(p, d)
        print("  BACKUP %s" % os.path.relpath(p, BUILDING))


def res_path(fn):
    """путь ресурса для меты: Assets/.../Data/<fn>"""
    rel = os.path.relpath(os.path.join(DATA_DIR, fn), ADDON_ROOT)
    return rel.replace(os.sep, "/")


def new_guid(addon_root):
    used = set()
    for dp, dns, fns in os.walk(addon_root):
        for f in fns:
            if f.endswith(".meta"):
                try:
                    t = io.open(os.path.join(dp, f), "r", encoding="utf-8", errors="replace").read(400)
                except Exception:
                    continue
                for m in re.finditer(r'\{([0-9A-Fa-f]{16})\}', t):
                    used.add(m.group(1).upper())
    while True:
        g = "".join(random.choice("0123456789ABCDEF") for _ in range(16))
        if g not in used:
            return "{%s}" % g


def meta_name(emat_path):
    p = emat_path + ".meta"
    if not os.path.exists(p):
        return None
    m = re.search(r'Name\s+"(\{[0-9A-Fa-f]{16}\}[^"]+\.emat)"', read(p))
    return m.group(1) if m else None


def main():
    apply = "--apply" in sys.argv
    print("режим: %s" % ("APPLY" if apply else "DRY-RUN"))
    print("здание: %s" % BUILDING)

    addon_root = ADDON_ROOT

    print()
    print("1) материалы в Data\\")
    ass = {}
    for src, fn in MATS.items():
        p = os.path.join(DATA_DIR, fn)
        body = PORTAL_BODY if src == PORTAL_MAT else DUMMY_BODY
        if not os.path.exists(p):
            print("   %-42s НЕТ -> создаю" % fn)
            if apply:
                os.makedirs(DATA_DIR, exist_ok=True)
                write(p, body)
                g = new_guid(addon_root)
                res = res_path(fn)
                write(p + ".meta", EMAT_META_TMPL.replace("{guid}", g).replace("{res}", res))
                print("      .emat.meta Name: %s%s" % (g, res))
        elif src == PORTAL_MAT:
            cur = read(p)
            if "MatLightPortal" in cur:
                print("   %-42s класс уже MatLightPortal ✓" % fn)
            else:
                print("   %-42s класс -> MatLightPortal" % fn)
                if apply:
                    backup(p)
                    write(p, PORTAL_BODY)
        else:
            print("   %-42s на месте" % fn)
        nm = meta_name(p)
        if nm:
            ass[src] = nm
        elif os.path.exists(p):
            g = new_guid(addon_root)
            res = res_path(fn)
            print("      .emat есть, а .meta нет -> создаю: %s%s" % (g, res))
            if apply:
                write(p + ".meta", EMAT_META_TMPL.replace("{guid}", g).replace("{res}", res))
            ass[src] = g + res
        else:
            print("      ! нет .emat.meta/Name")

    print()
    print("2) .xob.meta: MaterialAssigns -> локальные .emat")
    if not os.path.exists(META_PATH):
        print("   ! нет меты: %s" % META_PATH)
    else:
        t = read(META_PATH)
        for src, dst in ass.items():
            pat = re.compile(r'(SourceMaterial\s+"%s"\s*\n\s*AssignedMaterial\s*)"[^"]*"' % re.escape(src))
            if not pat.search(t):
                print("   ! нет SourceMaterial \"%s\" в мете (появится после первого реимпорта)" % src)
                continue
            new = pat.sub(lambda m: m.group(1) + '"%s"' % dst, t)
            if new == t:
                print("   %-42s уже локальный" % src)
            else:
                print("   %-42s -> %s" % (src, dst.split("/")[-1]))
                t = new
        if apply:
            write(META_PATH, t)

    print()
    print("2b) .xob.meta: переопределения MaterialAssigns (env STRUCTURA_MAT_ASSIGN_MAP)")
    ov_src = os.environ.get("STRUCTURA_MAT_ASSIGN_MAP", "")
    if ov_src:
        import json as _json
        try:
            ovm = _json.loads(ov_src)
        except Exception as e:
            print("   ! STRUCTURA_MAT_ASSIGN_MAP не json: %s" % e)
            ovm = {}
        t = read(META_PATH)
        for src, dst in ovm.items():
            pat = re.compile(r'(SourceMaterial\s+"%s"\s*\n\s*AssignedMaterial\s*)"[^"]*"' % re.escape(src))
            if not pat.search(t):
                print("   ! нет SourceMaterial \"%s\" в мете" % src)
                continue
            new = pat.sub(lambda m: m.group(1) + '"%s"' % dst, t)
            if new == t:
                print("   %-42s уже назначен" % src)
            else:
                print("   %-42s -> %s" % (src, dst.split("/")[-1]))
                t = new
        if apply:
            write(META_PATH, t)

    print()
    print("готово. Если APPLY — дальше structura_bsp_meta.py --apply и реимпорт.")


if __name__ == "__main__":
    main()
