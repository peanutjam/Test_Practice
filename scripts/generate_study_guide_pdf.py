#!/usr/bin/env python3
"""Generate a printable AZ-900 study guide PDF (concepts only, no practice Q&A)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import ListFlowable, ListItem, PageBreak, Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parent.parent
CONTENT_PATH = ROOT / "app" / "data" / "study_guide_content.json"
LEARN_PATHS = ROOT / "app" / "data" / "learn_az900_paths.json"
OUT_PATH = ROOT / "docs" / "AZ-900-Study-Guide.pdf"


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "GuideTitle",
            parent=base["Title"],
            fontSize=22,
            spaceAfter=14,
        ),
        "h1": ParagraphStyle(
            "GuideH1",
            parent=base["Heading1"],
            fontSize=16,
            spaceBefore=12,
            spaceAfter=8,
            textColor=colors.HexColor("#0078d4"),
        ),
        "h2": ParagraphStyle(
            "GuideH2",
            parent=base["Heading2"],
            fontSize=12,
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "GuideBody",
            parent=base["BodyText"],
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
        ),
        "small": ParagraphStyle(
            "GuideSmall",
            parent=base["BodyText"],
            fontSize=8,
            leading=11,
            textColor=colors.grey,
        ),
    }


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _bullets(story: list, items: list[str], styles: dict) -> None:
    story.append(
        ListFlowable(
            [ListItem(Paragraph(_escape(item), styles["body"])) for item in items],
            bulletType="bullet",
        )
    )


def main() -> None:
    content = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    learn = {}
    if LEARN_PATHS.exists():
        learn = json.loads(LEARN_PATHS.read_text(encoding="utf-8"))

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT_PATH),
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title="AZ-900 Study Guide",
    )
    styles = _styles()
    story: list = []

    overview = content.get("overview", {})
    story.append(Paragraph("AZ-900 Study Guide", styles["title"]))
    story.append(
        Paragraph(
            _escape(
                f"{overview.get('exam', 'Microsoft Azure Fundamentals')} — reference notes generated "
                f"{date.today().isoformat()}. Use the official exam page for authoritative objectives."
            ),
            styles["body"],
        )
    )
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("About the exam", styles["h1"]))
    for key, label in [
        ("audience", "Audience"),
        ("format_notes", "Format"),
        ("official_objectives", "Official objectives"),
    ]:
        if overview.get(key):
            story.append(Paragraph(_escape(label), styles["h2"]))
            story.append(Paragraph(_escape(str(overview[key])), styles["body"]))

    story.append(Spacer(1, 0.1 * inch))
    story.append(
        Paragraph(
            _escape(
                "This guide summarizes concepts only. Use the app's practice modes and Microsoft Learn modules for hands-on review."
            ),
            styles["body"],
        )
    )
    story.append(PageBreak())

    for domain in content.get("domains", []):
        story.append(Paragraph(_escape(domain.get("title", "Domain")), styles["h1"]))
        for section in domain.get("sections", []):
            story.append(Paragraph(_escape(section.get("heading", "")), styles["h2"]))
            for paragraph in section.get("paragraphs", []):
                story.append(Paragraph(_escape(paragraph), styles["body"]))
            if section.get("bullets"):
                _bullets(story, section["bullets"], styles)
            story.append(Spacer(1, 0.06 * inch))
        story.append(PageBreak())

    if learn.get("learning_paths"):
        story.append(Paragraph("Microsoft Learn training map", styles["h1"]))
        story.append(
            Paragraph(
                _escape(
                    "Complete these free learning paths on Learn for coverage aligned with AZ-900 skill areas."
                ),
                styles["body"],
            )
        )
        story.append(Spacer(1, 0.1 * inch))
        for path in learn["learning_paths"]:
            story.append(Paragraph(_escape(path["title"]), styles["h2"]))
            story.append(Paragraph(_escape(path["url"]), styles["small"]))
            for module in path.get("modules", []):
                line = f"{module['title']} — {module.get('duration_minutes', '?')} min"
                story.append(Paragraph(_escape(line), styles["body"]))
                story.append(Paragraph(_escape(module["url"]), styles["small"]))
            story.append(Spacer(1, 0.08 * inch))

    doc.build(story)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
