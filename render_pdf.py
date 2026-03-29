#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
import textwrap
from pathlib import Path


PAGE_WIDTH = 595.0
PAGE_HEIGHT = 842.0
MARGIN_X = 58.0
TOP_MARGIN = 70.0
BOTTOM_MARGIN = 68.0
CONTENT_WIDTH = PAGE_WIDTH - (2 * MARGIN_X)
TITLE_BANNER_HEIGHT = 168.0

TEXT_COLOR = (0.13, 0.15, 0.19)
MUTED_COLOR = (0.42, 0.46, 0.51)
SECTION_COLOR = (0.08, 0.33, 0.56)
SUBSECTION_COLOR = (0.12, 0.41, 0.39)
ACCENT_COLOR = (0.88, 0.60, 0.20)
RULE_COLOR = (0.84, 0.88, 0.90)
PANEL_COLOR = (0.95, 0.97, 0.98)
TITLE_BG = (0.10, 0.33, 0.35)
TITLE_TEXT = (1.00, 1.00, 1.00)
TITLE_MUTED = (0.88, 0.94, 0.94)


def escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def wrap_text(text: str, font_size: float, max_width: float) -> list[str]:
    if not text:
        return [""]
    avg_char_width = max(font_size * 0.50, 1.0)
    width = max(int(max_width / avg_char_width), 20)
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False)


def rgb(color: tuple[float, float, float]) -> str:
    return f"{color[0]:.3f} {color[1]:.3f} {color[2]:.3f}"


def estimate_text_width(text: str, font_size: float) -> float:
    return len(text) * font_size * 0.50


class PDFBuilder:
    def __init__(self) -> None:
        self.objects: list[bytes | None] = []

    def reserve(self) -> int:
        self.objects.append(None)
        return len(self.objects)

    def set_object(self, obj_id: int, data: bytes) -> None:
        self.objects[obj_id - 1] = data

    def add_object(self, data: bytes) -> int:
        obj_id = self.reserve()
        self.set_object(obj_id, data)
        return obj_id

    def build(self, root_id: int, info_id: int | None = None) -> bytes:
        output = bytearray()
        output.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]

        for idx, obj in enumerate(self.objects, start=1):
            if obj is None:
                raise ValueError(f"Object {idx} was reserved but never set")
            offsets.append(len(output))
            output.extend(f"{idx} 0 obj\n".encode("ascii"))
            output.extend(obj)
            output.extend(b"\nendobj\n")

        xref_start = len(output)
        output.extend(f"xref\n0 {len(self.objects) + 1}\n".encode("ascii"))
        output.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

        trailer = f"trailer\n<< /Size {len(self.objects) + 1} /Root {root_id} 0 R"
        if info_id is not None:
            trailer += f" /Info {info_id} 0 R"
        trailer += f" >>\nstartxref\n{xref_start}\n%%EOF\n"
        output.extend(trailer.encode("ascii"))
        return bytes(output)


