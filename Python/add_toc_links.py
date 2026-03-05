import os
import csv
import tempfile
import subprocess
from pathlib import Path

import fitz

# --------- Config ---------
PDF_DIR = Path(r"C:\Study\Python")
TOC_START_PAGE = 14  # 1-based inclusive
TOC_END_PAGE = 27    # 1-based inclusive
PAGE_OFFSET = -2     # pdf_page = book_page - 2

TESSERACT_EXE = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
TESSDATA_DIR = Path(r"C:\Program Files\Tesseract-OCR\tessdata")
OCR_DPI = 400

BUTTON_TEXT = "??"
BUTTON_FILL = (1.0, 0.95, 0.7)   # light yellow
BUTTON_BORDER = (0.4, 0.3, 0.1)  # brown-ish
BUTTON_TEXT_COLOR = (0, 0, 0)

BUTTON_DPI = 150
BUTTON_MARGIN_PT = 8

OUTPUT_SUFFIX = "_toc_linked"
# --------------------------


def find_pdf_file(pdf_dir: Path) -> Path:
    pdfs = list(pdf_dir.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"No PDF found in {pdf_dir}")
    if len(pdfs) > 1:
        # Prefer the original PDF (exclude outputs)
        originals = [p for p in pdfs if OUTPUT_SUFFIX not in p.stem]
        if len(originals) == 1:
            return originals[0]
        names = ", ".join(p.name for p in pdfs)
        raise RuntimeError(f"Multiple PDFs found in {pdf_dir}: {names}")
    return pdfs[0]


def pick_button_rect(page: fitz.Page) -> fitz.Rect:
    pix = page.get_pixmap(dpi=BUTTON_DPI, colorspace=fitz.csRGB)
    w, h = pix.width, pix.height
    samples = pix.samples
    scale = BUTTON_DPI / 72.0

    # Estimate background color from top-left 30x30 block
    sample_w = min(30, w)
    sample_h = min(30, h)
    total = [0, 0, 0]
    count = 0
    for y in range(sample_h):
        row = y * w * 3
        for x in range(sample_w):
            i = row + x * 3
            total[0] += samples[i]
            total[1] += samples[i + 1]
            total[2] += samples[i + 2]
            count += 1
    bg = [t / count for t in total]
    thr = 18  # tolerance from background

    def rect_has_ink(x0, y0, x1, y1, step=2):
        x0 = max(0, min(x0, w - 1))
        y0 = max(0, min(y0, h - 1))
        x1 = max(0, min(x1, w))
        y1 = max(0, min(y1, h))
        for y in range(y0, y1, step):
            row = y * w * 3
            for x in range(x0, x1, step):
                i = row + x * 3
                r = samples[i]
                g = samples[i + 1]
                b = samples[i + 2]
                if max(abs(r - bg[0]), abs(g - bg[1]), abs(b - bg[2])) > thr:
                    return True
        return False

    candidates = []
    for w_pt in [140, 120, 110, 100, 90, 80, 70, 60]:
        for h_pt in [40, 34, 30, 26, 24, 22, 20]:
            candidates.append((w_pt, h_pt))
    candidates.sort(key=lambda t: t[0] * t[1], reverse=True)

    for w_pt, h_pt in candidates:
        x0_pt = BUTTON_MARGIN_PT
        y0_pt = BUTTON_MARGIN_PT
        x1_pt = x0_pt + w_pt
        y1_pt = y0_pt + h_pt
        x0_px = int(x0_pt * scale)
        y0_px = int(y0_pt * scale)
        x1_px = int(x1_pt * scale)
        y1_px = int(y1_pt * scale)
        if not rect_has_ink(x0_px, y0_px, x1_px, y1_px):
            return fitz.Rect(x0_pt, y0_pt, x1_pt, y1_pt)

    # Fallback
    return fitz.Rect(BUTTON_MARGIN_PT, BUTTON_MARGIN_PT,
                     BUTTON_MARGIN_PT + 80, BUTTON_MARGIN_PT + 24)


