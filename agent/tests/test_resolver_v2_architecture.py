import os
import sys
import tempfile
import textwrap
import unittest

SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from architecture_index import build_architecture_package  # noqa: E402


def write(root, rel, content):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path) or root, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(textwrap.dedent(content).lstrip())
    return path


class ResolverV2ArchitectureTests(unittest.TestCase):
    def test_dependency_closure_emits_exact_missing_resource_request(self):
        with tempfile.TemporaryDirectory() as armst, tempfile.TemporaryDirectory() as vanilla:
            base = "Prefabs/Weapons/Rifles/Test/Base.et"
            child = "Prefabs/Weapons/Rifles/Test/ArmstChild.et"
            missing_conf = "Prefabs/Weapons/Core/Configs/FireModes/Missing.conf"

            write(
                vanilla,
                base,
                f'''\
                GenericEntity {{
                 components {{
                  WeaponComponent "{{1000}}" {{
                   components {{
                    MuzzleComponent "{{2001}}" {{
                     FireModes {{
                      BaseFireMode "{{C0DE}}" : "{{F001}}{missing_conf}" {{
                       RoundsPerMinute 600
                      }}
                     }}
                    }}
                   }}
                  }}
                 }}
                }}
                ''',
            )
            write(
                armst,
                child,
                f'''\
                GenericEntity : "{{B001}}{base}" {{
                 components {{
                  WeaponComponent "{{1000}}" {{
                   components {{
                    MuzzleComponent "{{2001}}" {{
                     DispersionRange 150
                    }}
                   }}
                  }}
                 }}
                }}
                ''',
            )

            package = build_architecture_package(
                armst,
                [f"materialized_base={vanilla}"],
            )

            self.assertEqual(package["summary"]["armst_blueprint_count"], 1)
            requests = package["export_requests"]
            self.assertEqual(len(requests), 1)
            self.assertEqual(requests[0]["guid"], "F001")
            self.assertEqual(requests[0]["path"], missing_conf)
            self.assertEqual(requests[0]["requested_extension"], ".conf")

            blueprint = package["blueprints"][0]
            self.assertEqual(blueprint["resource"], child)
            self.assertEqual(blueprint["resolution"]["chain"][1]["origin"], "materialized_base")
            local_ids = {row["instance_id"] for row in blueprint["local_instances"]}
            self.assertIn("{1000}", local_ids)
            self.assertIn("{2001}", local_ids)

            edges = package["graph"]["closure"]["missing_edges"]
            self.assertEqual(len(edges), 1)
            self.assertEqual(edges[0]["source"]["resource"], base)
            self.assertEqual(edges[0]["source"]["origin"], "materialized_base")

    def test_ambiguous_collision_is_identity_gap_not_export_request(self):
        with tempfile.TemporaryDirectory() as armst, tempfile.TemporaryDirectory() as vanilla:
            collided = "Prefabs/Weapons/Rifles/Test/Collision.et"
            child = "Prefabs/Weapons/Rifles/Test/Child.et"
            write(armst, collided, "GenericEntity {\n Value 100\n}\n")
            write(vanilla, collided, "GenericEntity {\n Value 50\n}\n")
            write(
                armst,
                child,
                f'''\
                GenericEntity : "{{A111}}{collided}" {{
                }}
                ''',
            )

            package = build_architecture_package(
                armst,
                [f"materialized_base={vanilla}"],
            )

            self.assertGreater(
                package["summary"]["ambiguous_identity_edge_count"],
                0,
            )
            self.assertEqual(package["export_requests"], [])
            ambiguous = package["graph"]["closure"]["ambiguous_identity_edges"]
            self.assertEqual(
                ambiguous[0]["resolution"]["reason"],
                "path_collision_without_proven_guid_owner",
            )


if __name__ == "__main__":
    unittest.main()
