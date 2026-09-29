#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Аудит префабов аддона по правилам наследования (см. docs/PREFAB_CREATION_GUIDE_RU.md).
Проверки:
  1) .et без .meta
  2) дубли ID компонентов внутри файла
  3) один и тот же класс компонента 2+ раз (дубли-смелл)
  4) новый ID для класса, который уже приходит по наследованию (нарушение правила override)
  5) компоненты с Enabled 0 (hand-waved отключения)
  6) родитель не разрешается ни в аддоне, ни в ваниле (висячая ссылка)
  7) meta.Name путь != фактический путь файла
  8) ссылки Prefab "{GUID}...(что-то.et)" без .meta в аддоне и без записи в ваниле
"""
import os, re, sys, io, json, collections

ADDON = r"C:\Users\yshky\OneDrive\Документы\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons"
VANILLA_RDB = r"C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger\addons\data\resourceDatabase.rdb"
OUTDIR = os.path.join(ADDON, "agent", "prefab_audit")

GUID_RE = re.compile(r"^[0-9A-Fa-f]{16}$")
PARENT_RE = re.compile(r"^\s*\w+\s*:\s*\"\{([0-9A-Fa-f]{16})\}([^\"]+)\"\s*\{")
ID_RE = re.compile(r"^\s*ID\s+\"([0-9A-Fa-f]{16})\"")
# объявление на 2-м уровне вложенности внутри components { ... }
COMP_RE = re.compile(r"^  ([A-Za-z_][A-Za-z0-9_]*)\s+\"\{([0-9A-Fa-f]{16})\}\"\s*\{")
PREFAB_REF_RE = re.compile(r"\"\{([0-9A-Fa-f]{16})\}([^\"]*\.et)\"")
ENABLED0_RE = re.compile(r"^\s*Enabled\s+0\s*$")

def read(p):
    with io.open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()

# ---------- 1. собрать карту GUID -> .et (по .meta) и путь -> файл ----------
guid_to_et = {}       # guid(meta) -> abs .et path
meta_path_mismatch = []
et_files = []
for dirpath, dirnames, filenames in os.walk(os.path.join(ADDON, "Prefabs")):
    for fn in filenames:
        if fn.endswith(".et"):
            et_files.append(os.path.join(dirpath, fn))
et_files.sort()

for et in et_files:
    mp = et + ".meta"
    if not os.path.exists(mp):
        continue
    txt = "\n".join(read(mp))
    m = re.search(r"Name\s+\"\{([0-9A-Fa-f]{16})\}([^\"]+)\"", txt)
    if not m:
        continue
    g, declared = m.group(1), m.group(2)
    guid_to_et[g] = et
    # фактический относительный путь
    rel = os.path.relpath(et, ADDON).replace("\\", "/")
    if declared.lower() != rel.lower():
        meta_path_mismatch.append((rel, declared, g))

# ---------- ванильные пути (чтобы отличать «ванильный родитель» от «висячей ссылки») ----------
vanilla_guids = set()
vanilla_paths = set()
if os.path.exists(VANILLA_RDB):
    data = open(VANILLA_RDB, "rb").read()
    # быстрый проход: пути вида ...et внутри rdb
    for m in re.finditer(rb"[ -~]{4,200}\.et", data):
        try:
            vanilla_paths.add(m.group(0).decode("ascii", "replace"))
        except Exception:
            pass
    # GUID идут после строки (LE) — соберём все 16-hex токены как «возможные» гуиды
    for m in re.finditer(rb"[\x20-\x7e]{4,200}\.et\x00\x06\x00\x00\x00\x00\x00", data):
        pos = m.end()
        g = data[pos:pos+8]
        if len(g) == 8:
            vanilla_guids.add("".join("%02X" % b for b in g[::-1]))

def is_vanilla_guid(g):
    return (g in vanilla_guids) or (g.upper() in vanilla_guids)

# ---------- 2. разбор префабов ----------
prefabs = {}   # path -> dict(parent_guid, parent_path, id, comps[(class,id,line)], enabled0[(class,line)], refs[(guid,path,line)])
for et in et_files:
    lines = read(et)
    p = {"parent_guid": None, "parent_path": None, "id": None,
         "comps": [], "enabled0": [], "refs": [], "lines": lines}
    for i, ln in enumerate(lines):
        if i == 0:
            m = PARENT_RE.match(ln)
            if m:
                p["parent_guid"], p["parent_path"] = m.group(1), m.group(2)
        m = ID_RE.match(ln)
        if m and p["id"] is None:
            p["id"] = m.group(1)
        m = COMP_RE.match(ln)
        if m:
            p["comps"].append((m.group(1), m.group(2), i + 1))
        if ENABLED0_RE.match(ln):
            p["enabled0"].append((i + 1, ln.strip()))
        for m in PREFAB_REF_RE.finditer(ln):
            p["refs"].append((m.group(1), m.group(2), i + 1))
    prefabs[et] = p

def rel(p):
    return os.path.relpath(p, ADDON).replace("\\", "/")

# ---------- 3. проверки ----------
report = []
issues = collections.Counter()

# 3.1 нет .meta
no_meta = [rel(e) for e in et_files if not os.path.exists(e + ".meta")]
issues["no_meta"] = len(no_meta)

# 3.2/3.3 дубли ID и дубли классов
dup_id = []
dup_class = []
for et, p in prefabs.items():
    ids = collections.Counter(c[1] for c in p["comps"])
    for i, n in ids.items():
        if n > 1:
            dup_id.append((rel(et), i, n))
    cls = collections.Counter(c[0] for c in p["comps"])
    for c, n in cls.items():
        if n > 1:
            dup_class.append((rel(et), c, n, [x[1] for x in p["comps"] if x[0] == c]))
issues["dup_id"] = len(dup_id)
issues["dup_class"] = len(dup_class)

# 3.4 новый ID вместо переопределения (ищем вверх по цепочке наследования в аддоне)
def chain(et, depth=12):
    seen = []
    cur = et
    for _ in range(depth):
        p = prefabs.get(cur)
        if not p or not p["parent_guid"]:
            break
        nxt = guid_to_et.get(p["parent_guid"])
        if not nxt:
            break
        seen.append(nxt)
        cur = nxt
    return seen

new_id_violations = []
for et, p in prefabs.items():
    anc = chain(et)
    if not anc:
        continue
    anc_comps = []   # (class, id, owner)
    for a in anc:
        for c in prefabs[a]["comps"]:
            anc_comps.append((c[0], c[1], rel(a)))
    for (cls, cid, line) in p["comps"]:
        for (acls, acid, aowner) in anc_comps:
            if acls == cls and acid != cid:
                new_id_violations.append((rel(et), cls, cid, acid, aowner, line))
issues["new_id_violation"] = len(new_id_violations)

# 3.5 Enabled 0 (все, для ручного разбора)
enabled0 = [(rel(et), l, s) for et, p in prefabs.items() for (l, s) in p["enabled0"]]
issues["enabled0"] = len(enabled0)

# 3.6 родитель не разрешается
dangling_parent = []
for et, p in prefabs.items():
    if p["parent_guid"] and p["parent_guid"] not in guid_to_et:
        if not is_vanilla_guid(p["parent_guid"]):
            dangling_parent.append((rel(et), p["parent_guid"], p["parent_path"]))
issues["dangling_parent"] = len(dangling_parent)

# 3.7 meta path mismatch
issues["meta_path_mismatch"] = len(meta_path_mismatch)

# 3.8 висячие ссылки Prefab на .et
dangling_refs = []
for et, p in prefabs.items():
    for (g, path, ln) in p["refs"]:
        if g in guid_to_et:
            continue
        base = path.split("/")[-1]
        if base in [os.path.basename(x) for x in guid_to_et.values()]:
            continue
        if path in vanilla_paths or base in [os.path.basename(x) for x in vanilla_paths]:
            continue
        dangling_refs.append((rel(et), g, path, ln))
issues["dangling_ref"] = len(dangling_refs)

# ---------- 4. отчёт ----------
os.makedirs(OUTDIR, exist_ok=True)
md = []
md.append("# Аудит префабов аддона: наследование и правила (read-only)\n")
md.append(f"- Префабов разобрано: **{len(et_files)}**")
md.append(f"- Всего в аддоне `.et` (вкл. `agent/`): **{sum(1 for r,_,fs in os.walk(ADDON) for f in fs if f.endswith('.et'))}**")
md.append("")
md.append("## Сводка\n")
md.append("| Проверка | Найдено |")
md.append("|---|---|")
md.append(f"| `.et` без `.meta` | {issues['no_meta']} |")
md.append(f"| дубли ID компонентов в файле | {issues['dup_id']} |")
md.append(f"| один класс компонента 2+ раз | {issues['dup_class']} |")
md.append(f"| новый ID вместо override унаследованного класса | {issues['new_id_violation']} |")
md.append(f"| компоненты с `Enabled 0` | {issues['enabled0']} |")
md.append(f"| родитель не разрешается (ни аддон, ни ваниль) | {issues['dangling_parent']} |")
md.append(f"| `meta.Name` путь != фактический | {issues['meta_path_mismatch']} |")
md.append(f"| висячие ссылки `Prefab \"{{GUID}}*.et\"` | {issues['dangling_ref']} |")
md.append("")

def sec(title, rows, fmt):
    md.append(f"## {title}\n")
    if not rows:
        md.append("_нет_\n")
        return
    for r in rows:
        md.append(fmt(r))
    md.append("")

sec("1. Префабы без .meta", no_meta, lambda r: f"- `{r}`")
sec("2. Дубли ID компонентов", dup_id, lambda r: f"- `{r[0]}` — ID `{r[1]}` ×{r[2]}")
sec("3. Один класс компонента 2+ раза", dup_class, lambda r: f"- `{r[0]}` — `{r[1]}` ×{r[2]} (ID: {', '.join(r[3])})")
sec("4. Новый ID вместо override (класс уже приходит по наследованию)",
    new_id_violations,
    lambda r: f"- `{r[0]}` — класс `{r[1]}` объявлен с ID `{r[2]}`, а в предке `{r[4]}` он с ID `{r[3]}` (строка {r[5]})")
sec("5. Родитель не разрешается", dangling_parent, lambda r: f"- `{r[0]}` — parent `{{{r[1]}}}{r[2]}`")
sec("6. meta.Name путь != фактический", meta_path_mismatch, lambda r: f"- `{r[0]}` — meta говорит `{r[1]}`")
sec("7. Висячие ссылки Prefab", dangling_refs, lambda r: f"- `{r[0]}` стр.{r[3]} — `{{{r[1]}}}{r[2]}`")
sec("8. Enabled 0 (для ручного разбора)", enabled0, lambda r: f"- `{r[0]}` стр.{r[1]} — `{r[2]}`")

with io.open(os.path.join(OUTDIR, "prefab_inheritance_audit.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md))

print("PREFABS:", len(et_files))
for k, v in issues.items():
    print(f"  {k}: {v}")
print("report:", os.path.join(OUTDIR, "prefab_inheritance_audit.md"))
