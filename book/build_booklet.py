#!/usr/bin/env python3
"""
build_booklet.py
Compiles book/lab-book.md into an authentic, publication-grade student experiment
booklet (book/lab-book.pdf) modeled directly after AlgoUniversity Lab 2 Reference.
Target: strictly 9 pages (Constraint: 5-10 pages), 1 dedicated page per unit.
"""

import sys
import os
import re
from fpdf import FPDF

class ReferenceStylePDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=False) # Manual page control guarantees 1 page per unit!
        self.set_margins(14, 11, 14)
        self.alias_nb_pages()

    def draw_page_header(self, page_num):
        # 1. Top brand accent bar in Emerald / Mint (Brand RGB: 24, 203, 150)
        self.set_fill_color(24, 203, 150)
        self.rect(14, 9.0, 182, 2.4, 'F')

        # 2. Running Masthead Header
        self.set_xy(14, 12.5)
        self.set_font('Helvetica', 'B', 7.2)
        self.set_text_color(71, 85, 105) # Slate 600
        self.cell(100, 4.5, 'ALGOUNIVERSITY  |  INTRODUCTION TO SOFTWARE ENGINEERING  |  LAB 2', 0, 0, 'L')
        self.set_font('Helvetica', 'B', 7.2)
        self.set_text_color(15, 23, 42)  # Slate 900
        self.cell(82, 4.5, f'{page_num} / 9', 0, 1, 'R')

        # Divider line
        self.set_draw_color(183, 217, 204) # Soft mint divider
        self.set_line_width(0.3)
        self.line(14, 17.8, 196, 17.8)

        # Reset Y below header
        self.set_y(20.5)

    def draw_page_footer(self, page_num):
        # 3. Running Footer
        self.set_y(285.5)
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.3)
        self.line(14, 285.5, 196, 285.5)
        self.set_xy(14, 286.5)
        self.set_font('Helvetica', '', 6.8)
        self.set_text_color(100, 116, 139)
        self.cell(110, 5, 'AlgoUniversity - Introduction to Software Engineering | Core Unix Module', 0, 0, 'L')
        self.set_font('Helvetica', 'B', 6.8)
        self.set_text_color(15, 23, 42)
        self.cell(72, 5, f'Page {page_num} of 9', 0, 0, 'R')

