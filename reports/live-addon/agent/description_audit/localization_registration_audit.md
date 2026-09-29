# ARMST Localization Registration Audit

## Verified
- Live ARMST references: 59; unique keys: 59; runtime tables: 13; each 59 Ids / 59 Texts.

## Project config (`addon.gproj`)
- WidgetManagerSettings present: False
- StringTableDefinition present: False
- StringTableSource present: False
- LanguageDefinition present: False
- ARMST runtime files referenced: 0 / 13

## Resources
- valid runtime resources: 13 / 13
- duplicate GUIDs: 34
- missing metas: 0
- Language/localization.st exists: False

| locale | guid | header==meta | dup |
|---|---|---|---|
| cs_cz | 0AD4179A60AC8C65 | True | 1 |
| de_de | 155B8785B40320A5 | True | 1 |
| en_us | FD056F6A77D94BBD | True | 1 |
| es_es | A50D9D243F2214B2 | True | 1 |
| fr_fr | 00B2AA18FD609EAD | True | 1 |
| it_it | E9B0EFA7BD0DC122 | True | 1 |
| ja_jp | B4B3E630945BFFFB | True | 1 |
| ko_kr | F1A2533581AB710A | True | 1 |
| pl_pl | 0910A9463A6EA8B7 | True | 1 |
| pt_br | 3AB1CE9E74578E52 | True | 1 |
| ru_ru | 294CC9C152D6A424 | True | 1 |
| uk_ua | 937D00DDAA2B1EF4 | True | 1 |
| zh_cn | B62E0E6E79D5A688 | True | 1 |

## Working references
- `addons/data/ArmaReforger.gproj` (13 locales) and `addons/core/core.gproj` (1 locale).
- Enclosing: `GameProjectConfig PC > WidgetManagerSettings > StringTables`.
- `StringTableDefinition { StringTableSource "..localization.st" Languages { LanguageDefinition { Code .. StringTableRuntime ..conf } } }`.

## Load chain
CASE B: addon.gproj -> WidgetManagerSettings.StringTables -> StringTableDefinition -> StringTableSource(.st) + Languages/LanguageDefinition(Code + StringTableRuntime .conf)

## Root cause
ARMST addon.gproj contains no WidgetManagerSettings/StringTables/StringTableDefinition registration. The 13 runtime .conf resources are valid but unregistered, so their Ids never enter the project StringTable and #AR-ARMST_* lookups fail.

## Required `.st`
- LOCALIZATION_ST_RUNTIME_REQUIRED: YES (StringTableSource is part of the definition; no working local example lacks it).

## Smallest proven repair plan (not executed)
- 1. Create Language/localization.st (+ .meta) as the StringTableSource for the ARMST definition (source identity; required by StringTableDefinition).
- 2. In addon.gproj, under Configurations > GameProjectConfig PC, add WidgetManagerSettings WidgetManagerSettings "{NEW_GUID}" { StringTables { StringTableDefinition "{NEW_GUID}" { StringTableSource "{ST_GUID}Language/localization.st" Languages { LanguageDefinition "{NEW_GUID}" { Code "<loc>" StringTableRuntime "{CONF_GUID}Language/localization.<loc>.conf" } for all 13 locales } } } }.
- 3. Use each runtime conf .meta GUID exactly as the StringTableRuntime reference; locale codes exactly en_us, ru_ru, de_de, fr_fr, es_es, it_it, pl_pl, pt_br, cs_cz, ja_jp, ko_kr, zh_cn, uk_ua.
- 4. Do not duplicate the game StringTableDefinition; each addon registers its own.
- 5. Secondary cleanup (not the missing-string cause): remove/relocate the stray Language/localiztion.pl_pl.conf (malformed header) and the agent/ backup copies that produce ResourceDB duplicate-GUID warnings.
