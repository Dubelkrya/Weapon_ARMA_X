# Weapon_ARMA_X

AI-friendly weapon intelligence catalog and local scanner for the ARMST Arma Reforger weapons addon.

The local addon is the source of truth. Repository data is derived analysis/export and must not silently invent missing engine values.

## Weapon Intelligence V1

The first scanner lives in:

```text
tools/weapon_intelligence/
```

It recursively reads `.et`, `.conf`, `.meta` and `.c` files, builds resource/reference and inheritance indexes, and exports normalized weapon/magazine/ammunition JSON without modifying the addon.

Run from this repository root:

```powershell
python tools/weapon_intelligence/scan.py `
  --root "C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons" `
  --out .
```

See `docs/WEAPON_INTELLIGENCE_V1.md` for the data model, safety boundary and current limitations.
