#!/usr/bin/env python3
"""
Invoice PDF Generator — Phase 2 of the Shop App Improvement Plan.

Reads order JSON files (produced by shopping_app.py checkout) and generates
professional PDF invoices using ReportLab.

Usage:
    # Single order
    python invoice_generator.py ../orders/order_20260625_203726.json

    # Batch — all un-invoiced orders
    python invoice_generator.py --batch

    # Custom output directory
    python invoice_generator.py order.json -o ../my_invoices

    # Open generated PDF (Windows only)
    python invoice_generator.py order.json --open
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# ── Lazy reportlab ─────────────────────────────────────────────────────
# reportlab is imported lazily inside generate_invoice() so that this
# module can be imported from shopping_app.py without reportlab installed.
_REPORTLAB_AVAILABLE = None
_REPORTLAB_ERROR = None


def _check_reportlab():
    global _REPORTLAB_AVAILABLE, _REPORTLAB_ERROR
    if _REPORTLAB_AVAILABLE is True:
        return True
    if _REPORTLAB_AVAILABLE is False:
        raise _REPORTLAB_ERROR
    try:
        import reportlab  # noqa: F401
        _REPORTLAB_AVAILABLE = True
        return True
    except ImportError:
        _REPORTLAB_AVAILABLE = False
        _REPORTLAB_ERROR = ImportError(
            "reportlab is required to generate PDF invoices.\n"
            "Install it with: pip install reportlab"
        )
        raise _REPORTLAB_ERROR


# ── Add project root to sys.path so we can import order module ─────────
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from order import Order, OrderRepository


# ── Paths (relative to this file's grandparent = shop_app/) ──────────────
SHOP_APP_DIR = Path(__file__).resolve().parent.parent
ORDERS_DIR = SHOP_APP_DIR / "orders"
INVOICES_DIR = SHOP_APP_DIR / "invoices"

# ── Shop info (shown on invoice header) ────────────────────────────────
SHOP_NAME = "Kacper's Shop"
SHOP_EMAIL = "shop@kacpers-shop.com"
SHOP_ADDRESS = "123 Main Street, Warsaw, Poland"


# ── Helpers ────────────────────────────────────────────────────────────

def fmt_price(amount: float) -> str:
    """Format a number as a Euro price string."""
    return f"€{amount:,.2f}"


# ═══════════════════════════════════════════════════════════════════════
#  PDF Generation (lazy reportlab import)
# ═══════════════════════════════════════════════════════════════════════

def generate_invoice(order: Order, output_path: Path) -> Path:
    """Generate a PDF invoice from an Order dataclass.

    reportlab is imported lazily here so importing this module from
    shopping_app.py doesn't fail if reportlab isn't installed.
    """
    _check_reportlab()

    # ── Lazy imports ─────────────────────────────────────────────
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        HRFlowable,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    # ── Layout constants ─────────────────────────────────────────
    MARGIN = 2 * cm
    CONTENT_WIDTH = A4[0] - 2 * MARGIN
    BRAND_COLOR = colors.HexColor("#1a1a2e")
    ACCENT_COLOR = colors.HexColor("#e94560")
    HEADER_BG = colors.HexColor("#16213e")
    EVEN_ROW = colors.HexColor("#f8f9fa")

    # ── Styles ───────────────────────────────────────────────────
    base = getSampleStyleSheet()
    s = {
        "title": ParagraphStyle(
            "InvoiceTitle", parent=base["Title"],
            fontSize=22, textColor=BRAND_COLOR, spaceAfter=2,
        ),
        "invoice_label": ParagraphStyle(
            "InvoiceLabel", parent=base["Normal"],
            fontSize=18, textColor=ACCENT_COLOR, alignment=2,
        ),
        "section": ParagraphStyle(
            "SectionHeader", parent=base["Heading2"],
            fontSize=13, textColor=HEADER_BG, spaceBefore=10, spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "BodyText9", parent=base["Normal"], fontSize=9, leading=13,
        ),
        "body_bold": ParagraphStyle(
            "BodyBold9", parent=base["Normal"],
            fontSize=9, leading=13, fontName="Helvetica-Bold",
        ),
        "th": ParagraphStyle(
            "TableHeader", fontName="Helvetica-Bold",
            fontSize=9, textColor=colors.white, leading=12,
        ),
        "tc": ParagraphStyle(
            "TableCell", fontSize=9, leading=12,
        ),
        "footer": ParagraphStyle(
            "Footer", fontSize=8, textColor=colors.grey,
            alignment=1, leading=10,
        ),
        "right": ParagraphStyle(
            "RightAlign", fontSize=10, alignment=2, leading=13,
        ),
    }

    # ── Build document ───────────────────────────────────────────
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
    )

    elements: list = []

    # ── Header ───────────────────────────────────────────────────
    order_date = datetime.fromisoformat(order.created_at).strftime("%B %d, %Y")
    order_id = order.order_id

    header = Table(
        [
            [
                Paragraph(f"<b>{SHOP_NAME}</b>", s["title"]),
                Paragraph("<b>INVOICE</b>", s["invoice_label"]),
            ],
            [
                Paragraph(f"Order #{order_id}", s["body_bold"]),
                Paragraph(f"Date: {order_date}", s["right"]),
            ],
        ],
        colWidths=[CONTENT_WIDTH / 2] * 2,
    )
    header.setStyle(TableStyle([
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(header)
    elements.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT_COLOR, spaceAfter=12))

    # ── Customer info ────────────────────────────────────────────
    c = order.customer
    elements.append(Paragraph("<b>Bill To:</b>", s["section"]))
    elements.append(Paragraph(c.name, s["body"]))
    elements.append(Paragraph(c.email, s["body"]))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(SHOP_ADDRESS, s["body"]))
    elements.append(Spacer(1, 14))

    # ── Items table ──────────────────────────────────────────────
    elements.append(Paragraph("<b>Order Details</b>", s["section"]))
    elements.append(Spacer(1, 4))

    col_widths = [6.5 * cm, 1.8 * cm, 3 * cm, 2.2 * cm, 3 * cm]
    data = [[Paragraph(h, s["th"]) for h in ("Item", "Qty", "Unit Price", "Weight", "Total")]]

    for item in order.items:
        line_total = item.quantity * item.unit_cost
        data.append([
            Paragraph(item.name, s["tc"]),
            Paragraph(str(item.quantity), s["tc"]),
            Paragraph(fmt_price(item.unit_cost), s["tc"]),
            Paragraph(f"{item.unit_weight} kg", s["tc"]),
            Paragraph(fmt_price(line_total), s["tc"]),
        ])

    items_table = Table(data, colWidths=col_widths, repeatRows=1)
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, EVEN_ROW]),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 16))

    # ── Totals ───────────────────────────────────────────────────
    t = order.totals
    total_rows = [
        [Paragraph("Subtotal:", s["body_bold"]), Paragraph(fmt_price(t.subtotal), s["body"])],
        [Paragraph("Shipping:", s["body_bold"]), Paragraph(fmt_price(t.shipping_cost), s["body"])],
        [Paragraph("Total Weight:", s["body_bold"]), Paragraph(f"{t.total_weight:.2f} kg", s["body"])],
        [Paragraph("<b>Grand Total:</b>", s["th"]), Paragraph(f"<b>{fmt_price(t.grand_total)}</b>", s["th"])],
    ]

    totals_tbl = Table(total_rows, colWidths=[8 * cm, 6 * cm])
    totals_tbl.setStyle(TableStyle([
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("LINEABOVE", (0, -1), (-1, -1), 2, HEADER_BG),
        ("LINEBELOW", (0, -2), (-1, -2), 0.5, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    wrapper = Table([[totals_tbl]], colWidths=[CONTENT_WIDTH])
    wrapper.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "RIGHT")]))
    elements.append(wrapper)
    elements.append(Spacer(1, 30))

    # ── Footer ───────────────────────────────────────────────────
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey, spaceAfter=8))
    elements.append(Paragraph(
        "Thank you for your purchase!<br/>"
        f"For questions, contact: {SHOP_EMAIL}",
        s["footer"],
    ))

    # ── Build PDF ────────────────────────────────────────────────
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.build(elements)
    return output_path


# ═══════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Generate PDF invoices from order JSON files.",
        epilog=(
            "Examples:\n"
            "  %(prog)s ../orders/order_20260625_203726.json\n"
            "  %(prog)s --batch\n"
            "  %(prog)s --batch -o ../my_invoices\n"
            "  %(prog)s order.json --open"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "order_file",
        nargs="?",
        help="Path to an order JSON file (e.g., orders/order_20260101_120000.json).",
    )
    parser.add_argument(
        "--batch", "-b",
        action="store_true",
        help="Process all un-invoiced orders.",
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=str(INVOICES_DIR),
        help=f"Output directory for generated PDFs (default: {INVOICES_DIR}).",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the generated PDF file(s) after creation (Windows only).",
    )

    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    repo = OrderRepository(ORDERS_DIR)

    if args.batch:
        uninvoiced = repo.find_uninvoiced(INVOICES_DIR)
        if not uninvoiced:
            print("[OK] All orders already invoiced. Nothing to do.")
            return
        print(f"[ORDERS] Found {len(uninvoiced)} un-invoiced order(s)...")
        order_list = uninvoiced
    elif args.order_file:
        path = Path(args.order_file)
        if not path.exists():
            print(f"[ERROR] File not found: {path}")
            sys.exit(1)
        order_list = [repo.load_by_path(path)]
    else:
        parser.print_help()
        sys.exit(1)

    # Generate PDFs
    generated: List[Path] = []
    for order in order_list:
        try:
            pdf_name = f"invoice_{order.order_id}.pdf"
            pdf_path = output_dir / pdf_name
            generate_invoice(order, pdf_path)
            generated.append(pdf_path)
            print(f"  [OK]  {pdf_name}")
        except Exception as exc:
            print(f"  [FAIL]  order_{order.order_id}: {exc}")

    if generated and args.open:
        for pdf in generated:
            try:
                os.startfile(pdf)  # Windows only
            except AttributeError:
                print("[WARN] --open is only supported on Windows.")


if __name__ == "__main__":
    main()
