import re


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

    def mask_pigeon_rings(self, text: str) -> str:
        pattern = re.compile(r'\b[A-Z]{2,}[A-Z\d\-]{10,}\d\b')

        def replacer(match):
            s = match.group()
            return s[:-5] + 'XXXXX'

        return pattern.sub(replacer, text)
