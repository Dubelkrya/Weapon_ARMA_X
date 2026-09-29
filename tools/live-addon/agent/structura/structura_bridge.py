# -*- coding: utf-8 -*-
r"""
Мост RWTK: поставить запрос на реимпорт и прочитать результат/ошибки.

  python structura_bridge.py post [имя_модуля]   # положить запрос в inbox
  python structura_bridge.py read                # результат + свежие ошибки из лога
  python structura_bridge.py log [N]             # последние N строк RESOURCES из лога

Порядок работы:
  1) я:    structura_bridge.py post
  2) ты:   в Workbench нажать "RWTK: Process Bridge Queue" (один раз)
  3) я:    structura_bridge.py read  -> вижу PASS/REJECTED и все ошибки движка
"""

import os
import io
import re
import sys
import glob
import shutil

sys.path.insert(0, r"C:\Users\yshky")
try:
    from structura_target import ADDON_PREFIX, MODULE, FBX_PATH
except Exception:
    ADDON_PREFIX, MODULE = "$ARMSTPLATFORMStructura:", "House_Individual_Brus_Modul_2"
    FBX_PATH = ""

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PROFILE = r"C:\Users\yshky\OneDrive\Документы\My Games\ArmaReforgerWorkbench\profile\RWTKBridge"
INBOX = os.path.join(PROFILE, "inbox")
OUTBOX = os.path.join(PROFILE, "outbox")
TARGETS = os.path.join(PROFILE, "reimport.txt")

REQ_TMPL = ("RWTK_WORKBENCH_BRIDGE_REQUEST_V1\n"
            "request_id={rid}\n"
            "task_id={rid}\n"
            "operation=bridge.reimport\n"
            "mode=write\n"
            "END\n")

KEY = re.compile(r"(Build failed|Build successful|\(E\)|\(W\)|ERROR|CRITICAL|AreaPortal|BSP|leak|Rebuilding|Reimporting)")


def res_path():
    """$PREFIX:Assets/.../Modul.fbx"""
    rel = FBX_PATH.replace("\\", "/")
    i = rel.lower().find("/assets/")
    if i < 0:
        return None
    return ADDON_PREFIX + rel[i + 1:]


def next_id():
    used = []
    for f in os.listdir(INBOX):
        m = re.match(r"reimport(\d+)\.request\.rwtk$", f)
        if m:
            used.append(int(m.group(1)))
    return "reimport%03d" % ((max(used) if used else 0) + 1)


def post():
    target = res_path()
    if not target:
        print("! не смог собрать путь ресурса из", FBX_PATH)
        return
    if os.path.exists(TARGETS) and not os.path.exists(TARGETS + ".bak"):
        shutil.copy2(TARGETS, TARGETS + ".bak")
    io.open(TARGETS, "w", encoding="utf-8", newline="\n").write(target + "\n")
    rid = next_id()
    io.open(os.path.join(INBOX, rid + ".request.rwtk"), "w", encoding="utf-8", newline="\n").write(
        REQ_TMPL.format(rid=rid))
    io.open(os.path.join(INBOX, rid + ".ready"), "w", encoding="utf-8", newline="\n").write("ready\n")
    print("reimport.txt :", target)
    print("запрос       :", rid)
    print()
    print(">>> теперь в Workbench: Plugins -> RWTK/Bridge -> 'RWTK: Process Bridge Queue'")


def newest_result():
    fs = glob.glob(os.path.join(OUTBOX, "*.result.rwtk"))
    if not fs:
        return None, None
    fs.sort(key=os.path.getmtime)
    p = fs[-1]
    return p, io.open(p, "r", encoding="utf-8", errors="replace").read()


def log_dir():
    wl = r"C:\Users\yshky\OneDrive\Документы\My Games\ArmaReforgerWorkbench\logs"
    if not os.path.isdir(wl):
        return None
    ds = [os.path.join(wl, d) for d in os.listdir(wl) if os.path.isdir(os.path.join(wl, d))]
    ds.sort(key=os.path.getmtime)
    return ds[-1] if ds else None


def read():
    p, txt = newest_result()
    print("=== последний результат моста ===")
    print(txt.strip() if txt else "(результатов нет — нажми плагин в Workbench)")
    if txt and "status=PASS" not in txt:
        print("!! запрос не выполнен")
        return
    d = log_dir()
    if not d:
        print("(нет каталога логов)"); return
    lines = io.open(os.path.join(d, "console.log"), "r", encoding="utf-8", errors="replace").read().splitlines()
    idx = [i for i, l in enumerate(lines) if "Reimporting" in l or "Rebuilding" in l]
    start = idx[-1] if idx else max(0, len(lines) - 60)
    print()
    print("=== движок (лог Workbench), начиная с последней сборки ===")
    for i in range(max(0, start - 2), len(lines)):
        if KEY.search(lines[i]):
            print("%6d| %s" % (i + 1, lines[i][:200]))


def log(n=60):
    d = log_dir()
    if not d:
        print("(нет каталога логов)"); return
    lines = io.open(os.path.join(d, "console.log"), "r", encoding="utf-8", errors="replace").read().splitlines()
    sel = [l for l in lines if KEY.search(l)]
    for l in sel[-int(n):]:
        print(l[:200])


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "read"
    if cmd == "post":
        post()
    elif cmd == "read":
        read()
    elif cmd == "log":
        log(sys.argv[2] if len(sys.argv) > 2 else 60)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
