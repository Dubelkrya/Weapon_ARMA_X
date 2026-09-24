"""
scan_build.py
=============
Primary analysis pipeline for the ARMST-PLATFORM---Weapons addon.

Reads every `.et` / `.conf` / `.meta` / `.c` text resource under the addon
root, builds an entity inventory, resolves local inheritance chains, merges
parameters with provenance, computes derived values, resolves the
weapon -> magazine -> ammo reference graph, and exports:

  catalog/   - one JSON per entity (weapons, magazines, ammunition, optics,
               attachments, grenades, misc)
  indexes/   - aggregated JSON indexes
  reports/   - scan_summary.md, unresolved_references.md,
               inheritance_issues.md, anomalies.md
  schema/    - JSON schemas describing the exported entities
  agent/     - scan_state.json

Rules honoured:
  * local mod is the source of truth
  * never invent values that cannot be reached through the local file chain
  * every resolved value keeps provenance (defined_in / inherited)
  * unresolved/external parents are reported, never guessed

Usage:
  python agent/scripts/scan_build.py
Environment:
  MOD_ROOT  - path to the addon (default: workbench addons dir)
  REPO_ROOT - path to this repository (default: two dirs up from this file)
"""

import os
import re
import json
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from et_parser import (parse_file, find_child, find_children, find_recursive,
                       GUID_REF_RE, Node)

# ----------------------------------------------------------------------------
# environment / paths
# ----------------------------------------------------------------------------

DEFAULT_MOD_ROOT = (r"C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench"
                    r"\addons\ARMST-PLATFORM---Weapons")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

MOD_ROOT = os.path.abspath(os.environ.get("MOD_ROOT", DEFAULT_MOD_ROOT))
REPO_ROOT = os.path.abspath(os.environ.get("REPO_ROOT", DEFAULT_REPO_ROOT))

CATALOG_DIR = os.path.join(REPO_ROOT, "catalog")
INDEX_DIR = os.path.join(REPO_ROOT, "indexes")
REPORT_DIR = os.path.join(REPO_ROOT, "reports")
SCHEMA_DIR = os.path.join(REPO_ROOT, "schema")
AGENT_DIR = os.path.join(REPO_ROOT, "agent")

W = []  # warnings / anomalies collected during scan


def warn(cat, msg):
    W.append({"category": cat, "message": msg})


# ----------------------------------------------------------------------------
# merged node with provenance
# ----------------------------------------------------------------------------


class MNode:
    """Merged node: same shape as et_parser.Node plus .src provenance."""

    __slots__ = ("name", "type", "id", "value", "children", "append",
                 "line", "ref", "src")

    def __init__(self, name, typ=None, nid=None, value=None, children=None,
                 append=False, line=0, src=None):
        self.name = name
        self.type = typ
        self.id = nid
        self.value = value if value is not None else []
        self.children = children if children is not None else []
        self.append = append
        self.line = line
        self.ref = ref_of(name, typ, nid, value)
        self.src = src

    def to_dict(self):
        d = {"name": self.name}
        if self.type is not None:
            d["type"] = self.type
        if self.id is not None:
            d["id"] = self.id
        if self.value:
            d["value"] = self.value
        if self.ref is not None:
            d["ref"] = self.ref
        if self.append:
            d["append"] = True
        if self.src:
            d["src"] = self.src
        if self.children:
            d["children"] = [c.to_dict() for c in self.children]
        return d

    def __repr__(self):
        return f"<MNode {self.name} id={self.id} v={self.value} n={len(self.children)} src={self.src}>"


def ref_of(name, typ, nid, value):
    """Re-derive resource reference from a Node's identity/value tokens."""
    for t in ([nid, typ] if nid is not None else [typ] if typ else []) + \
             [str(v) for v in (value or [])]:
        if not t:
            continue
        m = GUID_REF_RE.match(str(t))
        if m:
            return {"guid": m.group(1).upper(), "path": m.group(2),
                    "raw": str(t)}
    return None


def mnode_from_parsed(pn, src):
    """Convert an et_parser.Node (and whole subtree) into an MNode tree."""
    n = MNode(pn.name, pn.type, pn.id, list(pn.value), [], pn.append,
              pn.line, src)
    n.ref = pn.ref
    n.children = [mnode_from_parsed(c, src) for c in pn.children]
    return n


# --------------------------------------------------------------------- merge

def _is_scalar_block(node):
    return bool(node.children) and all(c.name == "__elem__" for c in node.children)


def merge_scopes(parent_nodes, child_nodes):
    """
    Merge child scope over parent scope (both lists of MNode at the same
    block level). Fields/instances are matched by (name, id) when present,
    otherwise by name+position. Provenance follows the winning node.
    """
    if not parent_nodes:
        return child_nodes

    def key(n, idx):
        if n.id is not None:
            return (n.name, "id", n.id)
        return (n.name, "idx", idx)

    parent_map = OrderedDict((key(p, i), p) for i, p in enumerate(parent_nodes))
    child_map = OrderedDict((key(c, i), c) for i, c in enumerate(child_nodes))

    child_keys = set(child_map)
    out = []
    for k, ch in child_map.items():
        pa = parent_map.get(k)
        if pa is None:
            out.append(ch)
        else:
            out.append(merge_pair(pa, ch))
    for k, pa in parent_map.items():
        if k not in child_keys:
            out.append(pa)
    return out


def merge_pair(parent, child):
    """Merge a child node over the matching parent node."""
    is_arr = (_is_scalar_block(parent) and parent.children) or \
             (_is_scalar_block(child) and child.children)
    if is_arr:
        if child.append and _is_scalar_block(parent):
            vals = list(parent.value) + list(child.value)
            kids = list(parent.children) + list(child.children)
        else:
            vals = list(child.value) if child.value else list(parent.value)
            kids = list(child.children) if child.children else list(parent.children)
        merged = MNode(child.name, child.type if child.type else parent.type,
                       child.id if child.id is not None else parent.id,
                       vals, kids, child.append, child.line,
                       child.src if child.value or child.children else parent.src)
        return merged

    merged = MNode(child.name, child.type if child.type else parent.type,
                   child.id if child.id is not None else parent.id,
                   list(child.value) if child.value else list(parent.value),
                   merge_scopes(parent.children, child.children),
                   child.append, child.line,
                   child.src if child.value else parent.src)
    merged.ref = child.ref if child.ref is not None else parent.ref
    return merged


def chain_merge(rels, resources_by_rel):
    """
    Merge an inheritance chain (list of relpaths, leaf-first, all local) into
    one resolved MNode tree.
    """
    trees = [mnode_from_parsed(resources_by_rel[r].root, r) for r in rels]
    acc = trees[-1]
    for t in reversed(trees[:-1]):
        acc = merge_pair(acc, t)
    return acc


# ----------------------------------------------------------------------------
# inventory helpers
# ----------------------------------------------------------------------------


def index_all_files(root):
    files = {}
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip non-game workspace folders inside the primary addon: agent audit
        # artifacts / historical backups and the git metadata directory must
        # not be treated as live source resources.
        dirnames[:] = [d for d in dirnames
                       if d not in ("agent", ".git", "__pycache__")]
        for fn in filenames:
            abspath = os.path.join(dirpath, fn)
            rel = os.path.relpath(abspath, root).replace("\\", "/")
            files[rel] = abspath
    return files


