# -*- coding: utf-8 -*-
r"""
Сканер МОДЕЛЕЙ Arm_Structura: по всем .fbx в Assets\ показывает, что уже оборудовано.

Для каждой модели:
  прт — порталы PRT_*          (сколько уникальных имён)
  bsp — геометрия BSP_*
  box — BOXVOL_* / SPHVOL_*
  ком — коллайдеры помещений UTM_*Room*
  дв  — Socket_Door*
  окн — Socket_Win*
  исп — сколько .et аддона ссылается на модель
  кб  — размер fbx

Статус:
  готово            — есть и порталы, и BSP
  нужны порталы+BSP — есть помещения/сокеты, но оборудования нет
  нет сокетов       — автоматически не оборудовать (не дом)

Запуск: python structura_scan_models.py
Пишет structura_model_scan.json + печатает таблицу.
"""

import os
import io
import re
import json
import sys
from collections import defaultdict

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ADDON = r"C:\Users\yshky\OneDrive\Документы\My Games\ArmaReforgerWorkbench\addons\Arm_Structura\Arm_Structura"
ASSETS = os.path.join(ADDON, "Assets")
OUT_JSON = r"C:\Users\yshky\structura_model_scan.json"
OUT_MD = r"C:\Users\yshky\structura_model_scan.md"

RE_GEN = re.compile(rb'BSP_[A-Za-z0-9_]{0,40}')
RE_PRT = re.compile(rb'PRT_[A-Za-z0-9_]{0,40}')
RE_BOX = re.compile(rb'(?:BOX|SPH)VOL_[A-Za-z0-9_]{0,40}')
RE_ROOM = re.compile(rb'UTM_[A-Za-z0-9_]{0,60}?Room[A-Za-z0-9_]{0,10}')
RE_DOOR = re.compile(rb'Socket_Door[A-Za-z0-9_]{0,10}')
RE_WIN = re.compile(rb'Socket_Win[A-Za-z0-9_]{0,10}')
RE_REF = re.compile(r'\{[0-9A-Fa-f]{16}\}([^"\s]+\.(?:xob|fbx))')
RE_REF2 = re.compile(r'([A-Za-z0-9_./-]+\.(?:xob|fbx))', re.I)


def main():
    print("ADDON:", ADDON)

    # ссылки на модели из всех .et аддона (использование)
    use = defaultdict(int)
    for dp, dns, fns in os.walk(ADDON):
        for fn in fns:
            if not fn.endswith(".et"):
                continue
            try:
                t = io.open(os.path.join(dp, fn), "r", encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            for r in RE_REF.findall(t):
                use[r.replace("\\", "/").lower()] += 1
            for r in RE_REF2.findall(t):
                use[r.replace("\\", "/").lower()] += 1

    # все модели
    models = []
    for dp, dns, fns in os.walk(ASSETS):
        for fn in fns:
            if fn.lower().endswith(".fbx"):
                models.append(os.path.join(dp, fn))
    models.sort()
    print("моделей (.fbx): %d" % len(models))

    rows = []
    for i, p in enumerate(models):
        rel = os.path.relpath(p, ADDON).replace(os.sep, "/")
        try:
            d = open(p, "rb").read()
        except Exception:
            continue
        prt = set(m.group(0) for m in RE_PRT.finditer(d))
        prt = set(x for x in prt if not x.lower().startswith(b"prt_195") and not x.lower().startswith(b"prt_70"))
        gen = set(m.group(0) for m in RE_GEN.finditer(d))
        box = set(m.group(0) for m in RE_BOX.finditer(d))
        room = set(m.group(0) for m in RE_ROOM.finditer(d))
        door = set(m.group(0) for m in RE_DOOR.finditer(d))
        win = set(m.group(0) for m in RE_WIN.finditer(d))
        r = {
            "model": rel,
            "kb": len(d) // 1024,
            "prt": len(prt), "bsp": len(gen), "box": len(box),
            "rooms": len(room), "doors": len(door), "wins": len(win),
            "use": use.get(rel.lower(), 0),
        }
        if r["prt"] and r["bsp"]:
            r["status"] = "готово"
        elif r["rooms"] or r["doors"] or r["wins"]:
            r["status"] = "нужны порталы+BSP"
        else:
            r["status"] = "нет сокетов"
        # приоритет
        s = 0
        if r["rooms"]:
            s += 30
        if r["doors"] or r["wins"]:
            s += 20
        if r["prt"] == 0:
            s += 25
        if r["bsp"] == 0:
            s += 15
        s += min(r["use"], 20)
        r["score"] = s
        rows.append(r)
        if (i + 1) % 50 == 0:
            print("   ... %d/%d" % (i + 1, len(models)))

    rows.sort(key=lambda r: (-r["score"], r["model"]))

    print()
    print("%-62s %3s %3s %3s %3s %3s %3s %4s %5s  %s" %
          ("модель", "прт", "bsp", "box", "ком", "дв", "окн", "исп", "кб", "статус"))
    print("-" * 150)
    for r in rows:
        short = r["model"].replace("Assets/", "").replace("assets/", "")
        print("%-62s %3d %3d %3d %3d %3d %3d %4d %5d  %s" %
              (short[-62:], r["prt"], r["bsp"], r["box"], r["rooms"], r["doors"],
               r["wins"], r["use"], r["kb"], r["status"]))

    print()
    print("сводка:")
    for st in ("готово", "нужны порталы+BSP", "нет сокетов"):
        n = len([r for r in rows if r["status"] == st])
        print("   %-22s %d" % (st, n))
    print("   всего моделей        %d" % len(rows))

    io.open(OUT_JSON, "w", encoding="utf-8").write(json.dumps(rows, ensure_ascii=False, indent=1))
    print()
    print("JSON:", OUT_JSON)

    md = io.open(OUT_MD, "w", encoding="utf-8")
    md.write("# Arm_Structura: что уже оборудовано в моделях\n\n")
    md.write("прт — порталы PRT_*, bsp — геометрия BSP_*, box — BOXVOL/SPHVOL,\n")
    md.write("ком — коллайдеры UTM_*Room*, дв/окн — Socket_Door*/Socket_Win*.\n\n")
    md.write("| модель | прт | bsp | box | ком | дв | окн | кб | статус |\n")
    md.write("|---|---:|---:|---:|---:|---:|---:|---:|---|\n")
    for r in rows:
        md.write("| `%s` | %d | %d | %d | %d | %d | %d | %d | %s |\n" % (
            r["model"], r["prt"], r["bsp"], r["box"], r["rooms"], r["doors"],
            r["wins"], r["kb"], r["status"]))
    md.close()
    print("MD  :", OUT_MD)


if __name__ == "__main__":
    main()
