"""Index Enforce Script class architecture from an offline source checkout.

The intended vanilla source is the pinned official
``BohemiaInteractive/Arma-Reforger-Script-Diff`` checkout created by
``sync_vanilla_scripts.py``. Workbench is not involved.

This is a structural indexer, not a full Enforce compiler. It records class
names, base classes, source locations, and top-level field/method names while
preserving multiple declarations (including ``modded class`` declarations).
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
import os
import re
from typing import Dict, List, Optional, Sequence, Tuple

from sync_vanilla_scripts import DEFAULT_DESTINATION


CLASS_RE = re.compile(
    r"(?m)^[ \t]*(?P<qual>(?:(?:modded|sealed|abstract)\s+)*)"
    r"class\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
    r"\s*(?::\s*(?P<base>[A-Za-z_][A-Za-z0-9_]*))?\s*\{"
)
ATTRIBUTE_PREFIX_RE = re.compile(r"^(?:\s*\[[^\]]*\]\s*)+")
CONTROL_NAMES = {"if", "for", "foreach", "while", "switch", "return", "sizeof"}
IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _strip_comments(text: str) -> str:
    """Remove comments while preserving newlines and quoted strings."""
    out = []
    i = 0
    n = len(text)
    in_string = False
    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if in_string:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_string = False
            i += 1
            continue
        if c == '"':
            in_string = True
            out.append(c)
            i += 1
            continue
        if c == "/" and nxt == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c == "/" and nxt == "*":
            i += 2
            while i < n:
                if text[i] == "\n":
                    out.append("\n")
                if text[i] == "*" and i + 1 < n and text[i + 1] == "/":
                    i += 2
                    break
                i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _matching_brace(text: str, open_index: int) -> Optional[int]:
    depth = 0
    in_string = False
    i = open_index
    while i < len(text):
        c = text[i]
        if in_string:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_string = False
            i += 1
            continue
        if c == '"':
            in_string = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None


def _top_level_statements(body: str) -> List[Tuple[int, str]]:
    """Return class-body declarations/signatures at brace depth zero."""
    rows = []
    depth = 0
    in_string = False
    start = 0
    line = 1
    statement_line = 1
    i = 0
    while i < len(body):
        c = body[i]
        if c == "\n":
            line += 1
        if in_string:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_string = False
            i += 1
            continue
        if c == '"':
            in_string = True
            i += 1
            continue
        if c == "{" and depth == 0:
            statement = " ".join(body[start:i].split())
            if statement:
                rows.append((statement_line, statement + " {"))
            depth = 1
            i += 1
            continue
        if c == "{" and depth > 0:
            depth += 1
            i += 1
            continue
        if c == "}" and depth > 0:
            depth -= 1
            if depth == 0:
                start = i + 1
                statement_line = line
            i += 1
            continue
        if c == ";" and depth == 0:
            statement = " ".join(body[start : i + 1].split())
            if statement:
                rows.append((statement_line, statement))
            start = i + 1
            statement_line = line
        i += 1
    return rows


def _without_attributes(statement: str) -> str:
    """Drop leading Enforce attribute blocks before class-member parsing."""
    previous = None
    current = statement.strip()
    while current != previous:
        previous = current
        current = ATTRIBUTE_PREFIX_RE.sub("", current).strip()
    return current


def _method_name(statement: str) -> Optional[str]:
    statement = _without_attributes(statement)
    if "(" not in statement:
        return None
    prefix = statement.split("(", 1)[0].strip()
    names = IDENT_RE.findall(prefix)
    if not names:
        return None
    name = names[-1]
    if name in CONTROL_NAMES:
        return None
    return name


def _field_name(statement: str) -> Optional[str]:
    statement = _without_attributes(statement)
    if "(" in statement or not statement.rstrip().endswith(";"):
        return None
    declaration = statement.rstrip().rstrip(";").strip()
    if not declaration:
        return None
    left = declaration.split("=", 1)[0].strip()
    names = IDENT_RE.findall(left)
    if len(names) < 2:
        return None
    return names[-1]


def parse_script_classes(text: str, source_file: str) -> List[dict]:
    clean = _strip_comments(text)
    rows = []
    for match in CLASS_RE.finditer(clean):
        open_index = clean.find("{", match.start(), match.end())
        close_index = _matching_brace(clean, open_index)
        if open_index < 0 or close_index is None:
            continue
        qualifiers = [token for token in match.group("qual").split() if token]
        class_line = _line_number(clean, match.start())
        body = clean[open_index + 1 : close_index]
        fields = []
        methods = []
        seen_fields = set()
        seen_methods = set()
        for relative_line, statement in _top_level_statements(body):
            absolute_line = class_line + relative_line - 1
            method = _method_name(statement)
            if method:
                key = (method, statement)
                if key not in seen_methods:
                    seen_methods.add(key)
                    methods.append(
                        {
                            "name": method,
                            "line": absolute_line,
                            "signature": statement,
                        }
                    )
                continue
            field = _field_name(statement)
            if field:
                key = (field, statement)
                if key not in seen_fields:
                    seen_fields.add(key)
                    fields.append(
                        {
                            "name": field,
                            "line": absolute_line,
                            "declaration": statement,
                        }
                    )
        rows.append(
            {
                "name": match.group("name"),
                "base": match.group("base"),
                "qualifiers": qualifiers,
                "modded": "modded" in qualifiers,
                "source_file": source_file.replace("\\", "/"),
                "line": class_line,
                "fields": fields,
                "methods": methods,
            }
        )
    return rows


def _source_marker(source_root: str) -> dict:
    marker_path = os.path.join(source_root, "_wax_source.json")
    if os.path.isfile(marker_path):
        try:
            with open(marker_path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except (OSError, json.JSONDecodeError):
            pass
    return {
        "source": "unmarked_script_root",
        "game_version": None,
        "commit": None,
    }


def build_script_index(source_root: str) -> dict:
    source_root = os.path.abspath(source_root)
    scripts_root = os.path.join(source_root, "scripts")
    if not os.path.isdir(scripts_root):
        raise RuntimeError(f"script source root has no scripts directory: {source_root}")

    declarations = []
    file_count = 0
    parse_failures = []
    for dirpath, _dirs, filenames in os.walk(scripts_root):
        for filename in filenames:
            if not filename.lower().endswith(".c"):
                continue
            file_count += 1
            absolute = os.path.join(dirpath, filename)
            rel = os.path.relpath(absolute, source_root).replace("\\", "/")
            try:
                with open(absolute, "r", encoding="utf-8-sig", errors="replace") as handle:
                    text = handle.read()
                declarations.extend(parse_script_classes(text, rel))
            except OSError as exc:
                parse_failures.append({"source_file": rel, "error": str(exc)})

    by_name: Dict[str, List[int]] = defaultdict(list)
    inheritance = []
    for index, row in enumerate(declarations):
        by_name[row["name"]].append(index)
        if row.get("base"):
            inheritance.append(
                {
                    "class": row["name"],
                    "base": row["base"],
                    "source_file": row["source_file"],
                    "line": row["line"],
                    "modded": row["modded"],
                }
            )

    marker = _source_marker(source_root)
    summary = {
        "source_root": source_root,
        "source": marker,
        "script_file_count": file_count,
        "class_declaration_count": len(declarations),
        "distinct_class_count": len(by_name),
        "inheritance_edge_count": len(inheritance),
        "parse_failure_count": len(parse_failures),
    }
    return {
        "summary": summary,
        "classes": declarations,
        "by_name": dict(sorted(by_name.items())),
        "inheritance": inheritance,
        "parse_failures": parse_failures,
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Index official Enforce script classes")
    parser.add_argument("--source-root", default=DEFAULT_DESTINATION)
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    payload = build_script_index(args.source_root)
    output = args.output or os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "architecture_output",
        "script_class_index.json",
    )
    output = os.path.abspath(output)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)

    print(json.dumps({"output": output, **payload["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