def parse_text_resources(all_files, rels):
    """Parse the text resources we care about (.et/.conf/.meta/.c)."""
    resources = {}
    for rel in rels:
        ext = os.path.splitext(rel)[1].lower()
        if ext not in (".et", ".conf", ".meta", ".c"):
            continue
        try:
            resources[rel] = parse_file(all_files[rel], MOD_ROOT)
        except Exception as exc:  # noqa: BLE001
            warn("PARSE", f"{rel}: {exc}")
    return resources


def build_guid_index(resources):
    guid_map = {}     # guid -> actual relpath of the resource
    aliases = {}      # guid -> relpath declared by a meta file's Name field
    by_actual = {}    # relpath -> guid (from that file's own meta)
    for r in resources.values():
        if r.kind != "meta":
            continue
        name_nodes = find_recursive(r.root, "Name")
        name_node = name_nodes[0] if name_nodes else None
        if name_node is None or not name_node.value:
            continue
        val = str(name_node.value[0])
        m = GUID_REF_RE.match(val)
        if not m:
            continue
        guid = m.group(1).upper()
        aliases.setdefault(guid, r.relpath)
        target = re.sub(r"\.meta$", "", r.relpath)
        guid_map.setdefault(guid, target)
        by_actual.setdefault(target, guid)
    return guid_map, aliases, by_actual


def lookup_file(relpath, all_files):
    if not relpath:
        return None
    rel = relpath.replace("\\", "/")
    if rel in all_files:
        return rel
    low = rel.lower()
    for k in all_files:
        if k.lower() == low:
            return k
    return None


def resolve_ref(guid, path, all_files, guid_index):
    rel = lookup_file(path, all_files)
    if rel:
        return {"status": "local", "rel": rel, "guid": guid, "path": path}
    if guid and guid in guid_index:
        return {"status": "local", "rel": guid_index[guid], "guid": guid,
                "path": path, "resolved_by": "guid"}
    return {"status": "external", "guid": guid, "path": path}


def collect_refs(node):
    """Return all resource references found in a node subtree, with source."""
    refs = []
    for c in node.children:
        if c.ref is not None:
            refs.append({"guid": c.ref["guid"], "path": c.ref["path"],
                         "raw": c.ref["raw"], "defined_in": c.src})
        refs.extend(collect_refs(c))
    return refs


def build_chain(resource, resources_by_rel, all_files, guid_index, depth=64):
    chain = []
    external = []
    seen = set()
    cur = resource.relpath
    while cur and depth:
        depth -= 1
        rs = resources_by_rel.get(cur)
        if rs is None:
            chain.append({"rel": cur, "kind": "file", "status": "file"})
            break
        chain.append({"rel": cur, "kind": rs.kind, "status": "local",
                      "class": rs.et_class})
        if cur in seen:
            warn("INHERIT-LOOP", f"cycle detected at {cur}")
            chain.append({"rel": cur, "status": "loop"})
            break
        seen.add(cur)
        parent = rs.parent
        if not parent:
            break
        resolved = resolve_ref(parent["guid"], parent["path"], all_files,
                               guid_index)
        if resolved["status"] == "local":
            cur = resolved["rel"]
            continue
        external.append({"guid": parent["guid"], "path": parent["path"],
                         "raw": parent["raw"]})
        break
    return chain, external


# ----------------------------------------------------------------------------
# classification
# ----------------------------------------------------------------------------


def has_comp(resolved, name):
    if resolved is None:
        return False
    return bool(find_recursive(resolved, name))


def comps_children(resolved):
    """Return component instances of the resolved entity (empty if none)."""
    if resolved is None:
        return []
    c = find_child(resolved, "components")
    return list(c.children) if c is not None else []


def classify(resource, resolved):
    cats = OrderedDict()
    rel = resource.relpath.lower()
    has_w = has_comp(resolved, "WeaponComponent")
    has_m = has_comp(resolved, "MagazineComponent")

    if resource.et_class == "Projectile":
        cats["kind"] = "ammunition"
        cats["confidence"] = "class"
    elif has_w:
        cats["kind"] = "weapon"
        cats["confidence"] = "components"
    elif has_m:
        cats["kind"] = "magazine"
        cats["confidence"] = "components"
    elif "/grenades/" in rel:
        cats["kind"] = "grenade"
        cats["confidence"] = "folder"
    elif "/tripods/" in rel:
        cats["kind"] = "tripod"
        cats["confidence"] = "folder"
    elif "/attachments/" in rel:
        cats["kind"] = "attachment"
        cats["confidence"] = "folder"
    elif "/handguns/" in rel or "/machineguns/" in rel or "/rifles/" in rel \
            or "Assets/Toz/" in rel:
        cats["kind"] = "weapon"
        cats["confidence"] = "folder"
    elif "/magazines/" in rel:
        cats["kind"] = "magazine"
        cats["confidence"] = "folder"
    elif "/ammo/" in rel:
        cats["kind"] = "ammunition"
        cats["confidence"] = "folder"
    elif "/particles/" in rel:
        cats["kind"] = "particle"
        cats["confidence"] = "folder"
    elif "/core/" in rel:
        cats["kind"] = "core"
        cats["confidence"] = "folder"
    else:
        cats["kind"] = "misc"
        cats["confidence"] = "unknown"

    if "/attachments/" in rel:
        if "/optics/" in rel:
            cats["attachment_kind"] = "optic"
        elif "/muzzle/" in rel:
            cats["attachment_kind"] = "muzzle"
        elif "/underbarrel/" in rel:
            cats["attachment_kind"] = "underbarrel"
        elif "/stocks/" in rel or "/handguards/" in rel:
            cats["attachment_kind"] = "stock"
        else:
            cats["attachment_kind"] = "other"
    return cats


def parent_is_local(resource, resources_by_rel):
    p = resource.parent
    if not p:
        return False
    return bool(lookup_file(p["path"], resources_by_rel)) or \
        p["guid"] in resources_by_rel


# ----------------------------------------------------------------------------
# extraction helpers
# ----------------------------------------------------------------------------


def mfind(node, name):
    return find_child(node, name)


def mfind_rec(node, name):
    return find_recursive(node, name)


def scalar(node):
    if node is None:
        return None
    return node.value[0] if node.value else None


def vec(node):
    return list(node.value)


def first_node(nodes):
    return nodes[0] if nodes else None


def pval(node):
    """Provenance wrapper for a scalar node: {value, src}."""
    if node is None:
        return None
    return {"value": scalar(node),
            "defined_in": node.src,
            "inherited": bool(node.src and node.src != TOP_REL)}


def pvec(node):
    if node is None:
        return None
    return {"value": list(node.value),
            "defined_in": node.src,
            "inherited": bool(node.src and node.src != TOP_REL)}


def pref(node):
    if node is None or node.ref is None:
        return None
    return {"guid": node.ref["guid"], "path": node.ref["path"],
            "defined_in": node.src}


TOP_REL = None  # set per-entity during export


# ----------------------------------------------------------------------------
# per-kind extraction
# ----------------------------------------------------------------------------

