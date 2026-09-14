from __future__ import annotations

from pathlib import Path
import sys
import unittest


TOOLS = Path(__file__).resolve().parents[1] / "tools" / "weapon_intelligence"
sys.path.insert(0, str(TOOLS))

from enfusion_text import parent_resource, parse_text  # noqa: E402
from scan import extract_weapon  # noqa: E402


VSS_SAMPLE = r'''GenericEntity : "{1FA22B1F5E7BC80B}Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et" {
 ID "CFBAA4B725411E45"
 components {
  SCR_MeleeWeaponProperties "{55349E9229B55E31}" {
   m_fDamage 2
  }
  SCR_WeaponAttachmentsStorageComponent "{51F080D5CE45A1A2}" {
   Attributes SCR_ItemAttributeCollection "{51F080D5C64F12C5}" {
    ItemDisplayName WeaponUIInfo "{5222CB07CFF6712A}" {
     Name "VSS Vintorez"
     Description "Special weapon"
    }
    ItemPhysAttributes ItemPhysicalAttributes "{55349E9229B55E3D}" {
     Weight 2.1
     SizeSetupStrategy Manual
     ItemDimensions 20 20 20
     ItemVolume 1000
    }
   }
  }
  WeaponComponent "{CFBAA4B706BA66E8}" {
   components {
    AttachmentSlotComponent "{5F189C826D592450}" {
     AttachmentSlot InventoryStorageSlot BayonetSlot {
      PivotID "slot_optics"
     }
     AttachmentType AttachmentOpticsDovetailAK "{60AAE435165C80B8}" {
     }
    }
    MuzzleComponent "{CA6BE4D6B867541F}" {
     FireModes {
      BaseFireMode "{B80A64F4A8EF8333}" {
       RoundsPerMinute 700
      }
      BaseFireMode "{619AB45C30091E43}" {
       RoundsPerMinute 700
      }
     }
     MagazineWell MagazineWell9x39 "{55349E9229B55D96}" {
     }
     BulletInitSpeedCoef 0.835
     DispersionDiameter 0.4
     DispersionRange 200
     WeaponAimModifiers {
      RecoilWeaponAimModifier "{55349E9229B55D9A}" {
       LinearData RecoilData "{58789524E765774D}" {
        "Curve Magnitudes" 1 0.9 0.9
       }
       AngularData RecoilData "{58789524E7CAB55F}" {
        "Curve Magnitudes" 1 0.9 1
       }
       TurnOffsetData RecoilData "{58789524E0951484}" {
        "Curve Magnitudes" 1 0.9 0
       }
      }
     }
     MagazineTemplate "{70D023F899C9C226}Prefabs/Weapons/Magazines/9x39/Magazine_9x39_20rnd_vss_SP5.et"
    }
   }
   UIInfo WeaponUIInfo "{CC3BA6A2C42F09F4}" {
    Name "VSS Vintorez"
    Description "Russian special weapon"
   }
  }
 }
}'''


class WeaponIntelligenceTests(unittest.TestCase):
    def test_vss_declared_values_are_extracted_without_guessing(self) -> None:
        document = parse_text(VSS_SAMPLE, "Rifle_VSS.et")
        self.assertEqual([], document.parse_warnings)

        parent = parent_resource(document)
        self.assertIsNotNone(parent)
        self.assertEqual("1FA22B1F5E7BC80B", parent["guid"])
        self.assertEqual(
            "Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et",
            parent["path"],
        )

        weapon = extract_weapon(document, "Prefabs/Weapons/Rifles/VSS/Rifle_VSS.et")
        self.assertEqual("VSS Vintorez", weapon["identity"]["name"])
        self.assertEqual(2.1, weapon["physical"]["weight"])
        self.assertEqual(1000, weapon["physical"]["volume"])
        self.assertEqual(2, weapon["melee"]["damage"])
        self.assertEqual(0.835, weapon["muzzle"]["bullet_init_speed_coef"])
        self.assertEqual(0.4, weapon["muzzle"]["dispersion_diameter"])
        self.assertEqual(200, weapon["muzzle"]["dispersion_range"])
        self.assertEqual("MagazineWell9x39", weapon["muzzle"]["magazine_well"])
        self.assertEqual(700, weapon["muzzle"]["fire_modes"][0]["rounds_per_minute"])
        self.assertIsNone(weapon["muzzle"]["fire_modes"][0]["max_burst"])
        self.assertEqual(
            "B80A64F4A8EF8333", weapon["muzzle"]["fire_modes"][0]["instance_guid"]
        )
        self.assertEqual(
            [1, 0.9, 0.9], weapon["recoil"]["LinearData"]["curve_magnitudes"]
        )
        self.assertEqual(
            "AttachmentOpticsDovetailAK", weapon["attachments"][0]["attachment_type"]
        )

    def test_missing_inherited_values_stay_unknown(self) -> None:
        document = parse_text(VSS_SAMPLE, "Rifle_VSS.et")
        weapon = extract_weapon(document, "Rifle_VSS.et")
        self.assertIsNone(weapon["muzzle"]["fire_modes"][0]["max_burst"])
        self.assertFalse(weapon["sights"]["zeroing_modifier_present_raw"])


if __name__ == "__main__":
    unittest.main()
