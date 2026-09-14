"""
et_parser.py
============
Parser for Arma Reforger workbench text resources:

  * `.et`  - entity / prefab templates    (class : "{GUID}path" { ... })
  * `.conf`- configuration resources      (FooConfig { ... })
  * `.meta`- meta files for resources     (Name "{GUID}path" ...)
  * `.c`   - script class definitions     (class X : Y { })

The parser is intentionally generic: it converts a resource file into an
ordered tree of Nodes. It makes no assumptions about specific component
classes; interpretation (which nodes are weapon balance params, links, etc.)
happens in scan_build.py.

Node model
----------
Each Node has:
  name     -- first token of the line (field name or serialized class name)
  type     -- optional second token (class name for `Field Class id {}` lines)
  id       -- optional third token: a GUID, an instance name, or a slot name
  value    -- parsed scalar tokens for value-only lines
  children -- child Nodes for `{ ... }` blocks
  append   -- True when the line used the `+` (append) modifier before `{`
  ref      -- parsed resource reference "{GUID}path..." if the value tokens
              contain one (first token only)
"""

import re
import os

GUID_REF_RE = re.compile(r"^\{([0-9A-Fa-f]{1,32})\}(.*)$")
INT_RE = re.compile(r"^[+-]?\d+$")
HEX_RE = re.compile(r"^0[xX][0-9A-Fa-f]+$")
FLOAT_RE = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$")
RESOURCE_EXT = (".et", ".conf", ".meta", ".ptc", ".xob", ".emat", ".asi", ".agr",
                ".acp", ".anm", ".edds", ".wav", ".txt", ".gproj", ".ent", ".layer")


class ParseError(Exception):
    pass


class Node:
    __slots__ = ("name", "type", "id", "value", "children", "append", "line", "ref")

    def __init__(self, name, typ=None, nid=None, value=None, children=None,
                 append=False, line=0):
        self.name = name
        self.type = typ
        self.id = nid
        self.value = value if value is not None else []
        self.children = children if children is not None else []
        self.append = append
        self.line = line
        self.ref = None

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
        if self.line:
            d["line"] = self.line
        if self.children:
            d["children"] = [c.to_dict() for c in self.children]
        return d

    def __repr__(self):
        return f"<Node {self.name} id={self.id} value={self.value} n={len(self.children)}>"


def _split_tokens(line):
    """Split a line on whitespace, keeping double-quoted strings intact."""
    tokens = []
    i, n = 0, len(line)
    while i < n:
        c = line[i]
        if c.isspace():
            i += 1
            continue
        if c == '"':
            j = line.find('"', i + 1)
            if j == -1:
                j = n
            tokens.append(line[i:j + 1])
            i = j + 1
            continue
        j = i
        while j < n and not line[j].isspace():
            j += 1
        tokens.append(line[i:j])
        i = j
    return tokens


def _strip_quotes(tok):
    if len(tok) >= 2 and tok.startswith('"') and tok.endswith('"'):
        return tok[1:-1]
    return tok


def _is_number_token(tok):
    return bool(HEX_RE.match(tok) or INT_RE.match(tok) or FLOAT_RE.match(tok))


def _parse_scalar(tok):
    if _is_number_token(tok):
        if HEX_RE.match(tok):
            return int(tok, 16)
        if INT_RE.match(tok):
            return int(tok)
        return float(tok)
    return _strip_quotes(tok)


def _value_token(tok):
    """A token(s) that represents a plain value rather than a field name."""
    if tok.startswith('"'):
        return True
    body = tok
    if bool(GUID_REF_RE.match(body)):
        return True
    if body.startswith("{"):
        return False  # bare GUID without a path -- treat as a name token
    return _is_number_token(body)


def _guid_ref(tok):
    """Return (guid, path) if tok looks like {GUID}rest, else None."""
    m = GUID_REF_RE.match(_strip_quotes(tok))
    if m:
        return m.group(1), m.group(2)
    return None


def _attach_refs(node):
    """Attach ref info to a node based on its first value token."""
    if node.value:
        for t0 in node.value[:1]:
            gr = _guid_ref(str(t0))
            if gr:
                node.ref = {"guid": gr[0].upper(), "path": gr[1], "raw": str(t0)}
    # component instance identifiers may be GUIDs but are NOT resource refs
    return node