def weapon_block(resolved):
    """Return the first WeaponComponent node in the resolved tree."""
    comps = find_child(resolved, "components")
    for c in (comps.children if comps else []):
        if c.name == "WeaponComponent":
            return c
    return None


def get_nested_components(weapon):
    """Return the `components` block list of the WeaponComponent."""
    inner = find_child(weapon, "components")
    return inner.children if inner else []


def weapon_extract(resolved, context):
    """
    Extract all structured balance-relevant params of a weapon prefab with
    provenance, as documented in the repo README / schemas.
    """
    global TOP_REL
    TOP_REL = context["rel"]
    w = weapon_block(resolved)
    if w is None:
        return {"error": "no WeaponComponent found"}

    inner = get_nested_components(w)
    muzzle = next((c for c in inner if c.name == "MuzzleComponent"), None)
    sights = next((c for c in inner if c.name == "SightsComponent"), None)
    anim = next((c for c in inner if c.name == "WeaponAnimationComponent"), None)

    def field_in_weapon(name):
        # prefer muzzle-carried values (ARMST pattern), then any inner comp
        for source in (muzzle, w):
            if source is None:
                continue
            n = find_child(source, name)
            if n is not None:
                return n
        return None

    # ---- fire modes
    fire_nodes = []
    fm = find_child(muzzle, "FireModes") if muzzle else None
    if fm is None:
        fm = find_child(w, "FireModes")
    if fm:
        for b in fm.children:
            if b.name != "BaseFireMode":
                continue
            fire_nodes.append({
                "mode_id": b.id,
                "ui_name": scalar(find_child(b, "UIName")),
                "rounds_per_minute": pval(find_child(b, "RoundsPerMinute")),
                "max_burst": pval(find_child(b, "MaxBurst")),
                "defined_in": b.src,
            })

    # ---- magazine well / template
    mw = find_child(muzzle, "MagazineWell") if muzzle else None
    if mw is None:
        mw = find_child(w, "MagazineWell")

    mag_template = None
    mt = find_child(muzzle, "MagazineTemplate") if muzzle else None
    if mt is None or mt.ref is None:
        mt = find_child(w, "MagazineTemplate")
    if mt is not None and mt.ref is not None:
        mag_template = {"guid": mt.ref["guid"], "path": mt.ref["path"],
                        "defined_in": mt.src}

    # ---- aim mods
    recoil = None
    sway = None
    aim_mods = field_in_weapon("WeaponAimModifiers")
    if aim_mods is not None:
        for am in aim_mods.children:
            if am.name == "RecoilWeaponAimModifier":
                recoil = _recoil_extract(am)
            elif am.name == "SwayWeaponAimModifier":
                sway = _sway_extract(am)

    # ---- name
    name = None
    ui = find_child(w, "UIInfo")
    if ui:
        name_ui = find_child(ui, "WeaponUIInfo")
        if name_ui:
            nn = find_child(name_ui, "Name")
            if nn is not None and nn.value:
                name = (scalar(nn), nn.src)
    if name is None:
        storage = next((c for c in comps_children(resolved)
                        if c.name == "SCR_WeaponAttachmentsStorageComponent"),
                       None)
        if storage:
            attrs = find_child(storage, "Attributes")
            itm = find_child(attrs, "ItemDisplayName")
            if itm:
                ui2 = find_child(itm, "WeaponUIInfo")
                if ui2:
                    nn = find_child(ui2, "Name")
                    if nn is not None and nn.value:
                        name = (scalar(nn), nn.src)
    if name is None:
        editable = next((c for c in comps_children(resolved)
                         if c.name == "SCR_EditableEntityComponent"), None)
        if editable is not None:
            eui = find_child(editable, "m_UIInfo")
            if eui is not None:
                nn = find_child(eui, "Name")
                if nn is not None and nn.value:
                    name = (scalar(nn), nn.src)

    physical = _physical_extract(resolved)

    attach_slots = []
    for a in inner:
        if a.name != "AttachmentSlotComponent":
            continue
        sl = find_child(a, "AttachmentSlot")
        att_types = [c.id or c.name for c in a.children
                     if c.name == "AttachmentType"]
        attach_slots.append({
            "slot": (scalar(sl) if sl else None),
            "pivot": pval(find_child(sl, "PivotID")) if sl else None,
            "enabled": pval(find_child(a, "Enabled")),
            "attachment_types": att_types,
            "defined_in": a.src,
        })

    # sights
    sights_info = None
    if sights is not None:
        ranges = []
        sr = find_child(sights, "SightsRanges")
        if sr:
            for rng in sr.children:
                r = find_child(rng, "Range")
                ranges.append(list(r.value) if r is not None else None)
        sights_info = {
            "switch_skip": pval(find_child(sights, "SightsSwitchSkip")),
            "ranges": ranges,
            "defined_in": sights.src,
        }

    muzzle_attachments = None
    if muzzle is not None:
        mz_inner = find_child(muzzle, "components")
        if mz_inner is not None:
            slot = next((c for c in mz_inner.children
                         if c.name == "AttachmentSlotComponent"), None)
            if slot is not None:
                sl = find_child(slot, "AttachmentSlot")
                muzzle_attachments = {
                    "slot": scalar(sl) if sl else None,
                    "enabled": pval(find_child(slot, "Enabled")),
                    "defined_in": slot.src,
                }

    return {
        "identity": {
            "name": {"value": name[0], "defined_in": name[1], "inherited": name[1] != TOP_REL} if name else None,
        },
        "fire_modes": fire_nodes,
        "physical": physical,
        "magazine": {
            "magazine_well": {"name": mw.name, "class": mw.type,
                              "defined_in": mw.src} if mw else None,
            "magazine_template": mag_template,
        },
        "ballistics": {
            "bullet_init_speed_coef": pval(field_in_weapon("BulletInitSpeedCoef")),
            "dispersion_diameter": pval(field_in_weapon("DispersionDiameter")),
            "dispersion_range": pval(field_in_weapon("DispersionRange")),
        },
        "aim": {
            "recoil": recoil,
            "sway": sway,
        },
        "sights": sights_info,
        "attachment_slots": attach_slots,
        "muzzle_attachment": muzzle_attachments,
        "animation": {
            "anim_graph": pref(find_child(anim, "AnimGraph")) if anim else None,
            "anim_instance": pref(find_child(anim, "AnimInstance")) if anim else None,
        },
    }


def _recoil_extract(am):
    out = {}
    for field in ("LinearData", "AngularData", "TurnOffsetData"):
        d = find_child(am, field)
        if d is None:
            out[field] = None
            continue
        rec = {}
        for attr in ("Curve Magnitudes", "Curve Mins", "Curve Maxs",
                     "Curve Time Scale", "Base Recoil Scale"):
            nd = find_child(d, attr)
            rec[attr.replace(" ", "_").lower()] = pvec(nd) if nd is not None else None
        out[field] = {"values": rec, "defined_in": d.src}
    return out


def _sway_extract(am):
    rec = {}
    for attr in ("Lower Translation", "Lower Rotation"):
        nd = find_child(am, attr)
        rec[attr.replace(" ", "_").lower()] = pvec(nd) if nd is not None else None
    return {"defined_in": am.src, "values": rec}


