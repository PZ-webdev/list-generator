import pdfkit
import re
import os
import shutil
import platform


def get_wkhtmltopdf_path():
    path = shutil.which('wkhtmltopdf')
    if path:
        return path

    if platform.system() == 'Windows':
        default_win_path = 'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
        if os.path.exists(default_win_path):
            return default_win_path

    raise FileNotFoundError('Nie znaleziono wkhtmltopdf. Dodaj go do PATH lub podaj ręczną ścieżkę.')


wkhtmltopdf_path = get_wkhtmltopdf_path()
config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)


def transform_control_codes(text):
    text = text.replace('\x1b', '[ESC]')
    text = text.replace('[ESC]2', '')
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    text = re.sub(r'\[ESC\]G\[ESC\]W1(.*?)(\[ESC\]H)?\[ESC\]W0', lambda m: f'<h1>{m.group(1).strip()}</h1>', text,
                  flags=re.S)
    text = re.sub(r'\[ESC\]G\[ESC\]W1(.*?)\[ESC\]W0', lambda m: f'<h2>{m.group(1).strip()}</h2>', text, flags=re.S)
    text = re.sub(r'\[ESC\]36(.*?)\[ESC\]H', lambda m: f'<h3>{m.group(1).strip()}</h3>', text, flags=re.S)
    text = text.replace('\f', '<div class="page-break"></div>')
    text = text.replace('[ESC]', '')
    text = text.replace('\r\n', '<br />').replace('\n', '<br />').replace('\r', '<br />')
    return text


def center_only_first_page(html):
    parts = html.split('<div class="page-break"></div>', 1)
    if len(parts) < 2:
        return html
    centered = f'<div class="first-page-center"><div class="first-page-inner">{parts[0]}</div></div>'
    return centered + '<div class="page-break"></div>' + parts[1]


def generate_pdf(file_path):
    with open(file_path, 'r', encoding='cp852') as f:
        raw_content = f.read()

    html_ready = transform_control_codes(raw_content)
    html_ready = center_only_first_page(html_ready)

    # Kluczowy szablon HTML z CSS!
    html_template = f'''
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
    body {{ font-family: 'DejaVu Sans Mono', monospace; font-size: 10pt; }}
    h1 {{ margin-left: 40mm; }}
    h3 {{ margin-left: 40mm; }}
    .page-break {{ page-break-after: always; }}
    .first-page-inner {{ font-size: 12pt; margin-top: -10mm; margin-left: 22mm; line-height: 1.2; }}
    </style>
    </head>
    <body><pre>{html_ready}</pre></body>
    </html>
    '''

    output_path = os.path.splitext(file_path)[0] + '.pdf'
    pdfkit.from_string(html_template, output_path, configuration=config)
    return output_path
