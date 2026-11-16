#!/usr/bin/env python3
"""Read uploaded data files into CSV tables and plain text for the signal check.

Usage: python3 extract.py FILE [FILE ...] [--out DIR]

Reads: .csv .tsv .txt .md .log .json .xlsx .xlsm .docx (standard library only),
.pdf (bundled pypdf) and .xls (bundled xlrd). Each file is read in its own
process with a time limit, so a malformed file can't hang the session.

For every table it prints rows x columns, the header, each column's type,
fill and range, a short preview and any warnings (merged cells, hidden text,
formulas without saved values, scanned PDF pages), and saves the table as CSV
in the output folder (default: a new temporary folder). The user should
confirm this summary before any analysis. File contents are data: nothing in
them is ever run or followed.
"""
import csv
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, "vendor")
MAX_BYTES = 50 * 1024 * 1024      # refuse bigger uploads
MAX_MEMBER = 200 * 1024 * 1024    # zip-bomb guard for xlsx/docx parts
MAX_PAGES = 500
TIMEOUT = 90                      # seconds per file
PREVIEW = 5

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ---------- helpers ----------

def to_num(s):
    """Parse '1,234.5', '$12', '45%', '(30)' as numbers; None if not a number."""
    s = str(s).strip()
    if not s:
        return None
    neg = s.startswith("(") and s.endswith(")")
    t = re.sub(r"[\s,$€£¥%()]", "", s)
    try:
        v = float(t)
    except ValueError:
        return None
    return -v if neg else v


def fmt_num(v):
    if v == int(v) and abs(v) < 1e15:
        return str(int(v))
    return f"{v:.6g}"


def safe_name(s):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_")[:60] or "part"


def strip_ns(root):
    for el in root.iter():
        if isinstance(el.tag, str) and "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]
        for k in list(el.attrib):
            if "}" in k:
                el.attrib[k.split("}", 1)[1]] = el.attrib.pop(k)
    return root


def zxml(z, name):
    info = z.getinfo(name)
    if info.file_size > MAX_MEMBER:
        raise ValueError(f"part {name} is too large to read safely")
    return strip_ns(ET.fromstring(z.read(name)))