def _physical_extract(resolved):
    comps = comps_children(resolved)
    storage = next((c for c in comps
                    if c.name == "SCR_WeaponAttachmentsStorageComponent"), None)
    rigids = [c for c in comps if c.name == "RigidBody"]
    melee = next((c for c in comps if c.name == "SCR_MeleeWeaponProperties"),
                 None)
    mesh = next((c for c in comps if c.name == "MeshObject"), None)

    phys = {}
    if storage is not None:
        attrs = find_child(storage, "Attributes")
        itm = find_child(attrs, "ItemPhysAttributes")
        if itm is not None and itm.children:
            ipa = itm.children[0]
            for f in ("Weight", "SizeSetupStrategy", "ItemDimensions",
                      "ItemVolume", "DimensionScaler"):
                n = find_child(ipa, f)
                phys[f] = pval(n) if n is not None else None
            phys["_defined_in"] = ipa.src
    if rigids:
        mass = find_child(rigids[0], "Mass")
        phys["Mass"] = pval(mass) if mass is not None else None
    if melee is not None:
        phys["MeleeDamage"] = pval(find_child(melee, "m_fDamage"))
    if mesh is not None:
        obj = find_child(mesh, "Object")
        phys["Model"] = pref(obj) if obj is not None else None
    return phys


# ---------------------------------------------------------------- magazines

def magazine_extract(resolved, context):
    global TOP_REL
    TOP_REL = context["rel"]
    comps = comps_children(resolved)
    mag = next((c for c in comps if c.name == "MagazineComponent"), None)
    inv = next((c for c in comps
                if c.name == "InventoryMagazineComponent"), None)
    editable = next((c for c in comps
                     if c.name == "SCR_EditableEntityComponent"), None)
    mesh = next((c for c in comps if c.name == "MeshObject"), None)

    out = {}
    if mag is not None:
        mw = find_child(mag, "MagazineWell")
        ui = find_child(mag, "UIInfo")
        ammo_cfg = find_child(mag, "AmmoConfig")
        out["magazine_well"] = \
            {"name": mw.name, "class": mw.type, "defined_in": mw.src} \
            if mw else None
        if ammo_cfg is not None and ammo_cfg.ref:
            out["ammo_config"] = {"guid": ammo_cfg.ref["guid"],
                                  "path": ammo_cfg.ref["path"],
                                  "defined_in": ammo_cfg.src}
        if ammo_cfg is None and mag.src:
            out["ammo_config_missing"] = ("able to search parent / external; "
                                          "no local AmmoConfig found")
        out["max_ammo"] = pval(find_child(mag, "MaxAmmo"))
        out["ammo_mapping"] = list(find_child(mag, "AmmoMapping").value) \
            if find_child(mag, "AmmoMapping") else None
        if ui is not None:
            cal = find_child(ui, "m_sAmmoCaliber")
            name = find_child(ui, "Name")
            out["caliber_id"] = pval(cal) if cal is not None else None
            out["name"] = pval(name) if name is not None else None
        out["_defined_in"] = mag.src

    if inv is not None:
        attrs = find_child(inv, "Attributes")
        itm = find_child(attrs, "ItemDisplayName")
        if itm is not None and itm.children:
            ui = itm.children[0]
            n = find_child(ui, "Name")
            out["display_name"] = pval(n) if n is not None else None
        ipa = find_child(attrs, "ItemPhysAttributes")
        if ipa is not None and ipa.children:
            ip = ipa.children[0]
            w = find_child(ip, "Weight")
            out["weight"] = pval(w) if w is not None else None
        gw = find_child(attrs, "m_iCustomGridWidth")
        gh = find_child(attrs, "m_iCustomGridHeight")
        out["grid"] = {"width": pval(gw) if gw else None,
                       "height": pval(gh) if gh else None}
        out["_inv_defined_in"] = inv.src

    if editable is not None:
        ui = find_child(editable, "m_UIInfo")
        if ui is not None:
            n = find_child(ui, "Name")
            out["editor_name"] = pval(n) if n is not None else None

    if mesh is not None:
        obj = find_child(mesh, "Object")
        out["model"] = pref(obj) if obj is not None else None
    return out


# --------------------------------------------------------------- ammunition

def ammunition_extract(resolved, context):
    global TOP_REL
    TOP_REL = context["rel"]
    comps = comps_children(resolved)
    shell = next((c for c in comps if c.name == "ShellMoveComponent"),
                 None)
    timer = next((c for c in comps if c.name == "TimerTriggerComponent"),
                 None)

    out = {}
    if shell is not None:
        out["shell"] = {}
        for f in ("InitSpeed", "InitSpeedVariation", "DispersionMultiplier",
                  "Mass", "TumblingDamageMultiplier", "PenetrationDepth",
                  "PenetrationSpeed", "PenetrationDensity", "AirDrag"):
            n = find_child(shell, f)
            out["shell"][f] = pval(n) if n is not None else None
        bt = find_child(shell, "BallisticTableConfig")
        out["shell"]["ballistic_table"] = pref(bt) if bt is not None else None
        out["shell"]["_defined_in"] = shell.src
    if timer is not None:
        out["timer"] = {
            "time": pval(find_child(timer, "TIMER")),
            "safety_distance": pval(find_child(timer, "SafetyDistance")),
            "_defined_in": timer.src,
        }

    # damage effects
    effects = None
    # ProjectileEffects can live under ShellMoveComponent (nested) or top level
    for owner in (shell, resolved):
        if owner is None:
            continue
        pe = find_child(owner, "ProjectileEffects")
        if pe is not None:
            effects = []
            for eff in pe.children:
                effects.append(_damage_effect(eff))
            break
    out["effects"] = effects

    out["_defined_in"] = shell.src if shell else None
    return out


def _damage_effect(eff):
    d = {"type": eff.name, "id": eff.id, "defined_in": eff.src}
    if eff.name == "ProjectileDamage":
        for f in ("DamageValue", "DamageType", "MinimumDamage"):
            n = find_child(eff, f)
            d[f] = pval(n) if n is not None else None
    return d


# ----------------------------------------------------------------------------
# reference graph
# ----------------------------------------------------------------------------


def build_ref_graph(entities, resources, all_files, guid_index):
    """Populate per-entity 'references' following the known chains."""
    graph = {}
    for rel, ent in entities.items():
        ctx = []
        for rref in ent["refs"]:
            res = resolve_ref(rref["guid"], rref["path"], all_files, guid_index)
            ctx.append({"guid": rref["guid"], "path": rref["path"],
                        "resolved": res["status"],
                        "target": res.get("rel"),
                        "defined_in": rref.get("defined_in")})
        graph[rel] = ctx
    return graph


# ----------------------------------------------------------------------------
# main pipeline
# ----------------------------------------------------------------------------