def extract_toc_numbers(page: fitz.Page) -> list[tuple[int, fitz.Rect]]:
    if not TESSERACT_EXE.exists():
        raise FileNotFoundError(f"Tesseract not found: {TESSERACT_EXE}")

    pix = page.get_pixmap(dpi=OCR_DPI)
    scale = OCR_DPI / 72.0

    with tempfile.TemporaryDirectory() as td:
        img_path = Path(td) / "page.png"
        out_base = Path(td) / "out"
        pix.save(str(img_path))

        cmd = [
            str(TESSERACT_EXE), str(img_path), str(out_base),
            "--dpi", str(OCR_DPI), "--psm", "6", "-l", "eng", "tsv"
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        tsv_path = Path(td) / "out.tsv"
        entries: list[tuple[int, fitz.Rect]] = []
        with open(tsv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                if row.get("level") != "5":
                    continue
                text = row.get("text", "").strip()
                if not text:
                    continue
                digits = "".join(ch for ch in text if ch.isdigit())
                if not digits:
                    continue
                if not (2 <= len(digits) <= 3):
                    continue
                conf = row.get("conf", "")
                try:
                    conf_val = float(conf) if conf != "" else -1
                except ValueError:
                    conf_val = -1
                if conf_val < 60:
                    continue

                left = float(row.get("left", "0"))
                top = float(row.get("top", "0"))
                width = float(row.get("width", "0"))
                height = float(row.get("height", "0"))

                # Ignore very-left numbers (e.g., section numbers)
                if left < pix.width * 0.30:
                    continue

                x0_pt = left / scale
                y0_pt = top / scale
                x1_pt = (left + width) / scale
                y1_pt = (top + height) / scale
                rect_pt = fitz.Rect(x0_pt, y0_pt, x1_pt, y1_pt)

                entries.append((int(digits), rect_pt))

        # Sort by vertical position (top) and de-dup near-identical boxes
        entries.sort(key=lambda t: (t[1].y0, t[1].x0))
        deduped = []
        seen = set()
        for num, rect in entries:
            key = (num, round(rect.x0, 1), round(rect.y0, 1))
            if key in seen:
                continue
            seen.add(key)
            deduped.append((num, rect))
        return deduped


def main():
    pdf_path = find_pdf_file(PDF_DIR)
    output_path = pdf_path.with_name(pdf_path.stem + OUTPUT_SUFFIX + pdf_path.suffix)

    doc = fitz.open(pdf_path)
    page_count = doc.page_count

    # Pick button rect from the page that corresponds to book page 30
    sample_index = 31  # PDF page 32 (1-based) -> index 31
    if sample_index >= page_count:
        sample_index = 0
    button_rect = pick_button_rect(doc[sample_index])

    toc_index = TOC_START_PAGE - 1
    if toc_index < 0 or toc_index >= page_count:
        raise ValueError("TOC start page out of range")

    # Add back-to-TOC buttons
    for i in range(page_count):
        page = doc[i]
        shape = page.new_shape()
        shape.draw_rect(button_rect)
        shape.finish(color=BUTTON_BORDER, fill=BUTTON_FILL, width=1)
        shape.commit()

        page.insert_textbox(
            button_rect,
            BUTTON_TEXT,
            fontname="helv",
            fontsize=9,
            color=BUTTON_TEXT_COLOR,
            align=fitz.TEXT_ALIGN_CENTER,
        )

        page.insert_link({
            "kind": fitz.LINK_GOTO,
            "from": button_rect,
            "page": toc_index,
            "to": fitz.Point(0, 0),
        })

    # Add TOC number links
    total_links = 0
    skipped = 0
    for p in range(TOC_START_PAGE - 1, TOC_END_PAGE):
        if p < 0 or p >= page_count:
            continue
        page = doc[p]
        entries = extract_toc_numbers(page)
        for num, rect in entries:
            target_index = num + PAGE_OFFSET - 1
            if target_index < 0 or target_index >= page_count:
                skipped += 1
                continue
            # Slight padding to make it easier to click
            pad = 2
            link_rect = fitz.Rect(rect.x0 - pad, rect.y0 - pad, rect.x1 + pad, rect.y1 + pad)
            page.insert_link({
                "kind": fitz.LINK_GOTO,
                "from": link_rect,
                "page": target_index,
                "to": fitz.Point(0, 0),
            })
            total_links += 1

    doc.save(output_path)
    doc.close()

    print(f"Input:  {pdf_path}")
    print(f"Output: {output_path}")
    print(f"Pages: {page_count}")
    print(f"Back-to-TOC button rect: {button_rect}")
    print(f"TOC links created: {total_links}")
    print(f"Skipped (out of range): {skipped}")


if __name__ == "__main__":
    main()