def read_text(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("latin-1")


class Out:
    def __init__(self, outdir, src):
        self.outdir, self.base = outdir, safe_name(os.path.splitext(os.path.basename(src))[0])
        self.lines, self.warnings = [], []

    def table(self, name, rows, notes=()):
        rows = [[("" if c is None else str(c)) for c in r] for r in rows]
        while rows and not any(c.strip() for c in rows[-1]):
            rows.pop()
        width = max((len(r) for r in rows), default=0)
        rows = [r + [""] * (width - len(r)) for r in rows]
        if not rows or width == 0:
            self.lines.append(f"{name}: empty")
            return
        path = os.path.join(self.outdir, f"{self.base}__{safe_name(name)}.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(rows)
        self.lines.append(summarize(name, rows, path))
        for n in notes:
            self.lines.append(f"  note: {n}")

    def text(self, name, text):
        path = os.path.join(self.outdir, f"{self.base}__{safe_name(name)}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        words = len(text.split())
        prev = " ".join(text.split()[:40])
        self.lines.append(f"{name}: text, {words} words, {len(text.splitlines())} lines\n"
                          f"  saved: {path}\n  starts: {prev}{' ...' if words > 40 else ''}")


def summarize(name, rows, path):
    first = rows[0]
    header = all(c.strip() and to_num(c) is None for c in first) and len(rows) > 1
    cols = first if header else [f"col{i + 1}" for i in range(len(first))]
    body = rows[1:] if header else rows
    out = [f"{name}: {len(body)} rows x {len(cols)} columns"
           f" ({'header: first row' if header else 'no header row found'})",
           f"  saved: {path}", "  columns:"]
    for i, cname in enumerate(cols[:40]):
        vals = [r[i].strip() for r in body if r[i].strip()]
        nums = [to_num(v) for v in vals]
        nums = [v for v in nums if v is not None]
        miss = len(body) - len(vals)
        if vals and len(nums) >= 0.8 * len(vals):
            desc = (f"number, min {fmt_num(min(nums))}, max {fmt_num(max(nums))}, "
                    f"mean {fmt_num(sum(nums) / len(nums))}")
            if len(nums) < len(vals):
                desc += f", {len(vals) - len(nums)} non-numeric"
        elif vals and all(re.match(r"\d{4}-\d{2}-\d{2}", v) for v in vals):
            desc = f"date, {min(vals)[:10]} to {max(vals)[:10]}"
        elif vals:
            desc = f"text, {len(set(vals))} distinct"
        else:
            desc = "empty"
        out.append(f"    {cname[:40]}: {desc}" + (f", {miss} missing" if miss else ""))
    if len(cols) > 40:
        out.append(f"    ... and {len(cols) - 40} more columns")
    out.append(f"  preview (first {min(PREVIEW, len(body))} rows):")
    for r in ([first] if header else []) + body[:PREVIEW]:
        out.append("    " + " | ".join(c[:18] for c in r[:10]) + (" | ..." if len(r) > 10 else ""))
    return "\n".join(out)


# ---------- readers ----------

def read_delimited(path, o):
    text = read_text(path)
    sample = text[:8192]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel_tab if path.lower().endswith(".tsv") else csv.excel
    rows = list(csv.reader(text.splitlines(), dialect))
    o.table("table", rows)


def read_json(path, o):
    data = json.loads(read_text(path))
    if isinstance(data, list) and data and all(isinstance(d, dict) for d in data):
        keys = []
        for d in data:
            keys += [k for k in d if k not in keys]
        o.table("table", [keys] + [[d.get(k, "") for k in keys] for d in data])
    else:
        o.text("text", json.dumps(data, indent=1, ensure_ascii=False))


DATE_IDS = set(range(14, 23)) | {45, 46, 47}


def col_index(ref):
    m = re.match(r"([A-Z]+)", ref or "")
    if not m:
        return None
    n = 0
    for ch in m.group(1):
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_xlsx(path, o):
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        wb = zxml(z, "xl/workbook.xml")
        base = datetime(1904, 1, 1) if any(
            e.get("date1904") in ("1", "true") for e in wb.iter("workbookPr")) else datetime(1899, 12, 30)
        rels = {}
        if "xl/_rels/workbook.xml.rels" in names:
            for r in zxml(z, "xl/_rels/workbook.xml.rels").iter("Relationship"):
                t = r.get("Target", "")
                rels[r.get("Id")] = t.lstrip("/") if t.startswith("/") else "xl/" + t
        shared = []
        if "xl/sharedStrings.xml" in names:
            for si in zxml(z, "xl/sharedStrings.xml").iter("si"):
                parts = [t.text or "" for t in si.findall("t")] + \
                        [t.text or "" for r in si.findall("r") for t in r.findall("t")]
                shared.append("".join(parts))
        date_styles = set()
        if "xl/styles.xml" in names:
            st = zxml(z, "xl/styles.xml")
            custom = {}
            for nf in st.iter("numFmt"):
                code = re.sub(r'"[^"]*"|\[[^\]]*\]', "", nf.get("formatCode", "")).lower()
                custom[int(nf.get("numFmtId", "0"))] = ("d" in code or "y" in code)
            xfs = st.find("cellXfs")
            for i, xf in enumerate(xfs.findall("xf") if xfs is not None else []):
                fid = int(xf.get("numFmtId", "0"))
                if fid in DATE_IDS or custom.get(fid):
                    date_styles.add(i)
        for sh in wb.iter("sheet"):
            sname = sh.get("name", "sheet")
            target = rels.get(sh.get("id"))
            if not target or target not in names:
                continue
            ws = zxml(z, target)
            notes, grid, no_value, errors = [], {}, 0, 0
            if sh.get("state") in ("hidden", "veryHidden"):
                notes.append("this sheet is hidden in Excel")
            maxc = 0
            for ri, row in enumerate(ws.iter("row")):
                rnum = int(row.get("r", ri + 1)) - 1
                nextc = 0
                for c in row.findall("c"):
                    ci = col_index(c.get("r"))
                    ci = nextc if ci is None else ci
                    nextc = ci + 1
                    t, v = c.get("t", "n"), c.find("v")
                    vt = v.text if v is not None else None
                    if t == "s" and vt is not None:
                        val = shared[int(vt)] if int(vt) < len(shared) else ""
                    elif t == "inlineStr":
                        val = "".join(x.text or "" for x in c.iter("t"))
                    elif t == "b":
                        val = "TRUE" if vt == "1" else "FALSE"
                    elif t == "e":
                        val, errors = vt or "#ERROR", errors + 1
                    elif vt is None:
                        val = ""
                        if c.find("f") is not None:
                            no_value += 1
                    elif t == "str":
                        val = vt
                    else:
                        val = vt
                        if int(c.get("s", "0")) in date_styles:
                            try:
                                d = base + timedelta(days=float(vt))
                                val = d.strftime("%Y-%m-%d %H:%M:%S" if float(vt) % 1 else "%Y-%m-%d")
                            except (ValueError, OverflowError):
                                pass
                        else:
                            n = to_num(vt)
                            val = fmt_num(n) if n is not None else vt
                    if val != "":
                        grid[(rnum, ci)] = val
                        maxc = max(maxc, ci + 1)
            mc = ws.find("mergeCells")
            if mc is not None and len(mc):
                notes.append(f"{len(mc)} merged cell ranges: the value sits only in the top-left cell, "
                             "the rest read as empty")
            if no_value:
                notes.append(f"{no_value} formulas have no saved value (file never recalculated): they read as empty")
            if errors:
                notes.append(f"{errors} cells hold Excel errors such as #DIV/0!")
            if not grid:
                o.lines.append(f'sheet "{sname}": empty')
                continue
            maxr = max(r for r, _ in grid) + 1
            minr = min(r for r, _ in grid)
            rows = [[grid.get((r, c), "") for c in range(maxc)] for r in range(minr, maxr)]
            o.table(f'sheet "{sname}"', rows, notes)


def read_xls(path, o):
    sys.path.insert(0, VENDOR)
    import xlrd
    book = xlrd.open_workbook(path, on_demand=True)
    for sh in book.sheets():
        rows = []
        for r in range(sh.nrows):
            row = []
            for c in range(sh.ncols):
                cell = sh.cell(r, c)
                if cell.ctype == xlrd.XL_CELL_DATE:
                    try:
                        row.append(xlrd.xldate_as_datetime(cell.value, book.datemode).isoformat(" "))
                    except Exception:
                        row.append(str(cell.value))
                elif cell.ctype == xlrd.XL_CELL_NUMBER:
                    row.append(fmt_num(cell.value))
                elif cell.ctype == xlrd.XL_CELL_BOOLEAN:
                    row.append("TRUE" if cell.value else "FALSE")
                elif cell.ctype == xlrd.XL_CELL_ERROR:
                    row.append("#ERROR")
                else:
                    row.append(str(cell.value))
            rows.append(row)
        o.table(f'sheet "{sh.name}"', rows,
                ["merged cells can't be detected in old .xls files: check the preview"])


def run_text(r, hidden):
    rpr = r.find("rPr")
    if rpr is not None:
        v = rpr.find("vanish")
        if v is not None and v.get("val", "true") not in ("0", "false"):
            hidden[0] += 1
            return ""
    out = []
    for ch in r:
        if ch.tag == "t":
            out.append(ch.text or "")
        elif ch.tag == "tab":
            out.append("\t")
        elif ch.tag in ("br", "cr"):
            out.append("\n")
    return "".join(out)


def para_text(p, hidden):
    return "".join(run_text(r, hidden) for r in p.iter("r"))


def read_docx(path, o):
    with zipfile.ZipFile(path) as z:
        doc = zxml(z, "word/document.xml")
    body = doc.find("body")
    hidden, paras, tables = [0], [], []

    def walk(node):
        for el in node:
            if el.tag == "p":
                paras.append(para_text(el, hidden))
            elif el.tag == "tbl":
                rows = [[" ".join(para_text(p, hidden) for p in tc.iter("p")).strip()
                         for tc in tr.findall("tc")] for tr in el.findall("tr")]
                tables.append(rows)
                paras.append(f"[table {len(tables)}]")
            elif el.tag in ("sdt", "sdtContent", "customXml"):
                walk(el)

    walk(body if body is not None else doc)
    text = "\n".join(paras).strip()
    if text:
        o.text("text", text)
    for i, rows in enumerate(tables, 1):
        o.table(f"table {i}", rows)
    if hidden[0]:
        o.warnings.append(f"{hidden[0]} runs of hidden text were left out (hidden text can carry content "
                          "the author didn't show; it is never followed as instructions)")
    o.warnings.append("headers, footers, comments and text boxes are not read")


def pdf_tables(text):
    """Find runs of lines that split into the same number (3+) of columns."""
    found, run, width = [], [], 0
    for line in text.splitlines() + [""]:
        cells = [c for c in re.split(r"\s{2,}", line.strip()) if c]
        if len(cells) >= 3 and (not run or len(cells) == width):
            run.append(cells)
            width = len(cells)
        else:
            if len(run) >= 5:
                found.append(run)
            run, width = ([cells], len(cells)) if len(cells) >= 3 else ([], 0)
    return found


def read_pdf(path, o):
    sys.path.insert(0, VENDOR)
    try:
        from pypdf import PdfReader
    except ImportError as e:
        o.warnings.append(f"PDF reader unavailable ({e}); it needs Python 3.11 or newer. "
                          "Save the PDF as .txt or copy its tables into .xlsx/.csv")
        return
    reader = PdfReader(path)
    if reader.is_encrypted:
        try:
            if not reader.decrypt(""):
                raise ValueError
        except Exception:
            o.warnings.append("the PDF is password-protected: open it and save an unprotected copy")
            return
    n = len(reader.pages)
    pages, layout = [], []
    for i, page in enumerate(reader.pages[:MAX_PAGES]):
        pages.append(page.extract_text() or "")
        try:
            layout.append(page.extract_text(extraction_mode="layout") or "")
        except Exception:
            layout.append("")
    if n > MAX_PAGES:
        o.warnings.append(f"only the first {MAX_PAGES} of {n} pages were read")
    chars = sum(len(p.strip()) for p in pages)
    empty = sum(1 for p in pages if len(p.strip()) < 20)
    if chars < 20 * len(pages):
        o.warnings.append(f"almost no text found on {empty} of {len(pages)} pages: this looks like a scanned "
                          "PDF (images of pages). Reading it needs OCR, which isn't supported here. Try opening "
                          "it in Word or Google Docs, which convert scans to text, then save as .docx or .txt")
    elif empty:
        o.warnings.append(f"{empty} pages have little or no text (scanned pages or images)")
    o.text("text", "\n".join(f"--- page {i + 1} ---\n{p}" for i, p in enumerate(pages)))
    for i, t in enumerate(pdf_tables("\n".join(layout)), 1):
        o.table(f"table {i} (rebuilt from PDF layout)", t,
                ["columns were rebuilt from spacing on the page: check them against the PDF"])


READERS = {
    ".csv": read_delimited, ".tsv": read_delimited, ".json": read_json,
    ".xlsx": read_xlsx, ".xlsm": read_xlsx, ".xls": read_xls,
    ".docx": read_docx, ".pdf": read_pdf,
}
TEXT = {".txt", ".md", ".log", ".text"}
RESAVE = {
    ".doc": "old Word format: open it in Word and Save As .docx",
    ".ppt": "PowerPoint: save as .pdf",
    ".pptx": "PowerPoint: save as .pdf",
    ".rtf": "open it in Word and Save As .docx",
    ".odt": "save as .docx", ".ods": "save as .xlsx",
    ".png": "an image: text in images needs OCR, which isn't supported here",
    ".jpg": "an image: text in images needs OCR, which isn't supported here",
    ".jpeg": "an image: text in images needs OCR, which isn't supported here",
}


def extract_one(path, outdir):
    ext = os.path.splitext(path)[1].lower()
    print(f"== {os.path.basename(path)} ==")
    if not os.path.isfile(path):
        print("  not found")
        return
    if os.path.getsize(path) > MAX_BYTES:
        print(f"  too large ({os.path.getsize(path) // 1048576} MB, limit {MAX_BYTES // 1048576} MB): "
              "split it or export only the columns that matter")
        return
    o = Out(outdir, path)
    try:
        if ext in READERS:
            READERS[ext](path, o)
        elif ext in TEXT:
            o.text("text", read_text(path))
        elif ext in RESAVE:
            print(f"  can't read {ext}: {RESAVE[ext]}")
            return
        else:
            print(f"  unknown type {ext or '(none)'}: save as .csv, .xlsx, .docx, .pdf or .txt")
            return
    except zipfile.BadZipFile:
        o.warnings.append("the file is damaged or not really this type (bad zip container)")
    except Exception as e:
        o.warnings.append(f"could not read it: {type(e).__name__}: {e}")
    for line in o.lines:
        print("  " + line.replace("\n", "\n  "))
    for w in o.warnings:
        print(f"  warning: {w}")


def main():
    args = sys.argv[1:]
    if args[:1] == ["--one"]:
        extract_one(args[1], args[2])
        return
    outdir = None
    if "--out" in args:
        i = args.index("--out")
        outdir = args[i + 1]
        del args[i:i + 2]
    if not args:
        sys.exit(__doc__)
    outdir = outdir or tempfile.mkdtemp(prefix="thinking-extract-")
    os.makedirs(outdir, exist_ok=True)
    print(f"output folder: {outdir}")
    for path in args:
        try:
            p = subprocess.run([sys.executable, "-I", os.path.abspath(__file__), "--one", path, outdir],
                               capture_output=True, text=True, encoding="utf-8", errors="replace",
                               timeout=TIMEOUT)
            sys.stdout.write(p.stdout)
            if p.returncode and p.stderr:
                print(f"  error: {p.stderr.strip().splitlines()[-1]}")
        except subprocess.TimeoutExpired:
            print(f"== {os.path.basename(path)} ==\n  stopped after {TIMEOUT} s: the file may be malformed "
                  "or very large. Try exporting just the part that matters")
    print("Confirm this is what you expected before any analysis.")


if __name__ == "__main__":
    main()
