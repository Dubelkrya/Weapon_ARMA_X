# CONFIG AUTHORING GUIDE

Source of truth for this layer: `Configs.zip`, combined with the already indexed `Weapons.zip`.

## Resolution rules

1. Resolve the weapon and magazine inheritance chain first: **child local > nearest parent > shared base**.
2. A `MagazineConfig` / `AmmoResourceArray` describes **allowed ammunition**. It does not prove what a particular magazine is loaded with.
3. Resolve loaded contents from the magazine's `AmmoMapping`: each integer is an index into the config resource array.
4. For mixed magazines, preserve the exact mapping counts from the serialized array. Do not reconstruct a nominal `4Ball_1Tracer` ratio from the filename.
5. Keep the projectile's primary kinetic `ProjectileDamage` separate from additional effects such as incendiary damage on tracers.
6. Use the projectile's actually referenced `BallisticTableConfig`. The presence of a more specific-looking `AIBT_*` config is not permission to swap it in.
7. Compute weapon muzzle velocity only as `Projectile.InitSpeed × Weapon.BulletInitSpeedCoef` when both inputs are source-backed.
8. `Configs.zip` has no 7.63×25/7.62×25 magazine config. TT-33 ammo remains an ARMST-local chain until its raw config/projectile sources are supplied.

## Confirmed handgun examples

### PM
`Magazine_9x18_PM_8rnd_Ball.et` → `Ammo_9x18Mak.conf` → allowed set `Ammo_9x18_Ball_57N181.et` → mapping index 0 × 8 → loaded **57N181 × 8**.

In this supplied snapshot `Ammo_9x18_Ball_57N181.et` is a thin child of `Ammo_Bullet_Base.et`; effective inherited values are InitSpeed 750, Mass 0.01, Diameter 8 and primary kinetic DamageValue 50.

### M9
`Magazine_9x19_M9_15rnd_Ball.et` → `Ammo_9x19.conf` → allowed index 0 `M882`, index 1 `JHP` → mapping index 0 × 15 → loaded **M882 × 15**. JHP is allowed but is not loaded in the standard Ball magazine.

### RPK-74 45rnd 4Ball/1Tracer
Serialized mapping resolves to **7N6 × 32 + 7T3 × 13**. The tracer has an additional incendiary damage effect; do not replace its inherited primary kinetic damage with the small incendiary value.

### PKM 100rnd 4Ball/1Tracer
Serialized mapping resolves to **57N323S × 76 + 7T2 × 24**. Tracer effects are additive to the kinetic damage chain.

### TT-33 exception
The weapon/magazine side is known from ARMST, but vanilla `Configs.zip` contains no 7.63×25 config. Do not substitute another caliber. `Ammo_763x25.conf` remains local/unresolved until the ARMST raw config/projectile source is supplied.