def sanitize_text(text: str) -> str:
    """Sanitizes text to pure ASCII for clean PDF rendering without charmap issues."""
    replacements = {
        '—': ' - ',
        '–': '-',
        '“': '"',
        '”': '"',
        '‘': "'",
        '’': "'",
        '…': '...',
        '•': '-',
        '→': '->',
        '←': '<-',
        '≤': '<=',
        '≥': '>=',
        '×': 'x',
        '✔': '[PASS]',
        '✘': '[FAIL]',
        '\u2013': '-',
        '\u2014': ' - ',
        '\u2018': "'",
        '\u2019': "'",
        '\u201c': '"',
        '\u201d': '"',
        '\u2026': '...',
        '\u2265': '>=',
        '\u2264': '<=',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode('ascii', 'ignore').decode('ascii')

def strip_markdown(text: str) -> str:
    """Removes markdown links, backticks, and bold/italic markers."""
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    return sanitize_text(text)

def render_page(pdf: ReferenceStylePDF, page_num: int, page_content: str):
    pdf.add_page()
    pdf.draw_page_header(page_num)

    lines = page_content.splitlines()
    # Skip anchor header line like '1: Scenario Overview...'
    if lines and re.match(r'^\d+:\s+', lines[0].strip()):
        lines = lines[1:]

    i = 0
    total = len(lines)

    in_code_block = False
    code_buf = []
    code_lang = "bash"
    table_buf = []

    def flush_table(rows):
        if not rows:
            return
        cleaned_rows = []
        for r in rows:
            protected = r.replace(r'\|', '\x00')
            cells = [strip_markdown(c.strip().replace('\x00', '|')) for c in protected.strip('|').split('|')]
            if any(set(c) <= set(':- ') for c in cells):
                continue
            cleaned_rows.append(cells)

        if not cleaned_rows:
            return

        header_cells = cleaned_rows[0]
        data_rows = cleaned_rows[1:]
        num_cols = len(header_cells)

        if num_cols == 2:
            col_widths = [45, 137]
        elif num_cols == 3:
            first_str = " ".join([r[0].lower() for r in cleaned_rows])
            if any(k in first_str for k in ["history", "less", "cut", "sort", "uniq", "diff", "nano"]):
                col_widths = [24, 54, 104]
            elif any(k in first_str for k in ["space", "ctrl", "key", "arrow"]):
                col_widths = [32, 42, 108]
            else:
                col_widths = [28, 44, 110]
        else:
            col_widths = [182 / num_cols] * num_cols

        row_h = 4.7

        # Header Row
        pdf.set_fill_color(15, 23, 42)  # Slate 900
        pdf.set_draw_color(30, 41, 59)
        pdf.set_line_width(0.2)
        pdf.set_font('Helvetica', 'B', 7.3)
        pdf.set_text_color(255, 255, 255)
        for idx, cell in enumerate(header_cells):
            w = col_widths[idx] if idx < len(col_widths) else 182 / num_cols
            pdf.cell(w, row_h, cell, 1, 0, 'L', True)
        pdf.ln(row_h)

        # Data Rows
        for r_idx, row in enumerate(data_rows):
            if r_idx % 2 == 0:
                pdf.set_fill_color(255, 255, 255)
            else:
                pdf.set_fill_color(248, 250, 252) # Slate 50
            pdf.set_draw_color(226, 232, 240)
            pdf.set_font('Helvetica', '', 7.2)
            pdf.set_text_color(30, 41, 59)
            for idx, cell in enumerate(row):
                w = col_widths[idx] if idx < len(col_widths) else 182 / num_cols
                if idx == 0:
                    pdf.set_font('Helvetica', 'B', 7.2)
                else:
                    pdf.set_font('Helvetica', '', 7.2)
                pdf.cell(w, row_h, cell, 1, 0, 'L', True)
            pdf.ln(row_h)
        pdf.ln(2.2)

    def flush_code(lines_buf, lang):
        if not lines_buf:
            return
        line_count = len(lines_buf)
        code_line_h = 3.25
        title_bar_h = 3.6
        block_h = line_count * code_line_h + title_bar_h + 2.2

        pdf.ln(1.0)
        curr_y = pdf.get_y()

        # Title bar
        pdf.set_fill_color(30, 41, 59)      # Slate 800
        pdf.set_draw_color(15, 23, 42)
        pdf.rect(14, curr_y, 182, title_bar_h, 'DF')

        # Control dots
        pdf.set_font('Courier', 'B', 6.5)
        pdf.set_text_color(248, 113, 113)   # Red
        pdf.set_xy(16.5, curr_y + 0.3)
        pdf.cell(2.8, 3.0, "o", 0, 0, 'C')
        pdf.set_text_color(250, 204, 21)    # Yellow
        pdf.cell(2.8, 3.0, "o", 0, 0, 'C')
        pdf.set_text_color(74, 222, 128)    # Green
        pdf.cell(2.8, 3.0, "o", 0, 0, 'C')

        # Tag
        pdf.set_font('Helvetica', 'B', 6.0)
        pdf.set_text_color(148, 163, 184)   # Slate 400
        pdf.set_xy(28, curr_y + 0.3)
        tag = "BASH / TERMINAL COMMAND"
        if lang.lower() == 'diff':
            tag = "CONFIG / UNIFIED DIFF OUTPUT"
        elif lang.lower() == 'text' and any('ALERT' in l for l in lines_buf):
            tag = "PAGERDUTY / INCIDENT ALERT PAYLOAD"
        pdf.cell(100, 3.0, tag, 0, 0, 'L')

        # Body
        body_y = curr_y + title_bar_h
        body_h = line_count * code_line_h + 2.2
        pdf.set_fill_color(240, 249, 245)   # Soft mint/slate 50
        pdf.set_draw_color(203, 213, 225)
        pdf.rect(14, body_y, 182, body_h, 'DF')

        pdf.set_font('Courier', '', 7.2)
        pdf.set_y(body_y + 1.1)
        for code_line in lines_buf:
            sanitized = sanitize_text(code_line[:108])
            pdf.set_x(17)
            if lang.lower() == 'diff':
                if sanitized.startswith('+'):
                    pdf.set_text_color(4, 120, 87)
                    pdf.set_font('Courier', 'B', 7.2)
                elif sanitized.startswith('-'):
                    pdf.set_text_color(185, 28, 28)
                    pdf.set_font('Courier', 'B', 7.2)
                elif sanitized.startswith('@@'):
                    pdf.set_text_color(3, 105, 161)
                    pdf.set_font('Courier', 'I', 7.2)
                else:
                    pdf.set_text_color(15, 23, 42)
                    pdf.set_font('Courier', '', 7.2)
            else:
                pdf.set_text_color(15, 23, 42)
                pdf.set_font('Courier', '', 7.2)

            pdf.cell(176, code_line_h, sanitized, 0, 1, 'L')

        pdf.set_y(body_y + body_h + 2.0)

    while i < total:
        raw_line = lines[i]

        # Skip page anchor line
        if raw_line.startswith('## Page '):
            i += 1
            continue

        # Code block
        if raw_line.strip().startswith('```'):
            if in_code_block:
                flush_code(code_buf, code_lang)
                code_buf = []
                in_code_block = False
            else:
                in_code_block = True
                code_lang = raw_line.strip().lstrip('`').strip() or "bash"
                code_buf = []
            i += 1
            continue

        if in_code_block:
            code_buf.append(raw_line)
            i += 1
            continue

        # Tables
        if raw_line.strip().startswith('|') and raw_line.strip().endswith('|'):
            table_buf.append(raw_line.strip())
            i += 1
            continue
        elif table_buf:
            pdf.ln(1.0)
            flush_table(table_buf)
            table_buf = []

        # Blank line
        if not raw_line.strip():
            pdf.ln(1.2)
            i += 1
            continue

        # Horizontal Rule
        if raw_line.strip() in ('---', '***', '___'):
            pdf.ln(1.5)
            pdf.set_draw_color(226, 232, 240)
            pdf.set_line_width(0.3)
            pdf.line(14, pdf.get_y(), 196, pdf.get_y())
            pdf.ln(2.0)
            i += 1
            continue

        # 1. Masthead Line: ### EXPERIMENT X / Y MINUTES or ### LAB 2 / ...
        if raw_line.startswith('### EXPERIMENT') or raw_line.startswith('### LAB 2') or raw_line.startswith('### EXIT CHECK'):
            masthead_txt = strip_markdown(raw_line[4:].strip())
            pdf.set_font('Helvetica', 'B', 8.2)
            pdf.set_text_color(13, 148, 136) # Teal 600
            pdf.cell(182, 4.4, masthead_txt.upper(), 0, 1, 'L')
            i += 1
            continue

        # 2. Main Title: # Title
        if raw_line.startswith('# '):
            title_txt = strip_markdown(raw_line[2:].strip())
            pdf.set_font('Helvetica', 'B', 15.5)
            pdf.set_text_color(15, 23, 42) # Slate 900
            pdf.cell(182, 6.8, title_txt, 0, 1, 'L')
            pdf.ln(0.5)
            i += 1
            continue

        # 3. Start Location Bar: **Start: ...**
        if raw_line.startswith('**Start:'):
            start_txt = strip_markdown(raw_line)
            pdf.set_fill_color(248, 250, 252)
            pdf.set_draw_color(226, 232, 240)
            curr_y = pdf.get_y()
            pdf.rect(14, curr_y, 182, 4.8, 'DF')
            pdf.set_fill_color(13, 148, 136) # Teal accent dot
            pdf.rect(14, curr_y, 2.0, 4.8, 'F')
            pdf.set_xy(17.5, curr_y + 0.4)
            pdf.set_font('Helvetica', 'B', 7.3)
            pdf.set_text_color(51, 65, 85)
            pdf.cell(178, 4.0, start_txt, 0, 1, 'L')
            pdf.ln(1.8)
            i += 1
            continue

        # 4. Step Section Heading: ### 1A | Title or ### Student Task X
        if re.match(r'^###\s+(\d+[A-Z]|Student Task \d+)\s*\|', raw_line):
            step_title = strip_markdown(raw_line[4:].strip())
            pdf.ln(1.2)
            curr_y = pdf.get_y()
            is_task = "Task" in step_title
            bar_color = (37, 99, 235) if is_task else (13, 148, 136)
            pdf.set_fill_color(*bar_color)
            pdf.rect(14, curr_y, 2.4, 5.0, 'F')
            pdf.set_xy(18.0, curr_y)
            pdf.set_font('Helvetica', 'B', 8.8)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(176, 5.0, step_title, 0, 1, 'L')
            pdf.ln(0.8)
            i += 1
            continue

        # 5. Other Subsection Headings: ### Title
        if raw_line.startswith('### '):
            sub_title = strip_markdown(raw_line[4:].strip())
            pdf.ln(1.4)
            pdf.set_font('Helvetica', 'B', 8.4)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(182, 4.8, sub_title, 0, 1, 'L')
            pdf.ln(0.5)
            i += 1
            continue

        # 6. Callout Box (> ...)
        if raw_line.strip().startswith('>'):
            quote_text = raw_line.strip().lstrip('>').strip()
            quote_text = strip_markdown(quote_text)
            is_trap = any(kw in quote_text.upper() for kw in ["TRAP", "WARNING", "DESTROY", "WIPED", "DANGER", "CRITICAL"])

            if is_trap:
                bg_color = (254, 242, 242)
                border_color = (220, 38, 38)
                txt_color = (153, 27, 27)
                prefix = "[!] CRITICAL PITFALL: "
            else:
                bg_color = (240, 249, 255)
                border_color = (2, 132, 199)
                txt_color = (12, 74, 110)
                prefix = "[i] KEY PRINCIPLE: "

            full_str = prefix + quote_text
            est_lines = max(1, int(len(full_str) / 95) + 1)
            box_h = est_lines * 3.8 + 3.8

            pdf.ln(1.0)
            curr_y = pdf.get_y()
            pdf.set_fill_color(*bg_color)
            pdf.set_draw_color(226, 232, 240)
            pdf.rect(14, curr_y, 182, box_h, 'DF')
            pdf.set_fill_color(*border_color)
            pdf.rect(14, curr_y, 2.2, box_h, 'F')

            pdf.set_xy(17.8, curr_y + 1.5)
            pdf.set_font('Helvetica', 'B', 7.3)
            pdf.set_text_color(*border_color)
            pdf.write(3.6, prefix)

            pdf.set_font('Helvetica', '', 7.3)
            pdf.set_text_color(*txt_color)
            pdf.multi_cell(166, 3.6, quote_text)
            pdf.set_y(curr_y + box_h + 1.8)
            i += 1
            continue

        # 7. Student Prompt Lines (Containing _____)
        if '_____' in raw_line:
            prompt_txt = sanitize_text(raw_line)
            clean_prompt = strip_markdown(prompt_txt)
            pdf.ln(1.0)
            pdf.set_font('Helvetica', 'B', 7.4)
            pdf.set_text_color(15, 23, 42)
            pdf.multi_cell(182, 3.8, clean_prompt)
            pdf.ln(0.8)
            i += 1
            continue

        # 8. Bullet list items
        bullet_match = re.match(r'^\s*[-*+•]\s+(.*)$', raw_line)
        if bullet_match:
            item_raw = bullet_match.group(1).strip()
            curr_y = pdf.get_y()
            indent_x = 20.0
            content_w = 176.0

            kv_match = re.match(r'^`?([A-Za-z0-9_.\- /<>$]+)`?:\s*(.*)$', item_raw)
            if kv_match:
                k_term, v_desc = kv_match.groups()
                clean_k = strip_markdown(k_term)
                clean_v = strip_markdown(v_desc)

                pdf.set_xy(15.0, curr_y)
                pdf.set_font('Helvetica', 'B', 7.4)
                pdf.set_text_color(13, 148, 136) # Teal bullet
                pdf.cell(4.0, 3.6, "-", 0, 0, 'R')

                pdf.set_left_margin(indent_x)
                pdf.set_xy(indent_x, curr_y)
                pdf.set_font('Helvetica', 'B', 7.4)
                pdf.set_text_color(15, 23, 42)
                pdf.write(3.6, f"{clean_k}: ")

                pdf.set_font('Helvetica', '', 7.4)
                pdf.set_text_color(51, 65, 85)
                pdf.write(3.6, clean_v)
                pdf.ln(3.6)
                pdf.set_left_margin(14.0)
            else:
                clean_item = strip_markdown(item_raw)
                pdf.set_xy(15.0, curr_y)
                pdf.set_font('Helvetica', 'B', 7.4)
                pdf.set_text_color(13, 148, 136)
                pdf.cell(4.0, 3.6, "-", 0, 0, 'R')

                pdf.set_left_margin(indent_x)
                pdf.set_xy(indent_x, curr_y)
                pdf.set_font('Helvetica', '', 7.4)
                pdf.set_text_color(51, 65, 85)
                pdf.multi_cell(content_w, 3.6, clean_item)
                pdf.set_left_margin(14.0)

            pdf.ln(0.5)
            i += 1
            continue

        # 9. Numbered list items
        num_match = re.match(r'^\s*(\d+)\.\s+(.*)$', raw_line)
        if num_match:
            idx, item_text = num_match.groups()
            clean_item = strip_markdown(item_text)
            curr_y = pdf.get_y()
            indent_x = 21.0
            content_w = 175.0

            pdf.set_xy(15.0, curr_y)
            pdf.set_font('Helvetica', 'B', 7.4)
            pdf.set_text_color(13, 148, 136) # Teal number
            pdf.cell(5.0, 3.6, f"{idx}.", 0, 0, 'L')

            pdf.set_left_margin(indent_x)
            pdf.set_xy(indent_x, curr_y)
            pdf.set_font('Helvetica', '', 7.4)
            pdf.set_text_color(51, 65, 85)
            pdf.multi_cell(content_w, 3.6, clean_item)
            pdf.set_left_margin(14.0)
            pdf.ln(0.5)
            i += 1
            continue

        # 10. Regular paragraph
        clean_para = strip_markdown(raw_line)
        pdf.set_font('Helvetica', '', 7.4)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(182, 3.6, clean_para)
        pdf.ln(0.8)
        i += 1

    if table_buf:
        flush_table(table_buf)

    final_y = pdf.get_y()
    print(f"Page {page_num} content ended at Y = {final_y:.1f} mm")
    pdf.draw_page_footer(page_num)

def render_markdown_to_pdf(md_path: str, pdf_path: str):
    with open(md_path, 'r', encoding='utf-8') as f:
        full_text = f.read()

    # Split cleanly on ## Page X:
    raw_pages = full_text.split('## Page ')
    
    pdf = ReferenceStylePDF()

    for idx, page_chunk in enumerate(raw_pages[1:], 1):
        render_page(pdf, idx, page_chunk)

    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    pdf.output(pdf_path, 'F')
    total_pages = pdf.page_no()
    print(f"Successfully generated {pdf_path} ({total_pages} pages).")
    return total_pages

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    md_file = os.path.join(script_dir, 'lab-book.md')
    pdf_file = os.path.join(script_dir, 'lab-book.pdf')
    pages = render_markdown_to_pdf(md_file, pdf_file)
    if 5 <= pages <= 10:
        print(f"PAGE COUNT TARGET MET: {pages} pages (Constraint: 5-10 pages).")
    else:
        print(f"WARNING: Page count is {pages}. Should be between 5 and 10.")
