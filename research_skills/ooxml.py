"""Normalize Office XML before the authoritative Microsoft SDK validation.

XLSX font children follow schema order. PPT chart axis IDs and references
are repaired together within the SDK-compatible integer range.
These repairs do not replace the shared export validator.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
import zipfile
from io import BytesIO

_SS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
# CT_Font 子元素的合法序列（按 localname）
_FONT_ORDER = ["b", "i", "strike", "condense", "extend", "outline", "shadow",
               "u", "vertAlign", "sz", "color", "name", "family", "charset", "scheme"]
_RANK = {n: i for i, n in enumerate(_FONT_ORDER)}


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _reorder_styles(xml_bytes: bytes) -> bytes | None:
    """重排 styles.xml 中每个 <font> 的子元素到 CT_Font 序。无改动返回 None。"""
    ET.register_namespace("", _SS)
    root = ET.fromstring(xml_bytes)
    fonts = root.find(f"{{{_SS}}}fonts")
    if fonts is None:
        return None
    changed = False
    for font in list(fonts):
        kids = list(font)
        ordered = sorted(kids, key=lambda e: _RANK.get(_local(e.tag), len(_FONT_ORDER)))
        if [id(k) for k in kids] != [id(k) for k in ordered]:
            for k in kids:
                font.remove(k)
            for k in ordered:
                font.append(k)
            changed = True
    if not changed:
        return None
    out = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
    return out


def normalize_xlsx(path: str) -> bool:
    """出厂前规范化：重写 xl/styles.xml 的 font 序。改动返回 True。幂等。"""
    with zipfile.ZipFile(path, "r") as zin:
        names = zin.namelist()
        data = {n: zin.read(n) for n in names}
    if "xl/styles.xml" not in data:
        return False
    fixed = _reorder_styles(data["xl/styles.xml"])
    if fixed is None:
        return False
    data["xl/styles.xml"] = fixed
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for n in names:  # 保持原始部件顺序
            zout.writestr(n, data[n])
    with open(path, "wb") as f:
        f.write(buf.getvalue())
    return True


def normalize_pptx(path) -> bool:
    """Repair invalid chart axis IDs while preserving all axis references."""
    from lxml import etree
    with zipfile.ZipFile(path) as archive:
        entries = [(item, archive.read(item.filename)) for item in archive.infolist()]
    changed, output = False, BytesIO()
    namespace = {"c": "http://schemas.openxmlformats.org/drawingml/2006/chart"}
    with zipfile.ZipFile(output, "w") as archive:
        for item, data in entries:
            if re.fullmatch(r"ppt/charts/chart\d+\.xml", item.filename):
                root = etree.fromstring(data)
                nodes = root.xpath("//c:axId | //c:crossAx", namespaces=namespace)
                values = {int(node.get("val")) for node in nodes}
                used = {value for value in values if 0 <= value <= 2147483647}
                mapping = {}
                for value in sorted(values - used):
                    replacement = value % 2147483648
                    while replacement in used:
                        replacement = (replacement + 1) % 2147483648
                    mapping[value] = replacement
                    used.add(replacement)
                if mapping:
                    for node in nodes:
                        node.set("val", str(mapping.get(int(node.get("val")), int(node.get("val")))))
                    data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
                    changed = True
            archive.writestr(item, data)
    if changed:
        with open(path, "wb") as stream:
            stream.write(output.getvalue())
    return changed
