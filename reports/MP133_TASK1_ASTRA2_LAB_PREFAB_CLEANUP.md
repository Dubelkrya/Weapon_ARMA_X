# MP-133 Task #1 — ASTRA2 lab cleanup (canonical prefab + obsolete prefab removal)

Статус: **ASTRA2_LAB_CLEANUP_OWNER_WB_VERIFY_PENDING**
Дата: 2026-10-05
Задание: Issue #34 [#6000357139](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6000357139), разрешение на применение — [#6000377139](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34) (W3 удалить, `old_pa/` оставить, GroupSelect не чинить).
Режим: **применено в live при закрытом Workbench**. Branch `t4b/installed-mag-probe`.

---

## 0. Что применено (live)

1. Канонический `Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et` переподключён со старого набора `MP133_Astra.*` на **ASTRA2** (`MP133_Astra2.agr` / `MP133_Astra2_weapon.asi` / `MP133_Astra2_player.asi`).
2. Удалены 8 исторических prefab'ов + их `.et.meta` из live и из labs-зеркала.
3. `Prefabs/Test/` теперь содержит ровно два prefab'а: канонический test weapon и `ARMST_T4B_G3B2_Tube3Mag.et`.
4. `old_pa/` и прочие ASTRA authoring-ресурсы — **не тронуты**.
5. Шесть `Missing Group Select` — **не тронуты** (предсуществующие, есть и в ORIGINAL).

Workbench на момент применения — закрыт (`Workbench/Reforger/Arma/Enfusion` = NONE).

---

## 1. Инвентарь `Prefabs/Test/` (до → после)

