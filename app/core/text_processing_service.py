import re
import os
from typing import List

from app.dto.settings_dto import SettingsDTO
from app.utils.file_utils import read_file_cp852
from app.utils.logger import log_info


class TextProcessingService:
    def transform_control_codes(self, text: str) -> str:
        text = re.sub(r'\x1b36\x1bH', '', text)
        text = re.sub(r'\x1b36', '', text)

        text = text.replace('\x1b', '[ESC]')
        text = text.replace('[ESC]2', '')
        text = text.replace('<', '&lt;').replace('>', '&gt;')

        text = re.sub(r'\[ESC\]G\[ESC\]W1(.*?)(\[ESC\]H)?\[ESC\]W0', lambda m: f'<h1>{m.group(1).strip()}</h1>', text, flags=re.S)
        text = re.sub(r'\[ESC\]G\[ESC\]W1(.*?)\[ESC\]W0', lambda m: f'<h2>{m.group(1).strip()}</h2>', text, flags=re.S)
        text = re.sub(r'\[ESC\]36(.*?)\[ESC\]H', lambda m: f'<h3>{m.group(1).strip()}</h3>', text, flags=re.S)

        text = text.replace('\f', '<div class="page-break"></div>')
        text = text.replace('[ESC]', '')
        text = text.replace('\r\n', '<br />').replace('\n', '<br />').replace('\r', '<br />')

        text = re.sub(r'(<div class="page-break"></div>\s*)+$', '', text, flags=re.S)
        text = re.sub(r'(<div class="page-break"></div><br />\s*)+$', '', text, flags=re.S)

        return text

    def center_only_first_page(self, html: str) -> str:
        parts = html.split('<div class="page-break"></div>', 1)
        if len(parts) < 2:
            return html
        centered = f'<div class="first-page-center"><div class="first-page-inner">{parts[0]}</div></div>'
        return centered + '<div class="page-break"></div>' + parts[1]

    def append_rating_files_to_content(self, content: str, base_dir: str, filenames: List[str]) -> str:
        for filename in filenames:
            additional_path = os.path.join(base_dir, filename)
            if os.path.exists(additional_path):
                log_info(f'Dołączam plik {additional_path} do pliku')
                additional_content = read_file_cp852(additional_path)
                content += '\n' + additional_content
        return content

    def mask_pigeon_rings(self, text: str) -> str:
        mask = 'XXXXX'

        try:
            settings = SettingsDTO.from_json()
            if settings.ring_mask.strip():
                mask = settings.ring_mask.strip()
        except Exception:
            pass

        pattern = re.compile(r'\b[A-Z]{2,}[A-Z\d\-]{10,}\d\b')

        def replacer(match):
            s = match.group()
            return s[:-len(mask)] + mask

        return pattern.sub(replacer, text)
