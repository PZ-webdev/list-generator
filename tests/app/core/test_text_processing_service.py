import os
from app.core.text_processing_service import TextProcessingService


def test_transform_control_codes_headers_and_breaks():
    s = TextProcessingService()
    src = "\x1bG\x1bW1TITLE\x1bW0\nline\fend"
    out = s.transform_control_codes(src)
    assert '<h1>TITLE</h1>' in out or '<h2>TITLE</h2>' in out
    assert 'line' in out
    assert '<div class="page-break"></div>' in out
    # trailing breaks removed
    assert not out.rstrip().endswith('<div class="page-break"></div>')


def test_center_only_first_page_wraps_first_page():
    s = TextProcessingService()
    html = 'A<div class="page-break"></div>B'
    out = s.center_only_first_page(html)
    assert out.startswith('<div class="first-page-center">')
    assert 'A' in out and 'B' in out


def test_append_rating_files_to_content(tmp_path):
    s = TextProcessingService()
    base = tmp_path
    f1 = base / 'PHD_1AS.TXT'
    f2 = base / 'PHDOD1A.TXT'
    f1.write_bytes('AAA'.encode('cp852'))
    f2.write_bytes('BBB'.encode('cp852'))
    out = s.append_rating_files_to_content('X', str(base), ['PHD_1AS.TXT', 'PHDOD1A.TXT'])
    assert 'AAA' in out and 'BBB' in out and out.startswith('X')


def test_mask_pigeon_rings_default_and_custom(monkeypatch):
    s = TextProcessingService()
    text = 'num PLABCDEFGHIJ123456 end'
    # Force default by making settings lookup fail
    monkeypatch.setattr('app.dto.settings_dto.SettingsDTO.from_json', lambda: (_ for _ in ()).throw(Exception('no settings')))
    masked = s.mask_pigeon_rings(text)
    assert masked.endswith('XXXXX end')

    class Dummy:
        ring_mask = '******'

    monkeypatch.setattr('app.dto.settings_dto.SettingsDTO.from_json', lambda: Dummy())
    masked2 = s.mask_pigeon_rings(text)
    assert masked2.endswith('****** end')
def test_remove_empty_section_rows():
    s = TextProcessingService()
    src = (
        "    |    SEKCJA    |Hod|W|Gon|% Ngr|\n"
        "    |nr 1          |  0|  0|  0| 0.0|\n"
        "    |KROSNO        | 16|861|239|27.8|\n"
        "    |nr 2          |  0|  0|  0| 0.0|\n"
        "    |SZCZEPAŃCOWA  | 13|846|226|26.7|\n"
    )
    out = s.transform_control_codes(src)
    assert 'nr 1' not in out and 'nr 2' not in out
    assert 'KROSNO' in out and 'SZCZEPA' in out


def test_ensure_page_break_after_section_table_inserts_ff():
    s = TextProcessingService()
    src = (
        "ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂ\n"
        "³    SEKCJA     ³\n"
        "ÃÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ\n"
        "³nr 1           ³  0  0  0  0.0\n"
        "³KROSNO         ³ 10 271  68 25.1\n"
        "ÃÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅ\n"
        "³ RAZEM ODDZIA  ³ 27  763  191 25.0\n"
        "ÀÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁ\n"
        "NEXT CONTENT\n"
    )
    out = s.transform_control_codes(src)
    assert '<div class="page-break"></div>' in out

    src2 = src.replace('NEXT CONTENT', '\fNEXT CONTENT')
    out2 = s.transform_control_codes(src2)
    assert out2.count('<div class="page-break"></div>') == 1