def main():
    print(f"MOD_ROOT   = {MOD_ROOT}")
    print(f"REPO_ROOT  = {REPO_ROOT}")

    all_files = index_all_files(MOD_ROOT)
    print(f"files indexed: {len(all_files)}")

    text_rels = [r for r in all_files
                 if os.path.splitext(r)[1].lower() in (".et", ".conf", ".meta", ".c")]
    resources = parse_text_resources(all_files, text_rels)
    print(f"text resources parsed: {len(resources)}")

    et_resources = {r: x for r, x in resources.items() if x.kind == "et"}
    guid_index, aliases, by_actual = build_guid_index(resources)
    print(f"guid index entries: {len(guid_index)}")

    entities = OrderedDict()
    for rel in sorted(et_resources):
        res = et_resources[rel]
        chain, external = build_chain(res, et_resources, all_files, guid_index)
        local_rels = [c["rel"] for c in chain if c.get("status") == "local"]
        resolved = chain_merge(local_rels, et_resources) if local_rels else None
        categories = classify(res, resolved)
        entities[rel] = {
            "rel": rel,
            "stem": res.stem,
            "class": res.et_class,
            "categories": categories,
            "chain": chain,
            "external_parents": external,
            "resolved": resolved,
            "has_local_components": bool(local_rels),
        }

    # role: base templates vs leaf items
    for rel, ent in entities.items():
        children = [e["rel"] for e in entities.values()
                    if any(c.get("status") == "local" and c["rel"] == rel
                           for c in e["chain"][1:])]
        ent["used_as_base_by"] = children
        ent["role"] = "base" if children else "leaf"

    # persist working tables for debugging
    os.makedirs(CATALOG_DIR, exist_ok=True)
    dump_working_tables(entities)

    import shutil
    for d in (CATALOG_DIR, INDEX_DIR, REPORT_DIR, SCHEMA_DIR):
        if os.path.isdir(d):
            shutil.rmtree(d, ignore_errors=True)
    for f in (os.path.join(AGENT_DIR, "scan_state.json"),):
        if os.path.isfile(f):
            os.remove(f)

    # export catalogs
    stats = export_catalogs(entities, resources, all_files, guid_index, by_actual)
    export_indexes(entities, stats)
    graph = build_reference_graph(entities, resources, all_files, guid_index)
    with open(os.path.join(INDEX_DIR, "reference_graph.json"), "w",
              encoding="utf-8") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)
    export_schemas()
    write_reports(entities, stats, graph)
    write_scan_state(stats)

    print("\n--- scan summary ---")
    for k, v in stats.items():
        print(f"{k:>28}: {v}")
    print(f"warnings: {len(W)}")


def dump_working_tables(entities):
    tmp = os.path.join(SCRIPT_DIR, "working_tables")
    os.makedirs(tmp, exist_ok=True)
    table = []
    for rel, ent in entities.items():
        table.append({
            "rel": rel,
            "class": ent["class"],
            "kind": ent["categories"].get("kind"),
            "chain": [c.get("rel") for c in ent["chain"]],
            "external_parents": ent["external_parents"],
        })
    with open(os.path.join(tmp, "entities.json"), "w", encoding="utf-8") as f:
        json.dump(table, f, indent=1, ensure_ascii=False)
    print(f"entities table: {len(entities)} entities -> agent/scripts/working_tables/")


def build_reference_graph(entities, resources, all_files, guid_index):
    """Build the semantic link graph weapon -> magazine -> ammo(conf) + inheritance.

    Also computes effective muzzle velocity (InitSpeed * BulletInitSpeedCoef)
    for weapons whose ammo chain resolves to a local ammo entity.
    """
    # prereq: conf resources and their AmmoResourceArray entries
    conf_ammo = {}
    for r in resources.values():
        if r.kind != "conf":
            continue
        arr_nodes = find_recursive(r.root, "AmmoResourceArray")
        arr = arr_nodes[0] if arr_nodes else None
        if arr is None:
            continue
        ammos = []
        for c in arr.children:
            if c.ref is None:
                continue
            res = resolve_ref(c.ref["guid"], c.ref["path"], all_files,
                              guid_index)
            ammos.append({"path": c.ref["path"], "target": res.get("rel"),
                          "status": res["status"]})
        conf_ammo[r.relpath] = ammos

    edges = []
    local_nodes = set(entities)

    def add_edge(frm, to, kind, status, defined_in=None):
        edges.append({"from": frm, "to": to, "kind": kind,
                      "status": status, "defined_in": defined_in})

    def dig(node, keys):
        """node[k1][k2]... with safe traversal."""
        cur = node
        for k in keys:
            if cur is None or not isinstance(cur, dict):
                return None
            cur = cur.get(k)
        return cur

    by_rel = {e["rel"]: e for e in entities.values()}

    for rel, ent in entities.items():
        doc = ent.get("_doc") or {}
        data = doc.get("data") or {}

        # inheritance chain -> parent edges
        chain = ent["chain"]
        for a, b in zip(chain, chain[1:]):
            if a.get("status") != "local":
                continue
            bt = b.get("rel")
            if not bt:
                continue
            st = b.get("status", "loop")
            add_edge(a["rel"], bt, "inherits", st, defined_in=a["rel"])
        for ext in ent["external_parents"]:
            add_edge(rel, ext["path"], "inherits_base_game", "external",
                     defined_in=rel)

        if ent["categories"].get("kind") == "weapon":
            tmpl = dig(data, ["magazine", "magazine_template"])
            if tmpl:
                res = resolve_ref(tmpl["guid"], tmpl["path"], all_files,
                                  guid_index)
                add_edge(rel, res.get("rel") or tmpl["path"],
                         "uses_magazine", res["status"],
                         defined_in=tmpl.get("defined_in"))

        elif ent["categories"].get("kind") == "magazine":
            acfg = dig(data, ["ammo_config"])
            if acfg:
                res = resolve_ref(acfg["guid"], acfg["path"], all_files,
                                  guid_index)
                add_edge(rel, res.get("rel") or acfg["path"],
                         "ammo_config", res["status"],
                         defined_in=acfg.get("defined_in"))
                target = res.get("rel")
                if target:
                    for am in conf_ammo.get(target, []):
                        add_edge(rel, am["target"] or am["path"],
                                 "loaded_with", am["status"],
                                 defined_in=target)

        elif ent["categories"].get("kind") == "ammunition":
            bt = dig(data, ["shell", "ballistic_table"])
            if bt:
                res = resolve_ref(bt["guid"], bt["path"], all_files,
                                  guid_index)
                add_edge(rel, res.get("rel") or bt["path"],
                         "ballistic_table", res["status"],
                         defined_in=bt.get("defined_in"))

    # ---- effective muzzle velocity
    weapon_ballistics = []
    for rel, ent in entities.items():
        if ent["categories"].get("kind") != "weapon":
            continue
        doc = ent.get("_doc") or {}
        data = doc.get("data") or {}
        coef = dig(data, ["ballistics", "bullet_init_speed_coef", "value"])
        if coef is None:
            continue
        tmpl = dig(data, ["magazine", "magazine_template"])
        init_speed = None
        ammo_rel = None
        if tmpl:
            mt = resolve_ref(tmpl["guid"], tmpl["path"], all_files, guid_index)
            mag = by_rel.get(mt.get("rel"))
            if mag:
                mdoc = mag.get("_doc") or {}
                acfg = dig(mdoc.get("data") or {}, ["ammo_config"])
                if acfg:
                    ac = resolve_ref(acfg["guid"], acfg["path"], all_files,
                                     guid_index)
                    ammos = conf_ammo.get(ac.get("rel"), [])
                    if ammos:
                        fam = ammos[0]
                        aent = by_rel.get(fam.get("target"))
                        if aent:
                            ammo_rel = fam["target"]
                            adoc = aent.get("_doc") or {}
                            init_speed = dig(adoc.get("data") or {},
                                             ["shell", "InitSpeed", "value"])
        weapon_ballistics.append({
            "weapon": rel,
            "bullet_init_speed_coef": coef,
            "ammo": ammo_rel,
            "ammo_init_speed": init_speed,
            "effective_muzzle_velocity":
                round(coef * init_speed, 2) if init_speed is not None else None,
            "derived": init_speed is not None,
        })

    return {
        "note": ("Semantic links between mod entities. 'external' targets lie "
                 "outside this addon (base game data, closed to the mod)."),
        "nodes_local": sorted(local_nodes),
        "edge_count": len(edges),
        "edges": edges,
        "weapon_ballistics": weapon_ballistics,
    }


