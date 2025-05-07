import pdfkit
import re
import os
import shutil
import platform

from utils.logger import log_info, log_error
from utils.resource_helper import resource_path


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


def generate_single_pdf(file_path):
    with open(file_path, 'r', encoding='cp852') as f:
        raw_content = f.read()

    html_ready = transform_control_codes(raw_content)
    html_ready = center_only_first_page(html_ready)

    template_path = resource_path('templates/pdf_template.html')
    with open(template_path, 'r', encoding='utf-8') as template_file:
        html_template = template_file.read()

    html_content = html_template.replace('{{ content }}', html_ready)

    output_path = os.path.splitext(file_path)[0] + '.pdf'

    pdfkit.from_string(html_content, output_path, configuration=config)

    return output_path


def generate_pdf_to_path(file_path, output_pdf_path, additional_list):
    with open(file_path, 'r', encoding='cp852') as f:
        raw_content = f.read()

    html_ready = transform_control_codes(raw_content)
    html_ready = center_only_first_page(html_ready)

    template_path = resource_path('templates/pdf_template.html')
    with open(template_path, 'r', encoding='utf-8') as tpl_file:
        html_template = tpl_file.read()

    filled_html = html_template.replace('{{ content }}', html_ready)
    pdfkit.from_string(filled_html, output_pdf_path, configuration=config)

    if additional_list:
        html_ready_masked = mask_pigeon_rings(html_ready)

        filled_html_masked = html_template.replace('{{ content }}', html_ready_masked)
        closed_list_path = output_pdf_path.replace('.pdf', ' - LISTA ZAMKNIĘTA.pdf')

        pdfkit.from_string(filled_html_masked, closed_list_path, configuration=config)


def mask_pigeon_rings(text):
    pattern = re.compile(r'\b[A-Z]{2,}[A-Z\d\-]{10,}\d\b')

    def replacer(match):
        s = match.group()
        return s[:-5] + 'XXXXX'

    return pattern.sub(replacer, text)