**Было (10 prefab'ов):** canonical, Tube3Mag + 8 исторических.
**Стало (2 prefab'а):**

| Prefab | GUID | Назначение |
|---|---|---|
| `ARMST_T4B_AstraRebuild_TestWeapon.et` | `{B9E884F7E642E292}` | **канонический** lab MP-133 (→ ASTRA2) |
| `ARMST_T4B_G3B2_Tube3Mag.et` | `{CD8091A2B3C4D5E6}` | фиксированная труба (dependency канонического) |

**Удалено (8 prefab'ов + 8 `.et.meta`; хэши SHA-256 live на момент удаления):**

| Prefab | GUID | `.et` SHA-256 | `.et.meta` SHA-256 |
|---|---|---|---|
| `ARMST_T4B_AstraV2_Bridge_TestWeapon.et` | `{29AAFC302B134E27}` | `BFA0C3E0FC2A32880A5559FCD9D6C3F4A0ABEBBD27E2BC52EF1770CC1FCE3926` | `6B751E340CB64AAB85DEEBB37A06C22BE35E87B95FAC8135B0742A0044DBD40F` |
| `ARMST_T4B_G3B1_DonorDevice.et` | `{1A2B3C4D5E6F7081}` | `12B073DD60318491752888DED79CD3807E8B25AFB171694CB796054C86CB8502` | `AAE07E095434B9078508EAA81EB7E52F2E535434052D32C10616F8016D8F3F9F` |
| `ARMST_T4B_G3B1_DonorMag.et` | `{C4D5E6F708192A3B}` | `437D75E3545400A31663F78DBD08E7898BEDE69BA758FC76935ABAA8D1FE0761` | `A1DB893F790DB72E73789F3C33BE334004F3E8325B4C9C6952A2D9E767FF02CF` |
| `ARMST_T4B_G3B2_InventoryWide_TestWeapon.et` | `{233445566778899A}` | `64C5DD56A8DBBA04D191D8D2D57DFCD9F32918039CCC67DE606051C30A1B602A` | `D972C7FAF774C86B85BACF960F29F2CBF94C427337A9516CDF94564B9B59D364` |
| `ARMST_T4B_G3B2_InventoryWide_WriteOn_TestWeapon.et` | `{78899AABBCDDEEFF}` | `7DB287F6F5B801500C796F1A46E4A3BB48FAF7F0F020EEF67AC7C22705439FDF` | `6972BC1FEC5BED6FC03E5F8559815F8602A156BEBFDBC1326EC92FC856EF6018` |
| `ARMST_T4B_G4A_OptionB_TestWeapon.et` | `{33918685A521E45A}` | `DC3087577E30FABB035E701E7C2BE03D940BDAE79D3BD2028E1A494AE59EF41C` | `3FBA7B5EC72FD4EC295392F9C543E2FB0C2400D9CAD1FDA0AAE5C2CBCC119511` |
| `ARMST_T4B_TestWeapon.et` | `{C2D3E4F506172839}` | `29C70A78B7CBA7678B84A57A29EBF32127A1ED2575742270D9CFACAB78F2AE83` | `8EBCBED43046664A0A0669C2D8B03616B690422BC4A0F7E778B3972F7FF6733E` |
| `ARMST_T4B_W3_CopiedWorkspace_TestWeapon.et` | `{E3693DABB8153C27}` | `B76B2783998D24B1216F70C517F4163E757FF17AF126756ACF1A1703008CBAD0` | `9DB933F4AB1F9297626AF64A8116EA125BDCCF9BDE00D5EDB5F4DCD8BA09D7BD` |

**Reference audit (read-only, вся папка addons):** ни один кандидат не был referenced другим prefab/script/config; только собственный `.meta`, генерируемый `resourceDatabase.rdb` и **комментарий** в `ARMST_T4B_InstalledMagProbe.c`. Placements в `.layer`/`.ent` — нет. После удаления повторная проверка dangling-ссылок (см. §6) → **NONE**.

---

## 2. Канонический prefab — old → ASTRA2

`ARMST_T4B_AstraRebuild_TestWeapon.et` (`{B9E884F7E642E292}`), старый `.et` hash `22A27E73BDE2B5C72C37D4B004BC1C1D05660FE243996AE9C97B3DC3E0AACAAB`.

| Поле | Было (old) | Стало (ASTRA2) |
|---|---|---|
| `AnimGraph` | `{7E087CCCBFB67045}…/MP133_Astra.agr` | `{AF2491EDB3449EED}…/MP133_Astra2.agr` |
| weapon `AnimInstance` | `{4CF7F797EC1FCA0E}…/MP133_Astra_weapon.asi` | `{5F61684997C53048}…/MP133_Astra2_weapon.asi` |
| injection `AnimGraph` | `{7E087CCCBFB67045}…/MP133_Astra.agr` | `{AF2491EDB3449EED}…/MP133_Astra2.agr` |
| player `AnimInstance` | `{B7A966A6741EAEE2}…/MP133_Astra_player.asi` | `{A43FF9780FC454A4}…/MP133_Astra2_player.asi` |

GUID'ы сверены с фактическими `.meta` ASTRA2. Сохранено: `ARMST_T4B_WeaponProbe "A5DD348953C44200"` + `m_iT4BStartAmmo 2`, `MuzzleComponent "{CA6BE4D6B867541F}"` + `MagazineTemplate {CD8091A2B3C4D5E6}…/ARMST_T4B_G3B2_Tube3Mag.et`, класс `ARMST_T4B_AstraV2_WeaponAnimationComponent`, `BindingName "Weapon"`, `BindWithInjection 1`, `ID "1D80E36020934900"`, наследование/модель. Канонический `.et.meta` не изменялся (`636DC0BAD9FCF52A1BD135FC01759AC31A95BB1538289BCF4F586A4EF0AAC37F`).

---

## 3. W3 — зафиксированное live-состояние перед удалением

Live `ARMST_T4B_W3_CopiedWorkspace_TestWeapon.et` (hash `B76B2783998D24B1216F70C517F4163E757FF17AF126756ACF1A1703008CBAD0`) на момент удаления:

```
GenericEntity : "{63FF6FDCA4E7E735}Prefabs/Weapons/Russian/Shotgun/armst_Shotgun_mp_133.et" {
 ID "A4B5C6D7E8F90112"
 components {
  ARMST_T4B_WeaponProbe B5C6D7E8F9011223 {
   m_iT4BStartAmmo 2
  }
  WeaponComponent "{CFBAA4B706BA66E8}" {
   components {
    MuzzleComponent "{CA6BE4D6B867541F}" {
     MagazineTemplate "{CD8091A2B3C4D5E6}Prefabs/Test/ARMST_T4B_G3B2_Tube3Mag.et"
    }
    ARMST_T4B_WeaponAnimationComponent "{60B4EA76EB15F6E0}" {
     AnimGraph "{9A5A46E2D8F8586F}Assets/MP133_AstraShellGraph/MP133_Astra.agr"
     AnimInstance "{AE8E3367177C57BD}Assets/MP133_AstraShellGraph/MP133_Astra_weapon.asi"
     AnimInjection AnimationAttachmentInfo "{532F3A9CB912F2BA}" {
      AnimGraph "{9A5A46E2D8F8586F}Assets/MP133_AstraShellGraph/MP133_Astra.agr"
      AnimInstance "{2629533DCE9A5811}Assets/MP133_AstraShellGraph/MP133_Astra_player.asi"
     }
    }
   }
  }
  ActionsManagerComponent "{A29AE67FF4D82B0F}" {
   additionalActions {
    ARMST_T4B_G3B2_TransferAction C6D7E8F901122334 {
     ParentContextList {
      "default"
     }
     UIInfo UIInfo F3A4B5C6D7E8F901 {
      Name "W3: transfer 1 (copied workspace; INVENTORY-WIDE WRITE ENABLED)"
     }
     m_bG3B2WriteEnabled 1
     m_bG3B2InventoryWide 1
    }
   }
  }
 }
 coords 148.268 1.9 77.971
}
```

Примечание: committed labs-зеркало содержало **другую** (Workbench-authored, unquoted) версию W3, указывающую на `Assets/Weapons_RUS/Mp_133/Workspace/Lab_MP133.*` (коммит `c416c1e`). Т.е. live и labs расходились ещё до этого задания; обе версии — исторические, обе удалены по разрешению владельца.

---

## 4. ASTRA resources (`Assets/MP133_AstraShellGraph_test/`)

- **Текущий ASTRA2** (`astra2.aw`, `MP133_Astra2.{agf,agr,ast}`, `MP133_Astra2_{player,weapon}.asi` + меты) — KEEP, не изменялся.
- **`old_pa/`** (`MP133_Astra.{agf,agr,ast}`, `MP133_AstraShellGraph_test.aw`, `MP133_Astra_{player,weapon}.asi` + меты) — **оставлен** по указанию владельца. После repoint больше не referenced каноническим prefab.

---

## 5. Ошибки/предупреждения ASTRA2 lab

Шесть `Missing Group Select`: `SafetyPose`, `SemiPose`, `AutoPose`, `SightPose`, `IdleFinger`, `BoltClosed` (`Source "Reload.Safety/Sight/Idle_finger/BoltPose"`).

**Аудит:** те же Pose-ноды с теми же `Source` присутствуют в **ORIGINAL** known-good AGF. → **предсуществующие**, не вызваны cleanup'ом; по решению владельца **не чинятся**. Помечено `PRE_EXISTING_LEGACY_WARNINGS`.

---

## 6. Верификация после применения

| Проверка | Ожидание | Факт |
|---|---|---|
| canonical == staged | True | **True** |
| old `MP133_Astra.` refs в canonical | 0 | **0** |
| ASTRA2 refs в canonical | 4 | **4** |
| `ARMST_T4B_G3B2_Tube3Mag.et` hash | `A4CA7943…BE80` | **без изменений** |
| `ARMST_T4B_G3B2_Tube3Mag.et.meta` hash | `64270F35…1F57` | **без изменений** |
| V2 probe hash | `C9D49A1B…EA6` | **без изменений** |
| ASTRA2 player/weapon ASI — 10 ANM (5 P + 5 W) | 10 | **10** (по 1 каждой) |
| 10 imported ANM GUID | без изменений | **без изменений** (count 10) |
| 9 legacy AGF-нод в ASTRA2 | 0 | **0** |
| dangling refs на 8 удалённых prefab'ов (gameplay-файлы, кроме rdb) | NONE | **NONE** |
| `Prefabs/Test/` | 2 prefab'а | **2** |

`resourceDatabase.rdb` не изменялся (генерируемая БД; пересоберётся Workbench).

---

## 7. Git

Узкий commit: labs-зеркало (canonical modified + 8 удалений) + этот отчёт. Граф/ASI/AGR/AST/AW/ANM/meta/G3B2/production/Core не тронуты. Live addon — не git-репозиторий; изменения отражены в `labs/`.

---

## 8. Статус

**`ASTRA2_LAB_CLEANUP_OWNER_WB_VERIFY_PENDING`** — применено при закрытом Workbench. Ожидается проверка владельца в Workbench: открыть лабу, убедиться, что `Prefabs/Test/` содержит только два prefab'а, канонический test weapon ссылается на ASTRA2, ошибки ASTRA2 отсутствуют (кроме шести предсуществующих GroupSelect-warning'ов). `old_pa/` намеренно оставлен.
