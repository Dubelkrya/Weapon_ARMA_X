# ARMST Localization Registration Fix

- localization.st: `Language/localization.st` GUID `69821F9E11916456`
- StringTableDefinition GUID: `8676871691CCCC71`
- definitions before/after: 0 -> 1
- source keys: 59 (sorted=True, unique=True)
- language definitions: 13
- runtime conf content changes: 0

## gproj registration
```
GameProjectConfig PC {
 WidgetManagerSettings WidgetManagerSettings "{AC4BE58770485E02}" {
  StringTables {
   StringTableDefinition "{8676871691CCCC71}" {
    StringTableSource "{69821F9E11916456}Language/localization.st"
    Languages { ... 13 LanguageDefinition ... }
   }
  }
 }
}
```

## Language mappings
| code | runtime guid | path |
|---|---|---|
| en_us | FD056F6A77D94BBD | Language/localization.en_us.conf |
| ru_ru | 294CC9C152D6A424 | Language/localization.ru_ru.conf |
| de_de | 155B8785B40320A5 | Language/localization.de_de.conf |
| fr_fr | 00B2AA18FD609EAD | Language/localization.fr_fr.conf |
| es_es | A50D9D243F2214B2 | Language/localization.es_es.conf |
| it_it | E9B0EFA7BD0DC122 | Language/localization.it_it.conf |
| pl_pl | 0910A9463A6EA8B7 | Language/localization.pl_pl.conf |
| pt_br | 3AB1CE9E74578E52 | Language/localization.pt_br.conf |
| cs_cz | 0AD4179A60AC8C65 | Language/localization.cs_cz.conf |
| ja_jp | B4B3E630945BFFFB | Language/localization.ja_jp.conf |
| ko_kr | F1A2533581AB710A | Language/localization.ko_kr.conf |
| zh_cn | B62E0E6E79D5A688 | Language/localization.zh_cn.conf |
| uk_ua | 937D00DDAA2B1EF4 | Language/localization.uk_ua.conf |

## Validation
```
{
 "LOCALIZATION_ST_EXISTS": true,
 "LOCALIZATION_ST_META_EXISTS": true,
 "ST_META_CLASS_OK": true,
 "LOCALIZATION_ST_GUID": "69821F9E11916456",
 "LOCALIZATION_ST_GUID_COLLISION": 0,
 "SOURCE_KEYS": 59,
 "SOURCE_UNIQUE": 59,
 "SOURCE_SORTED": true,
 "ARMST_STRINGTABLE_DEFINITIONS": 1,
 "LANGUAGE_DEFINITIONS": 13,
 "LOCALES": [
  "en_us",
  "ru_ru",
  "de_de",
  "fr_fr",
  "es_es",
  "it_it",
  "pl_pl",
  "pt_br",
  "cs_cz",
  "ja_jp",
  "ko_kr",
  "zh_cn",
  "uk_ua"
 ],
 "LANGUAGES_UNIQUE": true,
 "RUNTIME_REFS": 13,
 "RUNTIME_UNIQUE": true,
 "SOURCE_REF": [
  [
   "69821F9E11916456",
   "Language/localization.st"
  ]
 ],
 "SOURCE_MATCHES_META": true,
 "RUNTIME_CONF_CONTENT_CHANGES": [],
 "GAMEPLAY_FILES_CHANGED": 0,
 "TWELVE_GA_CHANGED": 0,
 "ST_ITEM_GUIDS_UNIQUE": true
}
```
