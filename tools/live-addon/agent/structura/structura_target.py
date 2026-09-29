# -*- coding: utf-8 -*-
r"""
ЦЕЛЬ конвейера: какое здание обрабатываем. Меняется ОДНА строка — MODULE.

Все скрипты (interior / bsp_shell / export / fix_materials / bsp_meta)
подтягивают пути отсюда:

    import sys; sys.path.insert(0, r"C:\Users\yshky")
    from structura_target import *
"""

import os

# Переключатель цели: по умолчанию Modul_4; можно через env:
#   STRUCTURA_MODULE=House_Individual_Brus_Modul_5
#   STRUCTURA_FBX_NAME=House_Individual_Modul_5_Brus.fbx   (когда имя FBX не равно MODULE+".fbx")
MODULE = os.environ.get("STRUCTURA_MODULE", "House_Individual_Brus_Modul_4")
FBX_NAME = os.environ.get("STRUCTURA_FBX_NAME", "")

ADDON_ROOT = (r"C:\Users\yshky\OneDrive\Документы\My Games\ArmaReforgerWorkbench"
              r"\addons\Arm_Structura\Arm_Structura")

FAMILY = r"Assets\Structures\Houses\House_Individual\House_Individual_Brus"

BUILDING = os.path.join(ADDON_ROOT, FAMILY, MODULE)
BASE_NAME = FBX_NAME[:-4] if FBX_NAME.endswith(".fbx") else (FBX_NAME or MODULE)
FBX_PATH = os.path.join(BUILDING, BASE_NAME + ".fbx")
META_PATH = os.path.join(BUILDING, BASE_NAME + ".xob.meta")
DATA_DIR = os.path.join(BUILDING, "Data")
BACKUP_ROOT = r"C:\Users\yshky\OneDrive\Документы\ARMST_Backups\Arm_Structura"

# имена материалов
PORTAL_MAT = "PRT_195x72"                      # класс обязан быть MatLightPortal
DUMMY_NAME = "dummyvolume_D3975B51F51E6BD5"    # для BOXVOL и BSP
DUMMY_KEY = "dummyvolume"

# префикс аддона для RWTK-моста
ADDON_PREFIX = "$ARMSTPLATFORMStructura:"
