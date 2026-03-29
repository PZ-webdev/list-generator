import os
from typing import List

from app.core.text_processing_service import TextProcessingService
from app.dto.branch import Branch
from app.utils.file_utils import read_file_utf8
from app.utils.resource_helper import resource_path


class StartClockPdfService:
    """Dedicated DRLSTZEG pipeline isolated from result PDF generation."""

    def __init__(self):
        self.text_service = TextProcessingService()

    def build_html(self, raw_content: str) -> str:
        normalized = self._normalize_comp_column(raw_content)
        normalized = self._normalize_continuations(normalized)
        normalized = self._normalize_duplicate_headers(normalized)
        normalized = self._ensure_page_break_between_breeders(normalized)
        normalized = self._strip_emphasis_codes(normalized)

        html_ready = self.text_service.transform_control_codes(normalized)
        html_ready = self._format_header_blocks(html_ready)
        html_ready = self._wrap_page_segments(html_ready)

        template_path = resource_path('app/templates/start_clock_template.html')
        html_template = read_file_utf8(template_path)
        return html_template.replace('{{ content }}', html_ready)

    def get_output_filename(self, branch: Branch, output_dir: str) -> str:
        return os.path.join(output_dir, 'LISTA STARTOWO-ZEGAROWA.pdf')

    def _strip_emphasis_codes(self, text: str) -> str:
        import re
        text = re.sub(r'\x1bG\x1bW1', '', text)
        text = re.sub(r'\x1bH\x1bW0', '', text)
        text = re.sub(r'\x1bW1', '', text)
        text = re.sub(r'\x1bW0', '', text)
        text = re.sub(r'\x1bG', '', text)
        text = re.sub(r'\x1bH', '', text)
        return text

    def _format_header_blocks(self, html: str) -> str:
        import re

        html = re.sub(
            r'LISTA STARTOWO-ZEGAROWA',
            '<span class="start-clock-title">LISTA STARTOWO-ZEGAROWA</span>',
            html,
        )

        html = re.sub(
            r'(Hodowca\s*-\s*)([^<\n\r]+?)(\s{2,}Sek\.nr)',
            lambda m: f'{m.group(1)}<span class="breeder-strong">{m.group(2).strip()}</span>  {m.group(3).lstrip()}',
            html,
        )

        return html

    def _normalize_comp_column(self, text: str) -> str:
        import re

        lines = text.splitlines(keepends=True)
        out: List[str] = []
        pattern = re.compile(r'\x1bG\x1bW1\s*(\d+)\x1bH\x1bW0')

        for line in lines:
            if self._looks_like_data_row(line):
                line = pattern.sub(lambda m: str(m.group(1)).center(6), line)
            out.append(line)

        return ''.join(out)

    def _normalize_continuations(self, text: str) -> str:
        lines = text.splitlines(keepends=True)
        out: List[str] = []
        i = 0

        while i < len(lines):
            line = lines[i]

            if self._is_continuation_chunk(lines[i:i + 4]):
                if out and out[-1].startswith('└'):
                    out[-1] = self._convert_bottom_border_to_middle(out[-1])
                i += 4
                continue

            if line in ('\f', '\x0c'):
                next_chunk = lines[i + 1:i + 5]
                if self._is_continuation_chunk(next_chunk):
                    if out and out[-1].startswith('└'):
                        out[-1] = self._convert_bottom_border_to_middle(out[-1])
                    i += 5
                    continue

            out.append(line)
            i += 1

        return ''.join(out)

    def _normalize_duplicate_headers(self, text: str) -> str:
        lines = text.splitlines(keepends=True)
        out: List[str] = []
        i = 0

        while i < len(lines):
            chunk = lines[i:i + 5]
            if self._is_duplicate_header_chunk(chunk):
                out.extend([chunk[0], chunk[1], chunk[4]])
                i += 5
                continue

            out.append(lines[i])
            i += 1

        return ''.join(out)

    def _ensure_page_break_between_breeders(self, text: str) -> str:
        lines = text.splitlines(keepends=True)
        out: List[str] = []

        for i, line in enumerate(lines):
            out.append(line)

            if 'podpis kom.' not in line.lower():
                continue

            lookahead = ''.join(lines[i + 1:i + 8])
            if ('\f' in lookahead) or ('\x0c' in lookahead):
                continue
            if 'Hodowca -' in lookahead:
                out.append('\f')

        return ''.join(out)

    def _wrap_page_segments(self, html: str) -> str:
        parts = html.split('<div class="page-break"></div>')
        wrapped = []
        for part in parts:
            wrapped.append(f'<div class="page"><div class="page-inner">{part}</div></div>')
        return ''.join(wrapped)

    def _is_continuation_chunk(self, lines: List[str]) -> bool:
        if len(lines) < 4:
            return False

        breeder_line = lines[0].strip()
        return (
            breeder_line != ''
            and self._looks_like_continuation_breeder_line(breeder_line)
            and self._is_box_border_line(lines[1], 'top')
            and self._looks_like_table_header_line(lines[2])
            and self._is_box_border_line(lines[3], 'mid')
        )

    def _is_duplicate_header_chunk(self, lines: List[str]) -> bool:
        if len(lines) < 5:
            return False

        return (
            self._is_box_border_line(lines[0], 'top')
            and self._looks_like_table_header_line(lines[1])
            and self._is_box_border_line(lines[2], 'mid')
            and lines[1] == lines[3]
            and self._is_box_border_line(lines[4], 'mid')
        )

    def _convert_bottom_border_to_middle(self, line: str) -> str:
        return (
            line.replace('└', '├')
            .replace('┴', '┼')
            .replace('┘', '┤')
        )

    def _looks_like_continuation_breeder_line(self, line: str) -> bool:
        import re
        return re.match(r'^\d+\s*-\s+\S.*$', line) is not None

    def _looks_like_table_header_line(self, line: str) -> bool:
        stripped = line.strip()
        if not (stripped.startswith('│') and stripped.endswith('│')):
            return False
        return stripped.count('│') >= 6

    def _is_box_border_line(self, line: str, border_type: str) -> bool:
        stripped = line.strip()
        if border_type == 'top':
            return stripped.startswith('┌') and stripped.endswith('┐')
        if border_type == 'mid':
            return stripped.startswith('├') and stripped.endswith('┤')
        return False

    def _looks_like_data_row(self, line: str) -> bool:
        stripped = line.strip()
        return stripped.startswith('│') and stripped.endswith('│') and stripped.count('│') >= 8
