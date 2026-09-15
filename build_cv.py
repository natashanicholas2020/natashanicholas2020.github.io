#!/usr/bin/env python3
"""
build_cv.py - Render a CV YAML file to a PDF that fills a whole number of pages.

This script is the "one command" entry point. You edit YOUR cv.yaml in your
own schema (the format that mirrors the JSON Resume / Jekyll al-folio style)
and this script:

    1. Translates your YAML into RenderCV's expected schema in memory.
    2. Hands the translated YAML to RenderCV.
    3. Auto-tunes RenderCV's design knobs (margins, line spacing, font size,
       inter-entry spacing) until the PDF fits in a target whole-page count.

You never touch the translated form. You never touch RenderCV's CLI directly.
Edit cv.yaml, run this script, get a PDF.

Usage:
    python3 build_cv.py                        # cv.yaml in cwd, smallest fit
    python3 build_cv.py path/to/cv.yaml        # custom input
    python3 build_cv.py -o ~/Desktop/CV.pdf    # custom output
    python3 build_cv.py --pages 2              # force 2-page result

Requires:
    pip install "rendercv[full]" pyyaml pypdf
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional

import yaml


# ---------------------------------------------------------------------------
# YAML translator: YOUR schema -> RenderCV's schema
# ---------------------------------------------------------------------------

def _format_date(value: Any) -> Optional[str]:
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    s = str(value).strip()
    if not s:
        return None
    if s.isdigit() and len(s) == 4:
        return f"{s}-01"
    return s


def _apply_dates(out: dict, start: Any, end: Any) -> None:
    """Write start_date / end_date directly into the entry dict."""
    s = _format_date(start)
    e = _format_date(end)
    if s is not None:
        out["start_date"] = s
    if e is not None:
        out["end_date"] = e
    elif s is not None:
        out["end_date"] = "present"


def _convert_education_entry(item: dict) -> dict:
    out: dict = {}
    if "institution" in item:
        out["institution"] = item["institution"]
    if "area" in item:
        out["area"] = item["area"]
    if "studyType" in item:
        out["degree"] = item["studyType"]
    if "location" in item:
        out["location"] = item["location"]
    _apply_dates(out, item.get("start_date"), item.get("end_date"))
    if item.get("highlights"):
        out["highlights"] = list(item["highlights"])
    return out


def _convert_experience_entry(item: dict) -> dict:
    out: dict = {}
    if "company" in item:
        out["company"] = item["company"]
    if "position" in item:
        out["position"] = item["position"]
    if "location" in item:
        out["location"] = item["location"]
    _apply_dates(out, item.get("start_date"), item.get("end_date"))
    if item.get("highlights"):
        out["highlights"] = list(item["highlights"])
    if item.get("summary"):
        out["summary"] = item["summary"]
    return out


def _convert_project_entry(item: dict) -> dict:
    out: dict = {}
    if "name" in item:
        out["name"] = item["name"]
    if "location" in item:
        out["location"] = item["location"]
    url = item.get("url")
    if isinstance(url, str) and (url.startswith("http://") or url.startswith("https://")):
        out["url"] = url
    _apply_dates(out, item.get("start_date"), item.get("end_date"))
    if item.get("summary"):
        out["summary"] = item["summary"]
    if item.get("highlights"):
        out["highlights"] = list(item["highlights"])
    return out


def _convert_one_line_entry(item: dict) -> dict:
    label = item.get("label") or item.get("name") or ""
    details = (
        item.get("details")
        or item.get("keywords")
        or item.get("summary")
        or ""
    )
    return {"label": label, "details": details}


def _convert_award_entry(item: dict) -> dict:
    title = item.get("title", "")
    parts: list[str] = []
    if item.get("awarder"):
        parts.append(str(item["awarder"]))
    if item.get("date") is not None:
        parts.append(str(item["date"]))
    if item.get("summary"):
        parts.append(str(item["summary"]))
    return {"label": title, "details": " · ".join(parts)}


SECTION_CONVERTERS = {
    "education": _convert_education_entry,
    "experience": _convert_experience_entry,
    "projects": _convert_project_entry,
    "relevant coursework": _convert_one_line_entry,
    "coursework": _convert_one_line_entry,
    "skills": _convert_one_line_entry,
    "languages": _convert_one_line_entry,
    "awards": _convert_award_entry,
}


def translate_to_rendercv(source: dict) -> dict:
    src_cv = source.get("cv", {}) or {}

    out_cv: dict = {}
    if "name" in src_cv:
        out_cv["name"] = src_cv["name"]
    if "location" in src_cv:
        out_cv["location"] = src_cv["location"]
    if "email" in src_cv:
        out_cv["email"] = src_cv["email"]
    if src_cv.get("label"):
        out_cv["headline"] = src_cv["label"]
    if src_cv.get("website"):
        out_cv["website"] = src_cv["website"]
    if src_cv.get("social_networks"):
        out_cv["social_networks"] = list(src_cv["social_networks"])

    out_sections: dict = {}

    summary_text = src_cv.get("summary")
    if isinstance(summary_text, str) and summary_text.strip():
        out_sections["Summary"] = [summary_text.strip()]

    for section_name, items in (src_cv.get("sections", {}) or {}).items():
        if not items:
            continue
        converter = SECTION_CONVERTERS.get(section_name.lower(), _convert_one_line_entry)
        out_sections[section_name] = [converter(item) for item in items]

    out_cv["sections"] = out_sections

    return {
        "cv": out_cv,
        "design": source.get("design") or {
            "theme": "engineeringresumes",
            "page": {"size": "us-letter", "show_footer": False},
            "header": {"connections": {"show_icons": True}},
        },
        "locale": source.get("locale") or {"language": "english"},
    }


# ---------------------------------------------------------------------------
# RenderCV invocation + auto-fit search
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Custom Typst header template
#
# Placed at {work_dir}/engineeringresumes/Header.j2.typ before each render so
# RenderCV picks it up instead of the built-in one.  Changes vs. the default:
#   1. Location is rendered on its own line via a second #headline() call.
#   2. Location is filtered OUT of the #connections() row (identified by the
#      FontAwesome icon name "location-dot" that appears when show_icons=true).
# ---------------------------------------------------------------------------

CUSTOM_HEADER_TEMPLATE = """\
{% if cv.name %}
= {{ cv.name }}
{% endif %}