def parse_text(resource_text, source_name="<text>", is_et=False):
    """
    Parse resource text into a Node tree.
    Returns (header, root).
    header: dict with class / parent info (for .et) or class (for .conf/.meta)
    """
    lines = resource_text.splitlines()
    root = Node("__root__")
    stack = [(root, -1)]
    header = None
    seen_first = False

    for idx, raw in enumerate(lines):
        if not raw.strip():
            continue
        stripped = raw.lstrip(" \t")
        indent = len(raw) - len(stripped)

        if not seen_first:
            seen_first = True
            if is_et:
                header = _parse_et_header(stripped, idx + 1)
                # header line itself: determine whether it opened a block
                hdr_open = stripped.rstrip().endswith("{")
                if not hdr_open:
                    raise ParseError(f"{source_name}:{idx+1}: "
                                     "entity header must open a block")
                continue

        if stripped == "}":
            # a closing brace closes exactly the innermost open block; the
            # dedent loop below must NOT also run for brace lines, otherwise
            # the frame is popped twice and its parent scope is lost.
            if len(stack) > 1:
                stack.pop()
            continue

        while len(stack) > 1 and indent <= stack[-1][1]:
            stack.pop()
        parent = stack[-1][0]

        # normalized body without closing/trailing tokens
        open_block = stripped.rstrip().endswith("{")
        body = stripped[:-1].rstrip() if open_block else stripped

        tokens = _split_tokens(body)
        if tokens and tokens[-1] == "+":
            tokens = tokens[:-1]
            append = True
        else:
            append = False

        if open_block:
            node = _make_block_node(tokens, idx + 1, append)
        else:
            node = _make_value_node(tokens, idx + 1, append)
        _attach_refs(node)
        parent.children.append(node)

        if open_block:
            stack.append((node, indent))

    return header, root


def _make_block_node(tokens, line, append):
    name = None
    typ = None
    nid = None
    rest = []
    if tokens:
        first = tokens[0]
        name = _strip_quotes(first)
        rest = tokens[1:]
        if len(rest) == 1:
            t = rest[0]
            if t.startswith('"') or t.startswith('{'):
                nid = _strip_quotes(t)
            else:
                typ = t
        elif len(rest) >= 2:
            typ = rest[0]
            nid = _strip_quotes(rest[1])
    node = Node(name, typ, nid, [], [], append, line)
    # some declarations carry a resource reference after the instance id,
    # e.g. "m_MagIndicator X "{id}" : "{GUID}path.conf"" -- grab it.
    for t in rest:
        gr = _guid_ref(t)
        if gr and gr[1]:
            node.ref = {"guid": gr[0].upper(), "path": gr[1], "raw": str(t)}
            break
    return node


def _make_value_node(tokens, line, append):
    if not tokens:
        return Node("__empty__", None, None, [], [], append, line)
    first = tokens[0]
    if first.startswith('"') or _value_token(first):
        # array element line or reference-only line
        values = [_parse_scalar(t) for t in tokens]
        return Node("__elem__", None, None, values, [], append, line)
    name = _strip_quotes(first)
    values = [_parse_scalar(t) for t in tokens[1:]]
    return Node(name, None, None, values, [], append, line)


def _parse_et_header(line, lineno):
    m = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?::\s*\"\{([0-9A-Fa-f]{1,32})\}([^\"]+)\"\s*)?(\{)?\s*$", line)
    if not m:
        raise ParseError(f"line {lineno}: unrecognized entity header: {line!r}")
    cls = m.group(1)
    parent = None
    if m.group(2):
        parent = {
            "guid": m.group(2).upper(),
            "path": m.group(3),
            "raw": f"{{{m.group(2)}}}{m.group(3)}",
        }
    return {"class": cls, "parent": parent, "line": lineno}


class Resource:
    """A parsed resource with its identity and header."""

    def __init__(self, abspath, relpath, kind, header, root):
        self.abspath = abspath
        self.relpath = relpath.replace("\\", "/")
        self.kind = kind  # et | conf | meta | c
        self.header = header
        self.root = root
        self.stem = os.path.splitext(os.path.basename(relpath))[0]

    @property
    def et_class(self):
        return self.header["class"] if self.header else None

    @property
    def parent(self):
        return self.header["parent"] if self.header else None


def parse_file(path, addon_root=None):
    ext = os.path.splitext(path)[1].lower()
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        text = f.read()
    rel = os.path.relpath(path, addon_root) if addon_root else path
    if ext == ".et":
        header, root = parse_text(text, source_name=rel, is_et=True)
        return Resource(path, rel, "et", header, root)
    if ext in (".conf",):
        header, root = parse_text(text, source_name=rel, is_et=False)
        return Resource(path, rel, "conf", header, root)
    if ext in (".meta",):
        header, root = parse_text(text, source_name=rel, is_et=False)
        return Resource(path, rel, "meta", header, root)
    if ext == ".c":
        return Resource(path, rel, "c", None, None)
    raise ValueError(f"unsupported resource type: {path}")


# ---------------------------------------------------------------- query utils

def find_children(node, name):
    return [c for c in node.children if c.name == name]


def find_child(node, name):
    for c in node.children:
        if c.name == name:
            return c
    return None


def find_recursive(node, name):
    out = []
    for c in node.children:
        if c.name == name:
            out.append(c)
        out.extend(find_recursive(c, name))
    return out


def walk(node):
    yield node
    for c in node.children:
        yield from walk(c)


def index_nodes(resource):
    """Return dict: (component_guid) -> {guid, type, name, node} is not trivial
    to compute generically; instead we provide helpers that operate on a
    components[] list."""
    return {}


def components_list(root):
    """Return the list of top-level component instances under 'components'."""
    if not root:
        return []
    comp_block = find_child(root, "components")
    if comp_block is None:
        # some files have components at root via class header; fallback:
        return [c for c in root.children if c.name == "components"]
    return [c for c in comp_block.children if c.name != "__elem__"]