"""Shared drop-data model, traversal, and generated-JavaScript I/O.

Monster and box tables use the same entry and cell protocol. A cell keeps the
legacy compact shape for zero or one drop and expands to ``{"items": [...]}``
when the source contains multiple independent drops. Consumers must traverse
cells through this module instead of depending on either representation.
"""

import json
import os
import re
import tempfile
from pathlib import Path


VERSIONS = ("bb", "dc", "ngc")
LANGUAGES = ("en", "ja", "zh")
DROP_TYPES = ("monsters", "boxes")

_ASSIGNMENT_RE = re.compile(
    r"(.*?window\.DROP_DATA_(?P<language>EN|JA|ZH)\s*=\s*)"
    r"(?P<data>\{.*\})(?P<suffix>\s*;\s*)$",
    re.DOTALL,
)


def make_drop_cell(drops):
    """Build the compact compatible representation for one cell."""
    drops = list(drops)
    if not drops:
        return {"item": "", "rate": ""}
    if len(drops) == 1:
        return drops[0]
    return {"items": drops}


def iter_cell_drops(cell):
    """Yield every drop mapping stored in one section-ID cell."""
    items = cell.get("items")
    if items is None:
        yield cell
    else:
        yield from items


def cell_shape_errors(cell):
    """Return structural errors for one compact single/multi drop cell."""
    if not isinstance(cell, dict):
        return [f"cell must be an object, got {type(cell).__name__}"]

    items = cell.get("items")
    if items is None:
        drops = [cell]
    else:
        if not isinstance(items, list):
            return ["cell.items must be an array"]
        if len(items) < 2:
            return ["cell.items must contain at least two drops"]
        if "item" in cell or "rate" in cell:
            return ["multi-item cell cannot also contain item/rate"]
        drops = items

    errors = []
    for index, drop in enumerate(drops):
        label = f"drop[{index}]"
        if not isinstance(drop, dict):
            errors.append(f"{label} must be an object")
            continue
        if "items" in drop:
            errors.append(f"{label} cannot contain nested items")
        if not isinstance(drop.get("item"), str):
            errors.append(f"{label}.item must be a string")
        if not isinstance(drop.get("rate"), str):
            errors.append(f"{label}.rate must be a string")
        if "ss" in drop and not isinstance(drop["ss"], bool):
            errors.append(f"{label}.ss must be a boolean")
    return errors


def iter_entry_drops(entry):
    """Yield every drop mapping in an entry, preserving cell/item order."""
    for cell in entry.get("drops", []):
        yield from iter_cell_drops(cell)


def iter_data_entries(data, *, drop_types=DROP_TYPES):
    """Yield every entry in stable difficulty/type/episode order."""
    for difficulty_data in data.get("data", {}).values():
        for drop_type in drop_types:
            for entries in difficulty_data.get(drop_type, {}).values():
                yield from entries


def iter_data_drops(data, *, drop_types=DROP_TYPES):
    """Yield every drop in a dataset through the shared cell protocol."""
    for entry in iter_data_entries(data, drop_types=drop_types):
        yield from iter_entry_drops(entry)


def load_framed_js(path, language=None):
    """Load a generated data file and preserve its JavaScript framing."""
    path = Path(path)
    match = _ASSIGNMENT_RE.fullmatch(path.read_text(encoding="utf-8"))
    if not match:
        raise ValueError(f"Cannot parse generated drop data: {path}")

    actual_language = match.group("language").lower()
    if language is not None and actual_language != language.lower():
        raise ValueError(
            f"{path}: expected {language.upper()} data, "
            f"found {actual_language.upper()}"
        )
    return (
        match.group(1),
        json.loads(match.group("data")),
        match.group("suffix"),
    )


def load_js_data(path, language=None):
    """Load only the JSON-compatible object from a generated data file."""
    return load_framed_js(path, language)[1]


def _atomic_write_text(path, content):
    """Atomically replace a generated file in its destination directory."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(content)
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def write_json(path, data):
    """Atomically write a UTF-8 JSON document."""
    _atomic_write_text(
        path,
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    )


def dump_framed_js(path, prefix, data, suffix):
    """Write data while preserving the existing JavaScript framing."""
    _atomic_write_text(
        path,
        prefix + json.dumps(data, ensure_ascii=False, indent=2) + suffix,
    )


def write_generated_js(path, data, *, language, generator, source):
    """Write a complete generated drop-data JavaScript file."""
    content = (
        f"// Auto-generated by {generator}\n"
        f"// {source}\n"
        f"window.DROP_DATA_{language.upper()} = "
        f"{json.dumps(data, ensure_ascii=False, indent=2)};\n"
    )
    _atomic_write_text(path, content)
    return len(content)
