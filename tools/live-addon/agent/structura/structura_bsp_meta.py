# -*- coding: utf-8 -*-
"""
Structura BSP meta patcher — выставляет в .xob.meta флаги генерации BSP.

Правильная структура (образец — 97-50_Panelka):

    Common TXOCommonClass "{...}" : "{...}MeshObjectCommon.conf" {
     GenerateBSP 1
     ForceCreatePortals 1
    }

Патчим на:
     GenerateBSP 1
     ForceCreatePortals 0      <- именно 0: ForceCreatePortals ОТКЛЮЧАЕТ построение BSP

Важно: ключи должны лежать НЕПОСРЕДСТВЕННО в блоке Common, рядом с GenerateBSP
(не внутри BSPDiagnostics!). Патчер построчный и не трогает вложенность.

Запуск:
    python structura_bsp_meta.py            # dry-run, только отчёт
    python structura_bsp_meta.py --apply    # применить (с бэкапами)
    python structura_bsp_meta.py --apply --only House_Individual_Brus_Modul_1
    python structura_bsp_meta.py --apply --restore   # вернуть из бэкапа и выйти
"""

import os
import re
import io
import sys
import shutil

sys.path.insert(0, r"C:\Users\yshky")
from structura_target import ADDON_ROOT as ADDON, BACKUP_ROOT, MODULE

BACKUP = os.path.join(BACKUP_ROOT, "bsp_meta")

WANT_BSP = "1"
WANT_PORTALS = "0"

RE_GEN = re.compile(r'^(\s*)GenerateBSP\s+\S+\s*$')
RE_FCP = re.compile(r'^(\s*)ForceCreatePortals\s+\S+\s*$')
RE_COMMON_OPEN = re.compile(r'^\s*Common TXOCommonClass\s+"\{[0-9A-Fa-f]{16}\}"\s*:')


def rel(p):
    return os.path.relpath(p, ADDON).replace("\\", "/")


def read(p):
    with io.open(p, "r", encoding="utf-8", errors="surrogateescape", newline="") as f:
        return f.read()


def write(p, t):
    with io.open(p, "w", encoding="utf-8", errors="surrogateescape", newline="") as f:
        f.write(t)


def patch_text(t):
    """Нормализовать пары GenerateBSP/ForceCreatePortals. Вернуть (текст, блоков)."""
    nl = "\r\n" if "\r\n" in t else "\n"
    lines = t.replace("\r\n", "\n").split("\n")
    has_gen = any(RE_GEN.match(ln) for ln in lines)

    out = []
    skip = False
    changed = 0

    for i, ln in enumerate(lines):
        if skip:
            skip = False
            continue

        # 1) ключ уже есть — нормализуем значение и гарантируем соседний ForceCreatePortals
        m = RE_GEN.match(ln)
        if m:
            ind = m.group(1)
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            out.append("%sGenerateBSP %s" % (ind, WANT_BSP))
            if RE_FCP.match(nxt):
                skip = True
            out.append("%sForceCreatePortals %s" % (ind, WANT_PORTALS))
            changed += 1
            continue

        # 2) ключей в файле нет вообще — вставляем сразу после открытия каждого Common-блока
        if not has_gen and RE_COMMON_OPEN.match(ln):
            out.append(ln)
            out.append("   GenerateBSP %s" % WANT_BSP)
            out.append("   ForceCreatePortals %s" % WANT_PORTALS)
            changed += 1
            continue

        out.append(ln)

    return nl.join(out), changed


def main():
    apply = "--apply" in sys.argv
    restore = "--restore" in sys.argv
    only = []
    if "--only" in sys.argv:
        only = [x.strip().lower() for x in sys.argv[sys.argv.index("--only") + 1].split(",") if x.strip()]
    if not only and "--all" not in sys.argv:
        # по умолчанию — только текущее здание из structura_target.py
        only = [MODULE.lower()]

    total = changed = skipped = 0
    for dp, dns, fns in os.walk(ADDON):
        for fn in fns:
            if not fn.endswith(".xob.meta"):
                continue
            p = os.path.join(dp, fn)
            # имя FBX может отличаться от MODULE (Modul_5: ..._Modul_5_Brus.fbx),
            # поэтому матчим и имя файла, и путь (папка здания = MODULE всегда)
            relpath = os.path.relpath(p, ADDON).replace("\\", "/").lower()
            if only and not any(o in fn.lower() or o in relpath for o in only):
                continue
            # только те модели, где реально есть BSP-геометрия
            fbx = p[:-9] + ".fbx"
            if not os.path.exists(fbx):
                continue
            try:
                with open(fbx, "rb") as f:
                    if b"BSP_" not in f.read():
                        continue
            except Exception:
                continue

            d = os.path.join(BACKUP, rel(p).replace("/", os.sep))
            total += 1

            if restore:
                if os.path.exists(d):
                    shutil.copy2(d, p)
                    print("  RESTORE %s" % rel(p))
                else:
                    print("  ! нет бэкапа для %s" % rel(p))
                continue

            t = read(p)
            new, n = patch_text(t)
            if new == t:
                skipped += 1
                continue
            changed += 1
            print("  %-90s блоков: %d" % (rel(p)[-90:], n))
            if apply:
                os.makedirs(os.path.dirname(d), exist_ok=True)
                if not os.path.exists(d):
                    shutil.copy2(p, d)
                write(p, new)

    print()
    print("мет всего: %d   изменено: %d   без изменений: %d   режим: %s" %
          (total, changed, skipped, "RESTORE" if restore else ("APPLY" if apply else "DRY-RUN")))
    if apply and not restore:
        print("BACKUP:", BACKUP)


if __name__ == "__main__":
    main()