def export_catalogs(entities, resources, all_files, guid_index, by_actual):
    import shutil
    if os.path.isdir(CATALOG_DIR):
        shutil.rmtree(CATALOG_DIR, ignore_errors=True)
    stats = {"entities": len(entities), "weapons": 0, "magazines": 0,
             "ammunition": 0, "optics": 0, "attachments": 0, "grenades": 0,
             "tripods": 0, "core": 0, "particles": 0, "misc": 0}
    plural = {"weapon": "weapons", "magazine": "magazines", "ammunition": "ammunition",
              "optic": "optics", "attachment": "attachments", "grenade": "grenades",
              "tripod": "tripods", "core": "core", "particle": "particles",
              "misc": "misc"}
    base_dirs = {
        "weapon": os.path.join(CATALOG_DIR, "weapons"),
        "magazine": os.path.join(CATALOG_DIR, "magazines"),
        "ammunition": os.path.join(CATALOG_DIR, "ammunition"),
        "optic": os.path.join(CATALOG_DIR, "optics"),
        "attachment": os.path.join(CATALOG_DIR, "attachments"),
        "grenade": os.path.join(CATALOG_DIR, "grenades"),
        "tripod": os.path.join(CATALOG_DIR, "tripods"),
        "core": os.path.join(CATALOG_DIR, "core"),
        "particle": os.path.join(CATALOG_DIR, "particles"),
        "misc": os.path.join(CATALOG_DIR, "misc"),
    }
    for d in base_dirs.values():
        os.makedirs(d, exist_ok=True)

    for rel, ent in entities.items():
        res = resources[rel]
        kind = ent["categories"].get("kind", "misc")
        if kind == "attachment" and \
                ent["categories"].get("attachment_kind") == "optic":
            kind = "optic"
        doc = build_catalog_entry(ent, res, resources, all_files, guid_index,
                                  by_actual)
        ent["_doc"] = doc
        slug = slugify(rel)
        fname = os.path.join(base_dirs[kind], slug + ".json")
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)
        stats[plural[kind]] += 1
    return stats


def slugify(rel):
    stem = re.sub(r"\.et$", "", os.path.basename(rel))
    s = re.sub(r"[^A-Za-z0-9]+", "_", stem).strip("_").lower()
    return s or "entity"


def build_catalog_entry(ent, res, resources, all_files, guid_index, by_actual):
    rel = ent["rel"]
    kind = ent["categories"].get("kind", "misc")
    global TOP_REL
    TOP_REL = rel

    refs = collect_refs(ent["resolved"])

    entry = {
        "id": slugify(rel),
        "role": ent.get("role", "leaf"),
        "source": {
            "resource": rel,
            "resource_guid": by_actual.get(rel),
            "meta_name": _meta_path_for(rel, resources),
            "class": ent["class"],
            "defined_in": rel,
        },
        "identity": _extract_identity(ent, kind),
        "classification": ent["categories"],
        "inheritance": {
            "chain": [{"resource": c.get("rel"),
                       "status": c.get("status"),
                       "class": c.get("class")} for c in ent["chain"]],
            "external_parents": ent["external_parents"],
            "used_as_base_by": ent.get("used_as_base_by", []),
            "chain_depth_local": len([c for c in ent["chain"]
                                      if c.get("status") == "local"]),
        },
        "references": _resolve_ref_list(refs, all_files, guid_index),
        "warnings": [w for w in W if w["category"] in ("PARSE", "INHERIT-LOOP")
                     and rel in w.get("message", "")],
    }

    if kind == "weapon":
        entry["data"] = weapon_extract(ent["resolved"], {"rel": rel})
        entry["derived"] = derive_weapon(entry)
    elif kind == "magazine":
        entry["data"] = magazine_extract(ent["resolved"], {"rel": rel})
        entry["derived"] = derive_magazine(entry)
    elif kind == "ammunition":
        entry["data"] = ammunition_extract(ent["resolved"], {"rel": rel})
        entry["derived"] = derive_ammunition(entry)
    return entry


def _meta_path_for(rel, resources):
    meta = rel + ".meta"
    r = resources.get(meta)
    if r is None:
        return None
    n = find_child(r.root, "Name")
    if n and n.value:
        return str(n.value[0])
    return None


def _resolve_ref_list(refs, all_files, guid_index):
    seen = {}
    for r in refs:
        key = r["guid"] + "|" + r["path"]
        if key in seen:
            continue
        res = resolve_ref(r["guid"], r["path"], all_files, guid_index)
        seen[key] = {"guid": r["guid"], "path": r["path"],
                     "resolved": res["status"],
                     "target": res.get("rel"),
                     "defined_in": r.get("defined_in")}
    return list(seen.values())


def _extract_identity(ent, kind):
    rel = ent["rel"]
    stem = ent["stem"]
    return {"name": stem, "resource": rel}


# ----------------------------------------------------------------------------
# derived computations
# ----------------------------------------------------------------------------


def derive_weapon(entry):
    out = {}

    fps_list = []
    data = entry.get("data", {})
    for fm in data.get("fire_modes", []):
        rpm = fm.get("rounds_per_minute")
        if rpm and isinstance(rpm.get("value"), (int, float)):
            fps_list.append(rpm["value"] / 60.0)
        if rpm and isinstance(rpm.get("value"), (int, float)):
            fm.setdefault("rounds_per_second",
                          {"value": round(rpm["value"] / 60.0, 3),
                           "derived": True})
    if fps_list:
        out["max_rounds_per_second"] = round(max(fps_list), 3)

    disp = data.get("ballistics", {})
    dd = disp.get("dispersion_diameter")
    dr = disp.get("dispersion_range")
    if dd and dr and isinstance(dd.get("value"), (int, float)) \
            and isinstance(dr.get("value"), (int, float)) \
            and dr["value"] != 0:
        ratio = dd["value"] / dr["value"]
        out["dispersion_m_per_m"] = {"value": round(ratio * 1000, 4),
                                     "formula": "DispersionDiameter / DispersionRange * 1000"}
        out["approx_moa"] = {"value": round(ratio * 3437.74677, 3),
                             "formula": "DispersionDiameter / DispersionRange * 3437.75"}

    # effective muzzle velocity comes from weapon <-> ammo links filled later
    return out


def derive_magazine(entry):
    out = {}
    data = entry.get("data", {})
    maxa = data.get("max_ammo")
    if maxa and isinstance(maxa.get("value"), (int, float)):
        out["capacity"] = maxa["value"]
    return out


