from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Iterable, Iterator, Optional


RESOURCE_REF_RE = re.compile(r"\{([0-9A-Fa-f]{16})\}([^\"\r\n]+)")

GUID_TOKEN_RE = re.compile(r"^\{([0-9A-Fa-f]{16})\}$")


def parse_guid_token(value: str) -> Optional[str]:
    match = GUID_TOKEN_RE.match(value.strip())
    return match.group(1).upper() if match else None


@dataclass
class Token:
    text: str
    quoted: bool = False


@dataclass
class Property:
    key: str
    values: list[str]
    raw: str
    line: int


@dataclass
class Node:
    header: str
    header_tokens: list[str]
    line: int
    end_line: Optional[int] = None
    properties: list[Property] = field(default_factory=list)
    children: list["Node"] = field(default_factory=list)
    parent: Optional["Node"] = field(default=None, repr=False)

    @property
    def name(self) -> str:
        return self.header_tokens[0] if self.header_tokens else ""

    def walk(self) -> Iterator["Node"]:
        yield self
        for child in self.children:
            yield from child.walk()

    def direct_properties(self, key: str) -> list[Property]:
        return [p for p in self.properties if p.key == key]

    def first_property(self, key: str) -> Optional[Property]:
        for prop in self.properties:
            if prop.key == key:
                return prop
        return None


@dataclass
class Document:
    path: Path
    root: Node
    parse_warnings: list[str] = field(default_factory=list)

    def walk(self) -> Iterator[Node]:
        for child in self.root.children:
            yield from child.walk()

    def find_nodes(self, name: str) -> list[Node]:
        return [node for node in self.walk() if node.name == name]

    def first_node(self, name: str) -> Optional[Node]:
        for node in self.walk():
            if node.name == name:
                return node
        return None


def tokenize_fragment(text: str) -> list[Token]:
    """Small tokenizer for Enfusion text resource line fragments.

    It is intentionally syntax-preserving rather than schema-specific:
    quoted tokens stay whole, ':' and '+' become standalone tokens, and
    unknown identifiers are retained verbatim.
    """
    out: list[Token] = []
    buf: list[str] = []
    quoted = False
    quote_char = ""
    escape = False

    def flush() -> None:
        nonlocal buf
        if buf:
            out.append(Token("".join(buf), False))
            buf = []

    i = 0
    while i < len(text):
        ch = text[i]
        if quoted:
            if escape:
                buf.append(ch)
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote_char:
                out.append(Token("".join(buf), True))
                buf = []
                quoted = False
                quote_char = ""
            else:
                buf.append(ch)
            i += 1
            continue

        if ch in ('"', "'"):
            flush()
            quoted = True
            quote_char = ch
            i += 1
            continue
        if ch.isspace():
            flush()
            i += 1
            continue
        if ch in (":", "+"):
            flush()
            out.append(Token(ch, False))
            i += 1
            continue
        buf.append(ch)
        i += 1

    if quoted:
        out.append(Token("".join(buf), True))
    else:
        flush()
    return out


def strip_comments(line: str, in_block_comment: bool) -> tuple[str, bool]:
    out: list[str] = []
    i = 0
    in_quote = False
    quote_char = ""
    escape = False

    while i < len(line):
        if in_block_comment:
            end = line.find("*/", i)
            if end < 0:
                return "".join(out), True
            i = end + 2
            in_block_comment = False
            continue

        ch = line[i]
        nxt = line[i + 1] if i + 1 < len(line) else ""

        if in_quote:
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote_char:
                in_quote = False
                quote_char = ""
            i += 1
            continue

        if ch in ('"', "'"):
            in_quote = True
            quote_char = ch
            out.append(ch)
            i += 1
            continue

        if ch == "/" and nxt == "/":
            break
        if ch == "/" and nxt == "*":
            in_block_comment = True
            i += 2
            continue

        out.append(ch)
        i += 1

    return "".join(out), in_block_comment


def parse_text(text: str, path: str | Path = "<memory>") -> Document:
    virtual = Node("__document__", ["__document__"], line=0)
    stack: list[Node] = [virtual]
    warnings: list[str] = []
    in_block_comment = False

    for lineno, original in enumerate(text.splitlines(), start=1):
        line, in_block_comment = strip_comments(original, in_block_comment)
        stripped = line.strip()
        if not stripped:
            continue

        while stripped.startswith("}"):
            if len(stack) == 1:
                warnings.append(f"line {lineno}: unmatched closing brace")
            else:
                stack[-1].end_line = lineno
                stack.pop()
            stripped = stripped[1:].strip()
        if not stripped:
            continue

        if stripped.endswith("{"):
            header = stripped[:-1].rstrip()
            tokens = [t.text for t in tokenize_fragment(header)]
            node = Node(header=header, header_tokens=tokens, line=lineno, parent=stack[-1])
            stack[-1].children.append(node)
            stack.append(node)
            continue

        tokens = tokenize_fragment(stripped)
        if not tokens:
            continue
        prop = Property(
            key=tokens[0].text,
            values=[t.text for t in tokens[1:]],
            raw=stripped,
            line=lineno,
        )
        stack[-1].properties.append(prop)

    if in_block_comment:
        warnings.append("unterminated block comment")
    if len(stack) > 1:
        for node in stack[1:]:
            warnings.append(f"line {node.line}: unclosed block '{node.header}'")

    return Document(path=Path(path), root=virtual, parse_warnings=warnings)


def parse_file(path: str | Path, encoding: str = "utf-8") -> Document:
    path = Path(path)
    text = path.read_text(encoding=encoding, errors="replace")
    return parse_text(text, path)


def parse_resource_ref(value: str) -> Optional[dict[str, str]]:
    match = RESOURCE_REF_RE.search(value)
    if not match:
        return None
    return {"guid": match.group(1).upper(), "path": match.group(2).strip()}


def iter_resource_refs(text: str) -> Iterable[dict[str, object]]:
    for lineno, line in enumerate(text.splitlines(), start=1):
        for match in RESOURCE_REF_RE.finditer(line):
            yield {
                "guid": match.group(1).upper(),
                "path": match.group(2).strip(),
                "line": lineno,
            }


def parent_resource(document: Document) -> Optional[dict[str, object]]:
    if not document.root.children:
        return None
    top = document.root.children[0]
    tokens = top.header_tokens
    if ":" not in tokens:
        return None
    colon = tokens.index(":")
    if colon + 1 >= len(tokens):
        return None
    ref = parse_resource_ref(tokens[colon + 1])
    if not ref:
        return None
    return {**ref, "line": top.line, "root_class": tokens[0] if tokens else ""}


def node_value(node: Optional[Node], key: str) -> Optional[object]:
    if node is None:
        return None
    prop = node.first_property(key)
    if prop is None:
        return None
    if len(prop.values) == 0:
        return ""
    if len(prop.values) == 1:
        return coerce_scalar(prop.values[0])
    return [coerce_scalar(v) for v in prop.values]


def coerce_scalar(value: str) -> object:
    low = value.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    try:
        if re.fullmatch(r"[-+]?\d+", value):
            return int(value)
        if re.fullmatch(r"[-+]?(?:\d+\.\d*|\d*\.\d+)(?:[eE][-+]?\d+)?", value):
            return float(value)
    except ValueError:
        pass
    return value