{% if cv.headline %}
#headline([{{ cv.headline }}])

{% endif %}
{% if cv.location %}
#headline([{{ cv.location }}])

{% endif %}
#connections(
{% for connection in cv._connections %}
{% if "location-dot" not in connection %}
  [{{ connection }}],
{% endif %}
{% endfor %}
)
"""


PRESETS = [
    {  # 0: roomy
        "design.page.top_margin": "0.75in",
        "design.page.bottom_margin": "0.75in",
        "design.page.left_margin": "0.75in",
        "design.page.right_margin": "0.75in",
        "design.typography.font_size.body": "10pt",
        "design.typography.line_spacing": "0.7em",
        "design.sections.space_between_regular_entries": "1.4em",
        "design.section_titles.space_above": "0.5cm",
        "design.section_titles.space_below": "0.3cm",
        "design.header.space_below_name": "0.6cm",
        "design.header.space_below_headline": "0.3cm",
        "design.header.space_below_connections": "0.5cm",
    },
    {  # 1: slightly tighter
        "design.page.top_margin": "0.6in",
        "design.page.bottom_margin": "0.6in",
        "design.page.left_margin": "0.7in",
        "design.page.right_margin": "0.7in",
        "design.typography.font_size.body": "10pt",
        "design.typography.line_spacing": "0.65em",
        "design.sections.space_between_regular_entries": "1.2em",
        "design.section_titles.space_above": "0.4cm",
        "design.section_titles.space_below": "0.25cm",
        "design.header.space_below_name": "0.5cm",
        "design.header.space_below_headline": "0.25cm",
        "design.header.space_below_connections": "0.4cm",
    },
    {  # 2: moderate
        "design.page.top_margin": "0.5in",
        "design.page.bottom_margin": "0.5in",
        "design.page.left_margin": "0.6in",
        "design.page.right_margin": "0.6in",
        "design.typography.font_size.body": "10pt",
        "design.typography.line_spacing": "0.6em",
        "design.sections.space_between_regular_entries": "1.0em",
        "design.section_titles.space_above": "0.35cm",
        "design.section_titles.space_below": "0.2cm",
        "design.header.space_below_name": "0.4cm",
        "design.header.space_below_headline": "0.2cm",
        "design.header.space_below_connections": "0.35cm",
    },
    {  # 3: compact
        "design.page.top_margin": "0.4in",
        "design.page.bottom_margin": "0.4in",
        "design.page.left_margin": "0.55in",
        "design.page.right_margin": "0.55in",
        "design.typography.font_size.body": "9.5pt",
        "design.typography.line_spacing": "0.55em",
        "design.sections.space_between_regular_entries": "0.85em",
        "design.section_titles.space_above": "0.3cm",
        "design.section_titles.space_below": "0.18cm",
        "design.header.space_below_name": "0.35cm",
        "design.header.space_below_headline": "0.18cm",
        "design.header.space_below_connections": "0.3cm",
    },
    {  # 4: tight
        "design.page.top_margin": "0.35in",
        "design.page.bottom_margin": "0.35in",
        "design.page.left_margin": "0.5in",
        "design.page.right_margin": "0.5in",
        "design.typography.font_size.body": "9.5pt",
        "design.typography.line_spacing": "0.5em",
        "design.sections.space_between_regular_entries": "0.7em",
        "design.section_titles.space_above": "0.25cm",
        "design.section_titles.space_below": "0.15cm",
        "design.header.space_below_name": "0.3cm",
        "design.header.space_below_headline": "0.15cm",
        "design.header.space_below_connections": "0.25cm",
    },
    {  # 5: very tight (last resort)
        "design.page.top_margin": "0.3in",
        "design.page.bottom_margin": "0.3in",
        "design.page.left_margin": "0.45in",
        "design.page.right_margin": "0.45in",
        "design.typography.font_size.body": "9pt",
        "design.typography.line_spacing": "0.45em",
        "design.sections.space_between_regular_entries": "0.55em",
        "design.section_titles.space_above": "0.2cm",
        "design.section_titles.space_below": "0.12cm",
        "design.header.space_below_name": "0.25cm",
        "design.header.space_below_headline": "0.12cm",
        "design.header.space_below_connections": "0.2cm",
    },
]


def check_rendercv_installed() -> None:
    if shutil.which("rendercv") is None:
        sys.exit(
            "Error: rendercv is not installed or not on your PATH.\n"
            "Install it with: pip install \"rendercv[full]\""
        )


def count_pdf_pages(pdf_path: Path) -> int:
    try:
        from pypdf import PdfReader
        return len(PdfReader(str(pdf_path)).pages)
    except ImportError:
        pass
    if shutil.which("pdfinfo"):
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)], capture_output=True, text=True, check=True,
        )
        for line in result.stdout.splitlines():
            if line.startswith("Pages:"):
                return int(line.split(":", 1)[1].strip())
    sys.exit(
        "Error: cannot count PDF pages. Install pypdf (`pip install pypdf`) "
        "or poppler-utils (provides `pdfinfo`)."
    )


def render_with_preset(translated_yaml_path: Path, work_dir: Path, preset: dict) -> Path:
    work_dir.mkdir(parents=True, exist_ok=True)

    # Write custom header template so location appears on its own line.
    theme_dir = work_dir / "engineeringresumes"
    theme_dir.mkdir(exist_ok=True)
    (theme_dir / "Header.j2.typ").write_text(CUSTOM_HEADER_TEMPLATE, encoding="utf-8")

    pdf_out = work_dir / "cv.pdf"
    if pdf_out.exists():
        pdf_out.unlink()

    cmd: list[str] = [
        "rendercv", "render",
        str(translated_yaml_path.resolve()),
        "--pdf-path", "cv.pdf",
        "-nomd", "-nohtml", "-nopng",
    ]
    for key, value in preset.items():
        cmd.extend([f"--{key}", value])

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=work_dir)

    auto_out = work_dir / "rendercv_output"
    if auto_out.exists():
        shutil.rmtree(auto_out)

    if result.returncode != 0 or not pdf_out.exists():
        print(result.stdout)
        print(result.stderr)
        sys.exit(f"\nrendercv failed (exit {result.returncode}).")

    return pdf_out


def find_whole_page_fit(
    translated_yaml_path: Path,
    work_dir: Path,
    target_pages: Optional[int],
) -> tuple[Path, int, int]:
    page_counts: list[int] = []
    last_pdf: Optional[Path] = None

    for i, preset in enumerate(PRESETS):
        pdf_path = render_with_preset(translated_yaml_path, work_dir, preset)
        pages = count_pdf_pages(pdf_path)
        page_counts.append(pages)
        last_pdf = pdf_path
        print(f"  preset {i}: {pages} page(s)")
        if target_pages is not None and pages <= target_pages:
            return pdf_path, pages, i

    if target_pages is not None:
        sys.exit(
            f"\nCould not fit content in {target_pages} page(s). "
            f"Page counts tried: {page_counts}."
        )

    min_pages = min(page_counts)
    chosen_idx = page_counts.index(min_pages)
    if chosen_idx != len(PRESETS) - 1:
        pdf_path = render_with_preset(translated_yaml_path, work_dir, PRESETS[chosen_idx])
    else:
        pdf_path = last_pdf  # type: ignore[assignment]
    return pdf_path, min_pages, chosen_idx


def main() -> None:
    parser = argparse.ArgumentParser(description="Render YOUR cv.yaml to a PDF.")
    parser.add_argument("input", type=Path, nargs="?", default=Path("cv.yaml"))
    parser.add_argument("--output", "-o", type=Path, default=None)
    parser.add_argument("--pages", "-p", type=int, default=None)
    parser.add_argument("--keep-build-dir", action="store_true")
    args = parser.parse_args()

    check_rendercv_installed()

    if not args.input.exists():
        sys.exit(f"Input file not found: {args.input}")

    output = args.output or args.input.with_suffix(".pdf")

    print(f"Reading {args.input}")
    with args.input.open("r", encoding="utf-8") as f:
        source = yaml.safe_load(f)
    if not isinstance(source, dict):
        sys.exit(f"{args.input} did not parse as a YAML mapping.")

    translated = translate_to_rendercv(source)

    with tempfile.TemporaryDirectory(prefix="cv_build_") as tmp:
        tmp_path = Path(tmp)
        translated_path = tmp_path / "translated.yaml"
        with translated_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(translated, f, sort_keys=False, allow_unicode=True)

        if args.keep_build_dir:
            shutil.copy2(translated_path, output.parent / "translated.yaml")

        print("Translated to RenderCV schema. Searching for fit:")
        if args.pages is not None:
            print(f"  target: <= {args.pages} page(s)")
        else:
            print("  target: smallest page count that fits")

        pdf_path, pages, preset_idx = find_whole_page_fit(tmp_path / "translated.yaml", tmp_path, args.pages)

        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf_path, output)

    print(f"\nWrote {output} ({pages} page(s), preset {preset_idx})")

    if args.pages is not None and pages < args.pages:
        print(f"Note: content only fills {pages} page(s); you asked for {args.pages}.")


if __name__ == "__main__":
    main()