def derive_ammunition(entry):
    out = {}
    data = entry.get("data", {})
    sh = data.get("shell") or {}
    init = sh.get("InitSpeed")
    if init and isinstance(init.get("value"), (int, float)):
        out["init_speed"] = init["value"]
    eff = data.get("effects") or []
    for e in eff:
        if e.get("type") == "ProjectileDamage":
            dv = e.get("DamageValue")
            if dv and isinstance(dv.get("value"), (int, float)):
                out["projectile_damage"] = dv["value"]
    return out


# ----------------------------------------------------------------------------
# indexes, schemas, reports, state
# ----------------------------------------------------------------------------


def export_indexes(entities, stats):
    os.makedirs(INDEX_DIR, exist_ok=True)

    def index_for(kind):
        rows = []
        for rel, ent in entities.items():
            if ent["categories"].get("kind") != kind:
                continue
            rows.append({
                "id": slugify(rel),
                "resource": rel,
                "class": ent["class"],
                "name": ent["stem"],
                "role": ent.get("role", "leaf"),
            })
        return rows

    def index_for_attachment(akind):
        rows = []
        for rel, ent in entities.items():
            if ent["categories"].get("kind") == "attachment" and \
                    ent["categories"].get("attachment_kind") == akind:
                rows.append({
                    "id": slugify(rel),
                    "resource": rel,
                    "class": ent["class"],
                    "name": ent["stem"],
                    "role": ent.get("role", "leaf"),
                })
        return rows

    weapons = index_for("weapon")
    magazines = index_for("magazine")
    ammunition = index_for("ammunition")
    optics = index_for_attachment("optic")
    attachments = index_for("attachment")
    grenades = index_for("grenade")

    with open(os.path.join(INDEX_DIR, "weapons.json"), "w", encoding="utf-8") as f:
        json.dump(weapons, f, indent=2, ensure_ascii=False)
    with open(os.path.join(INDEX_DIR, "magazines.json"), "w", encoding="utf-8") as f:
        json.dump(magazines, f, indent=2, ensure_ascii=False)
    with open(os.path.join(INDEX_DIR, "ammunition.json"), "w", encoding="utf-8") as f:
        json.dump(ammunition, f, indent=2, ensure_ascii=False)
    with open(os.path.join(INDEX_DIR, "optics.json"), "w", encoding="utf-8") as f:
        json.dump(optics, f, indent=2, ensure_ascii=False)
    with open(os.path.join(INDEX_DIR, "attachments.json"), "w", encoding="utf-8") as f:
        json.dump(attachments, f, indent=2, ensure_ascii=False)

    # reference graph: summary of link categories
    graph = {
        "note": "full link graph is available per-entity in catalog/*/references",
        "entity_count": len(entities),
    }
    with open(os.path.join(INDEX_DIR, "references.json"), "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)


def export_schemas():
    os.makedirs(SCHEMA_DIR, exist_ok=True)
    pv = {
        "type": ["number", "string", "boolean", "null"],
        "description": "Resolved scalar value.",
    }
    pv_obj = {
        "type": "object",
        "properties": {
            "value": pv,
            "defined_in": {"type": ["string", "null"],
                           "description": "Resource that defined this value."},
            "inherited": {"type": "boolean",
                          "description": "True when the value comes from a "
                                         "parent in the chain, not the entity "
                                         "file itself."},
        },
        "required": ["value"],
    }
    ref = {
        "type": "object",
        "properties": {
            "guid": {"type": "string"}, "path": {"type": "string"},
            "defined_in": {"type": "string"},
        },
    }
    chain_item = {
        "type": "object",
        "properties": {
            "resource": {"type": "string"},
            "status": {"enum": ["local", "file", "loop"]},
            "class": {"type": "string"},
        },
    }
    ext_parent = {
        "type": "object",
        "properties": {
            "guid": {"type": "string"}, "path": {"type": "string"},
            "raw": {"type": "string"},
        },
    }
    ref_entry = {
        "type": "object",
        "properties": {
            "guid": {"type": "string"}, "path": {"type": "string"},
            "resolved": {"enum": ["local", "external"]},
            "target": {"type": ["string", "null"]},
            "defined_in": {"type": ["string", "null"]},
        },
        "required": ["guid", "path", "resolved"],
    }

    common = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "role": {"enum": ["leaf", "base"]},
            "source": {"type": "object", "properties": {
                "resource": {"type": "string"},
                "resource_guid": {"type": ["string", "null"]},
                "meta_name": {"type": ["string", "null"]},
                "class": {"type": ["string", "null"]},
                "defined_in": {"type": "string"},
            }},
            "identity": {"type": "object", "properties": {
                "name": {"type": ["string", "null"]},
                "resource": {"type": "string"},
            }},
            "classification": {"type": "object", "properties": {
                "kind": {"type": "string"},
                "confidence": {"enum": ["components", "folder", "class",
                                        "unknown"]},
                "attachment_kind": {"type": "string"},
            }},
            "inheritance": {"type": "object", "properties": {
                "chain": {"type": "array", "items": chain_item},
                "external_parents": {"type": "array", "items": ext_parent},
                "used_as_base_by": {"type": "array", "items": {"type": "string"}},
                "chain_depth_local": {"type": "integer"},
            }},
            "references": {"type": "array", "items": ref_entry},
            "warnings": {"type": "array"},
            "derived": {"type": "object"},
        },
        "required": ["id", "source", "identity", "classification",
                     "inheritance", "references"],
    }

    weapon = dict(common)
    weapon.update({
        "title": "Resolved weapon prefab (catalog/weapons/*.json)",
        "description": "ARMST weapon with resolved balance parameters. Every "
                       "field carries provenance (defined_in / inherited). "
                       "External (base game) data is never guessed.",
        "properties": dict(common["properties"], data={"type": "object",
            "properties": {
                "identity": {"type": "object", "properties": {
                    "name": pv_obj, "description": {"type": "string"}}},
                "fire_modes": {"type": "array", "items": ref},
                "physical": {"type": "object"},
                "magazine": {"type": "object", "properties": {
                    "magazine_well": {"type": ["object", "null"], "properties": {
                        "name": {"type": "string"},
                        "class": {"type": ["string", "null"]},
                        "defined_in": {"type": "string"}}},
                    "magazine_template": {"type": ["object", "null"],
                                          "properties": ref["properties"]}}},
                "ballistics": {"type": "object", "properties": {
                    "bullet_init_speed_coef": pv_obj,
                    "dispersion_diameter": pv_obj,
                    "dispersion_range": pv_obj}},
                "aim": {"type": "object"},
                "sights": {"type": "object"},
                "attachment_slots": {"type": "array"},
                "muzzle_attachment": {"type": "object"},
                "animation": {"type": "object"},
            }}),
    })

    magazine = dict(common)
    magazine.update({
        "title": "Resolved magazine prefab (catalog/magazines/*.json)",
        "properties": dict(common["properties"], data={"type": "object",
            "properties": {
                "magazine_well": {"type": ["object", "null"]},
                "ammo_config": {"type": ["object", "null"],
                                "properties": ref["properties"]},
                "max_ammo": pv_obj,
                "caliber_id": {"type": ["object", "null"]},
                "name": {"type": ["object", "null"]},
                "display_name": {"type": ["object", "null"]},
                "weight": {"type": ["object", "null"]},
                "grid": {"type": "object"},
                "editor_name": {"type": ["object", "null"]},
                "model": {"type": ["object", "null"]},
            }}),
    })

    ammunition = dict(common)
    ammunition.update({
        "title": "Resolved ammunition prefab (catalog/ammunition/*.json)",
        "properties": dict(common["properties"], data={"type": "object",
            "properties": {
                "shell": {"type": "object", "properties": {
                    "InitSpeed": pv_obj, "InitSpeedVariation": pv_obj,
                    "DispersionMultiplier": pv_obj, "Mass": pv_obj,
                    "TumblingDamageMultiplier": {"type": ["number", "null"]},
                    "PenetrationDepth": {"type": ["object", "null"]},
                    "PenetrationSpeed": {"type": ["object", "null"]},
                    "PenetrationDensity": {"type": ["object", "null"]},
                    "AirDrag": {"type": ["object", "null"]},
                    "ballistic_table": {"type": ["object", "null"]}},
                    "required": ["InitSpeed"]},
                "effects": {"type": "array"},
            }}),
    })

    for fname, sch in (("entity.schema.json", common),
                       ("weapon.schema.json", weapon),
                       ("magazine.schema.json", magazine),
                       ("ammunition.schema.json", ammunition)):
        with open(os.path.join(SCHEMA_DIR, fname), "w", encoding="utf-8") as f:
            json.dump(sch, f, indent=2, ensure_ascii=False)