def parse_markdown_blocks(text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    current: list[str] = []

    def flush() -> None:
        if not current:
            return
        raw = "\n".join(current).strip()
        current.clear()
        if not raw:
            return

        lines = raw.splitlines()
        if len(lines) == 1 and lines[0].startswith("# "):
            blocks.append(("h1", lines[0][2:].strip()))
        elif len(lines) == 1 and lines[0].startswith("## "):
            blocks.append(("h2", lines[0][3:].strip()))
        elif len(lines) == 1 and lines[0].startswith("### "):
            blocks.append(("h3", lines[0][4:].strip()))
        elif all(line.startswith("- ") for line in lines):
            for line in lines:
                blocks.append(("bullet", line[2:].strip()))
        elif all(re.match(r"^\d+\.\s", line) for line in lines):
            for line in lines:
                blocks.append(("number", line.strip()))
        else:
            blocks.append(("para", " ".join(part.strip() for part in lines)))

    for line in text.splitlines():
        if line.strip():
            current.append(line.rstrip())
        else:
            flush()
    flush()
    return blocks


def text_cmd(font: str, size: float, x: float, y: float, text: str, color: tuple[float, float, float]) -> tuple:
    return ("text", font, size, x, y, text, color)


def rect_cmd(x: float, y: float, w: float, h: float, color: tuple[float, float, float]) -> tuple:
    return ("rect", x, y, w, h, color)


def line_cmd(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    width: float,
    color: tuple[float, float, float],
) -> tuple:
    return ("line", x1, y1, x2, y2, width, color)


def layout_blocks(blocks: list[tuple[str, str]]) -> list[list[tuple]]:
    pages: list[list[tuple]] = [[]]
    y = PAGE_HEIGHT - TOP_MARGIN
    title_drawn = False

    def new_page() -> None:
        nonlocal y
        pages.append([])
        y = PAGE_HEIGHT - TOP_MARGIN

    def ensure_space(required: float) -> None:
        nonlocal y
        if y - required < BOTTOM_MARGIN:
            new_page()

    def add_gap(height: float) -> None:
        nonlocal y
        ensure_space(height)
        y -= height

    def add_line(
        font: str,
        size: float,
        text: str,
        color: tuple[float, float, float],
        x: float = MARGIN_X,
        leading: float = 1.45,
    ) -> float:
        nonlocal y
        line_height = size * leading
        ensure_space(line_height)
        y -= line_height
        pages[-1].append(text_cmd(font, size, x, y, text, color))
        return y

    def draw_title_banner(title: str) -> None:
        nonlocal y, title_drawn
        page = pages[-1]
        banner_y = PAGE_HEIGHT - TITLE_BANNER_HEIGHT
        page.append(rect_cmd(0, banner_y, PAGE_WIDTH, TITLE_BANNER_HEIGHT, TITLE_BG))
        title_lines = wrap_text(title, 30, CONTENT_WIDTH - 8)
        title_y = PAGE_HEIGHT - 92
        for line in title_lines:
            page.append(text_cmd("F2", 30, MARGIN_X, title_y, line, TITLE_TEXT))
            title_y -= 34
        y = banner_y - 18
        title_drawn = True

    for block_type, content in blocks:
        if block_type == "h1" and not title_drawn:
            draw_title_banner(content)
            add_gap(8)
            continue

        if block_type == "h1":
            add_gap(10)
            for line in wrap_text(content, 24, CONTENT_WIDTH):
                add_line("F2", 24, line, SECTION_COLOR, leading=1.25)
            add_gap(10)
            continue

        if block_type == "h2":
            add_gap(12)
            heading_lines = wrap_text(content, 16, CONTENT_WIDTH - 8)
            for idx, line in enumerate(heading_lines):
                baseline = add_line("F2", 16, line, SECTION_COLOR, leading=1.25)
                if idx == 0:
                    pages[-1].append(rect_cmd(MARGIN_X - 14, baseline - 2, 6, 18, ACCENT_COLOR))
            pages[-1].append(line_cmd(MARGIN_X, y - 5, PAGE_WIDTH - MARGIN_X, y - 5, 1.1, RULE_COLOR))
            add_gap(12)
            continue

        if block_type == "h3":
            add_gap(8)
            for line in wrap_text(content, 13.5, CONTENT_WIDTH):
                add_line("F2", 13.5, line, SUBSECTION_COLOR, leading=1.25)
            add_gap(8)
            continue

        if block_type == "bullet":
            lines = wrap_text(content, 11.2, CONTENT_WIDTH - 34)
            if lines:
                baseline = add_line("F1", 11.2, lines[0], TEXT_COLOR, x=MARGIN_X + 24, leading=1.50)
                pages[-1].append(rect_cmd(MARGIN_X + 6, baseline + 4, 6, 6, ACCENT_COLOR))
                for line in lines[1:]:
                    add_line("F1", 11.2, line, TEXT_COLOR, x=MARGIN_X + 24, leading=1.50)
            add_gap(2)
            continue

        if block_type == "number":
            lines = wrap_text(content, 11.2, CONTENT_WIDTH - 14)
            if lines:
                add_line("F1", 11.2, lines[0], TEXT_COLOR, x=MARGIN_X + 8, leading=1.50)
                for line in lines[1:]:
                    add_line("F1", 11.2, line, TEXT_COLOR, x=MARGIN_X + 24, leading=1.50)
            add_gap(2)
            continue

        lines = wrap_text(content, 11.2, CONTENT_WIDTH)
        for line in lines:
            add_line("F1", 11.2, line, TEXT_COLOR, leading=1.52)
        add_gap(8)

    return pages


def encode_pages(layout_pages: list[list[tuple]], doc_title: str) -> list[bytes]:
    encoded: list[bytes] = []
    total_pages = len(layout_pages)

    for page_index, page in enumerate(layout_pages, start=1):
        commands: list[str] = []
        commands.append(f"{rgb(PANEL_COLOR)} rg 0 0 {PAGE_WIDTH:.2f} {PAGE_HEIGHT:.2f} re f")

        for cmd in page:
            if cmd[0] == "text":
                _, font, size, x, y, text, color = cmd
                commands.append(
                    f"{rgb(color)} rg BT /{font} {size:.2f} Tf {x:.2f} {y:.2f} Td ({escape_pdf_text(text)}) Tj ET"
                )
            elif cmd[0] == "rect":
                _, x, y, w, h, color = cmd
                commands.append(f"{rgb(color)} rg {x:.2f} {y:.2f} {w:.2f} {h:.2f} re f")
            elif cmd[0] == "line":
                _, x1, y1, x2, y2, width, color = cmd
                commands.append(
                    f"{rgb(color)} RG {width:.2f} w {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S"
                )

        footer_y = 34.0
        commands.append(f"{rgb(RULE_COLOR)} RG 1.00 w {MARGIN_X:.2f} 44.00 m {PAGE_WIDTH - MARGIN_X:.2f} 44.00 l S")
        commands.append(
            f"{rgb(MUTED_COLOR)} rg BT /F3 9.00 Tf {MARGIN_X:.2f} {footer_y:.2f} Td ({escape_pdf_text(doc_title)}) Tj ET"
        )
        page_label = f"Page {page_index} of {total_pages}"
        page_x = PAGE_WIDTH - MARGIN_X - estimate_text_width(page_label, 9.0)
        commands.append(
            f"{rgb(MUTED_COLOR)} rg BT /F3 9.00 Tf {page_x:.2f} {footer_y:.2f} Td ({escape_pdf_text(page_label)}) Tj ET"
        )

        encoded.append("\n".join(commands).encode("latin-1", "replace"))

    return encoded


def render_markdown_to_pdf(input_path: Path, output_path: Path) -> None:
    text = input_path.read_text(encoding="utf-8")
    blocks = parse_markdown_blocks(text)
    layout_pages = layout_blocks(blocks)
    doc_title = next((content for block_type, content in blocks if block_type == "h1"), input_path.stem)
    page_streams = encode_pages(layout_pages, doc_title)

    pdf = PDFBuilder()

    font_regular = pdf.add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    font_bold = pdf.add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    font_italic = pdf.add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique >>")
    pages_id = pdf.reserve()

    page_ids: list[int] = []
    for stream in page_streams:
        stream_obj = pdf.add_object(
            f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"\nendstream"
        )
        page_obj = pdf.add_object(
            (
                "<< /Type /Page /Parent "
                f"{pages_id} 0 R /MediaBox [0 0 {PAGE_WIDTH:.0f} {PAGE_HEIGHT:.0f}] "
                "/Resources << /Font << "
                f"/F1 {font_regular} 0 R /F2 {font_bold} 0 R /F3 {font_italic} 0 R "
                ">> >> "
                f"/Contents {stream_obj} 0 R >>"
            ).encode("ascii")
        )
        page_ids.append(page_obj)

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    pdf.set_object(pages_id, f"<< /Type /Pages /Count {len(page_ids)} /Kids [{kids}] >>".encode("ascii"))
    catalog_id = pdf.add_object(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode("ascii"))
    info_id = pdf.add_object(
        f"<< /Title ({escape_pdf_text(doc_title)}) /Author (Codex) /Producer (Codex PDF Renderer) >>".encode("ascii")
    )

    output_path.write_bytes(pdf.build(catalog_id, info_id=info_id))


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: render_pdf.py <input.md> <output.pdf>", file=sys.stderr)
        return 2

    input_path = Path(sys.argv[1]).resolve()
    output_path = Path(sys.argv[2]).resolve()

    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 1

    render_markdown_to_pdf(input_path, output_path)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
