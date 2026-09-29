#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Исправления по отчёту agent/prefab_audit:
   1) armst_Optic_1P29.et: GUID родителя 0745A57C37C15101 -> 952D9BD7B6F8F591
   2) armst_Ammo_9x18_PP.et: путь ссылки Ammo_9x18_Ball_57N181.et -> ...57N181S.et
   3) все *.meta: Name "{GUID}старый_путь" -> фактический путь (GUID сохраняется)
Все изменения — с бэкапом в ARMST_Backups/.../audit_fixes/<relpath>.
"""
import os, re, io, shutil, sys

ADDON = r"C:\Users\yshky\OneDrive\Документы\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons"
BACKUP = r"C:\Users\yshky\OneDrive\Документы\ARMST_Backups\ARMST-PLATFORM---Weapons\audit_fixes"
NAME_RE = re.compile(r'(Name\s+"\{)([0-9A-Fa-f]{16})(\})([^"]*)(")')

def rel(p): return os.path.relpath(p, ADDON).replace("\\", "/")

def backup(path):
    r = rel(path)
    dst = os.path.join(BACKUP, r.replace("/", os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not os.path.exists(dst):
        shutil.copy2(path, dst)

def read_text(path):
    with io.open(path, "r", encoding="utf-8", errors="surrogateescape", newline="") as f:
        return f.read()

def write_text(path, txt):
    with io.open(path, "w", encoding="utf-8", errors="surrogateescape", newline="") as f:
        f.write(txt)

changed = []

# ---- 1) 1P29 parent GUID ----
p = os.path.join(ADDON, "Prefabs", "Weapons", "Attachments", "Optics", "Optic_1P29", "armst_Optic_1P29.et")
if os.path.exists(p):
    t = read_text(p)
    if "0745A57C37C15101" in t:
        backup(p)
        write_text(p, t.replace("0745A57C37C15101", "952D9BD7B6F8F591"))
        changed.append((rel(p), "1P29 parent GUID -> 952D9BD7B6F8F591"))
else:
    print("MISSING", p)

# ---- 2) ammo reference path ----
p = os.path.join(ADDON, "Prefabs", "Weapons", "Ammo", "armst_Ammo_9x18_PP.et")
if os.path.exists(p):
    t = read_text(p)
    if "Ammo_9x18_Ball_57N181.et" in t:
        backup(p)
        write_text(p, t.replace("Ammo_9x18_Ball_57N181.et", "Ammo_9x18_Ball_57N181S.et"))
        changed.append((rel(p), "ref path -> Ammo_9x18_Ball_57N181S.et"))
else:
    print("MISSING", p)

# ---- 3) все *.meta: путь в Name под фактическое расположение ----
fixed_metas = 0
for dp, dns, fns in os.walk(ADDON):
    if os.sep + "agent" + os.sep in dp + os.sep:
        continue
    for fn in fns:
        if not fn.endswith(".meta"):
            continue
        mp = os.path.join(dp, fn)
        # фактический ресурс = имя без .meta
        res = mp[:-5]
        if not os.path.exists(res):
            continue  # битая мета/не .meta ресурса
        actual = rel(res)
        t = read_text(mp)
        m = NAME_RE.search(t)
        if not m:
            continue
        declared = m.group(4)
        if declared.lower() == actual.lower():
            continue
        backup(mp)
        new = t[:m.start()] + m.group(1) + m.group(2) + m.group(3) + actual + m.group(5) + t[m.end():]
        write_text(mp, new)
        fixed_metas += 1

print("TEXT FIXES:")
for r, w in changed:
    print("  ", r, "->", w)
print("METAS FIXED:", fixed_metas)
print("BACKUP:", BACKUP)