def write_reports(entities, stats, graph=None):
    from collections import Counter
    os.makedirs(REPORT_DIR, exist_ok=True)
    local = [e for e in entities.values()]
    resolved_local = [e for e in local if e["has_local_components"]]

    # ---- scan summary
    sum_kind = Counter(e["categories"].get("kind") for e in local)
    summary = {
        "mod_root": MOD_ROOT,
        "repo_root": REPO_ROOT,
        "entities": len(local),
        "entities_with_local_chain": len(resolved_local),
        "counts_by_classification": dict(sum_kind.most_common()),
        "warnings": len(W),
        "graph_edges": (graph or {}).get("edge_count"),
        "weapons_with_effective_velocity": sum(
            1 for w in (graph or {}).get("weapon_ballistics", [])
            if w.get("effective_muzzle_velocity") is not None),
    }
    with open(os.path.join(REPORT_DIR, "scan_summary.json"), "w",
              encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    with open(os.path.join(REPORT_DIR, "scan_summary.md"), "w",
              encoding="utf-8") as f:
        f.write("# Scan summary\n\n")
        f.write(f"- Mod root: `{MOD_ROOT}`\n")
        f.write(f"- Repository: `{REPO_ROOT}`\n")
        f.write(f"- Entities (.et with local chain): {len(local)}\n")
        f.write(f"- Warnings: {len(W)}\n")
        f.write(f"- Graph edges: {summary['graph_edges']}\n\n")
        f.write("## Counts by classification\n\n")
        for k, v in sum_kind.most_common():
            f.write(f"- {k}: {v}\n")

    # ---- unresolved references (external = base game data, not read)
    unresolved = []
    for e in local:
        refs = []
        doc = e.get("_doc") or {}
        for r in doc.get("references", []):
            if r.get("resolved") == "external":
                refs.append({"path": r.get("path"), "guid": r.get("guid"),
                             "defined_in": r.get("defined_in")})
        if refs:
            unresolved.append({"entity": e["rel"], "external_refs": refs})
    ur_doc = {
        "note": ("These targets are not present in this addon. They live in "
                 "the base game data, which is closed to this analysis; no "
                 "values were guessed for them."),
        "entities": unresolved,
        "total_external_refs": sum(len(u["external_refs"]) for u in unresolved),
    }
    with open(os.path.join(REPORT_DIR, "unresolved_references.json"), "w",
              encoding="utf-8") as f:
        json.dump(ur_doc, f, indent=2, ensure_ascii=False)
    with open(os.path.join(REPORT_DIR, "unresolved_references.md"), "w",
              encoding="utf-8") as f:
        f.write("# Unresolved references (base game data)\n\n")
        f.write(ur_doc["note"] + "\n\n")
        for u in unresolved:
            f.write(f"\n## {u['entity']}\n")
            f.write("```json\n" + json.dumps(u["external_refs"], indent=2)
                    + "\n```\n")

    # ---- inheritance issues
    issues = []
    for e in local:
        isues = []
        if any(c.get("status") == "loop" for c in e["chain"]):
            isues.append("inheritance loop detected")
        if e["external_parents"]:
            isues.append("external tail: " + e["external_parents"][0].get("path"))
        if not isues:
            continue
        issues.append({"entity": e["rel"], "issues": isues})
    with open(os.path.join(REPORT_DIR, "inheritance_issues.json"), "w",
              encoding="utf-8") as f:
        json.dump(issues, f, indent=2, ensure_ascii=False)
    with open(os.path.join(REPORT_DIR, "inheritance_issues.md"), "w",
              encoding="utf-8") as f:
        f.write("# Inheritance issues\n\n")
        if not issues:
            f.write("No inheritance issues.\n")
        for i in issues:
            f.write(f"- **{i['entity']}**: {'; '.join(i['issues'])}\n")

    # ---- anomalies
    with open(os.path.join(REPORT_DIR, "anomalies.json"), "w",
              encoding="utf-8") as f:
        json.dump(W, f, indent=2, ensure_ascii=False)
    with open(os.path.join(REPORT_DIR, "anomalies.md"), "w",
              encoding="utf-8") as f:
        f.write("# Anomalies\n\n")
        if not W:
            f.write("No anomalies recorded.\n")
        else:
            for w in W:
                f.write(f"- [{w['category']}] {w['message']}\n")

    # ---- weapon ballistics summary (effective muzzle velocity)
    if graph:
        with open(os.path.join(REPORT_DIR, "weapon_ballistics.json"), "w",
                  encoding="utf-8") as f:
            json.dump({"weapons": graph.get("weapon_ballistics", []),
                       "note": ("effective_muzzle_velocity = ammo InitSpeed "
                                "* weapon BulletInitSpeedCoef; set when the "
                                "magazine template resolves to a local "
                                "magazine with a local ammo config.")},
                       f, indent=2, ensure_ascii=False)


def write_scan_state(stats):
    os.makedirs(AGENT_DIR, exist_ok=True)
    import datetime
    state = {
        "schema_version": "1.0",
        "mod_root": MOD_ROOT,
        "repo_root": REPO_ROOT,
        "scan_date": datetime.date.today().isoformat(),
        "tool": "agent/scripts/scan_build.py",
        "stats": stats,
        "warnings": len(W),
        "steps": {
            "inventory": "done",
            "parse": "done",
            "inherit_chains": "done",
            "resolution": "done",
            "extraction": "done",
            "derived": "done",
            "reference_graph": "done",
            "catalogs": "done",
            "indexes": "done",
            "reports": "done",
        },
    }
    with open(os.path.join(AGENT_DIR, "scan_state.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()