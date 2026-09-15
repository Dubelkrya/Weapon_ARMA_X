# CONFIG AUTHORING GUIDE

Sources of truth for this layer are the supplied config snapshots (`Configs.zip` plus the later supplemental `Configs(1).zip`) combined with the already indexed weapon/magazine sources. When the snapshots disagree or one adds a previously missing resource, preserve provenance and prefer the later supplied source for that specific resource instead of silently rewriting unrelated records.

## Resolution rules

1. Resolve the weapon and magazine inheritance chain first: **child local > nearest parent > shared base**.
2. A `MagazineConfig` / `AmmoResourceArray` describes **allowed ammunition**. It does not prove what a particular magazine is loaded with.
3. Resolve loaded contents from the magazine's `AmmoMapping`: each integer is an index into the config resource array.
4. For mixed magazines, preserve the exact mapping counts from the serialized array. Do not reconstruct a nominal `4Ball_1Tracer` ratio from the filename.
5. Keep the projectile's primary kinetic `ProjectileDamage` separate from additional effects such as incendiary damage on tracers.
6. Use the projectile's actually referenced `BallisticTableConfig`. The presence of a more specific-looking `AIBT_*` config is not permission to swap it in.
7. Compute weapon muzzle velocity only as `Projectile.InitSpeed × Weapon.BulletInitSpeedCoef` when both inputs are source-backed.
8. Unknown values remain unknown. A missing resource in one snapshot is not proof that it does not exist in a later supplied snapshot.
9. Keep source provenance explicit when a chain was resolved by a supplemental archive.

## Confirmed handgun examples

### PM
`Magazine_9x18_PM_8rnd_Ball.et` → `Ammo_9x18Mak.conf` → allowed set `Ammo_9x18_Ball_57N181.et` → mapping index 0 × 8 → loaded **57N181 × 8**.

In the supplied snapshot `Ammo_9x18_Ball_57N181.et` is a thin child of `Ammo_Bullet_Base.et`; effective inherited values include InitSpeed 750, Mass 0.01, Diameter 8 and primary kinetic DamageValue 50.

### M9
`Magazine_9x19_M9_15rnd_Ball.et` → `Ammo_9x19.conf` → allowed index 0 `M882`, index 1 `JHP` → mapping index 0 × 15 → loaded **M882 × 15**. JHP is allowed but is not loaded in the standard Ball magazine.

### RPK-74 45rnd 4Ball/1Tracer
Serialized mapping resolves to **7N6 × 32 + 7T3 × 13**. The tracer has an additional incendiary damage effect; do not replace its inherited primary kinetic damage with the small incendiary value.

### PKM 100rnd 4Ball/1Tracer
Serialized mapping resolves to **57N323S × 76 + 7T2 × 24**. Tracer effects are additive to the kinetic damage chain.

### TT-33 — resolved by the supplemental ARMST config snapshot
The older `Configs.zip` snapshot did not contain the 7.63×25 / 7.62×25 magazine config. That earlier absence is historical, not the current resolution state.

`Configs(1).zip` supplies:

- `Configs/Weapons/Ammo/Ammo_763x25.conf` (`9379B9A38F29D508`);
- allowed projectile `Prefabs/Weapons/Ammo/Ammo_763x25_Ball.et` (`5AE7AF31B9D7EB6C`).

The TT magazine resolves to **8 × `Ammo_763x25_Ball.et`** through its inherited PM-magazine structure.

Source-backed projectile values from the supplied snapshot:

- InitSpeed: 430
- InitSpeedVariation: 15
- Mass: 0.00804
- AirDrag: 0.0000125
- Diameter: 9.1
- Length: 15.5
- PenetrationDepth: 20
- PenetrationDensity: 0.65
- PenetrationSpeed: 355
- primary kinetic DamageValue: inherited 50 from `Ammo_Bullet_Base`
- BallisticTableConfig: `Configs/Weapons/AIBallisticTables/AIBT_9x19_Ball_M882.conf`

These are implementation/source facts. Do not silently replace unusual values with real-world Tokarev figures.

A separate legacy `Ammo_763x25.et` also exists in the supplied sources, but it is **not** the projectile selected by the resolved `Ammo_763x25.conf` chain. Do not use its values as the loaded TT round merely because the filename looks relevant.
