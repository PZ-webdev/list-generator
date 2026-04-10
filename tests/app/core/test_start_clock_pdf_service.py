from app.core.start_clock_pdf_service import StartClockPdfService


def test_normalize_start_clock_duplicate_headers_collapses_repeated_block():
    s = StartClockPdfService()
    src = (
        "┌──────────────────┬──┬──┬──┬──┬──┬──┐\n"
        "│NRY GOŁ. SERYJNYCH│  │  │  │  │  │  │\n"
        "├──────────────────┼──┼──┼──┼──┼──┼──┤\n"
        "│NRY GOŁ. SERYJNYCH│  │  │  │  │  │  │\n"
        "├──┬───────────────┼──┴──┴──┴──┴──┴──┤\n"
    )
    out = s._normalize_duplicate_headers(src)
    assert out.count("NRY GOŁ. SERYJNYCH") == 1
    assert out == (
        "┌──────────────────┬──┬──┬──┬──┬──┬──┐\n"
        "│NRY GOŁ. SERYJNYCH│  │  │  │  │  │  │\n"
        "├──┬───────────────┼──┴──┴──┴──┴──┴──┤\n"
    )


def test_wrap_page_segments_creates_separate_pages():
    s = StartClockPdfService()
    out = s._wrap_page_segments("A<div class=\"page-break\"></div>B")
    assert out.count('<div class="page">') == 2
    assert 'page-inner' in out


def test_wrap_page_segments_ignores_empty_trailing_page_break():
    s = StartClockPdfService()
    out = s._wrap_page_segments("A<div class=\"page-break\"></div>")
    assert out.count('<div class="page">') == 1
    assert 'A' in out


def test_strip_emphasis_codes_removes_start_clock_highlight_markup():
    s = StartClockPdfService()
    src = "Hodowca -\x1bG\x1bW1 413\x1bH\x1bW0- PARUCH ADAM\n"
    out = s._strip_emphasis_codes(src)
    assert '\x1b' not in out
    assert "Hodowca - 413- PARUCH ADAM\n" == out


def test_normalize_comp_column_removes_escape_markup_from_table_rows():
    s = StartClockPdfService()
    src = "│ G│PL-496-20--6613│        │01│          │\x1bG\x1bW1  1\x1bH\x1bW0│   │       │                 │\n"
    out = s._normalize_comp_column(src)
    assert '\x1bG' not in out
    assert '\x1bW1' not in out
    assert '│  1   │' in out


def test_normalize_comp_column_handles_non_pl_table_rows():
    s = StartClockPdfService()
    src = "│ G│SK-2401-20-1425│        │01│          │\x1bG\x1bW1  4\x1bH\x1bW0│   │       │                 │\n"
    out = s._normalize_comp_column(src)
    assert '\x1bG' not in out
    assert '│  4   │' in out


def test_get_output_filename_is_start_clock_specific(tmp_path):
    from app.dto.branch import Branch

    s = StartClockPdfService()
    branch = Branch(id='1', name='B', number='123', input=str(tmp_path), output=str(tmp_path))
    out = s.get_output_filename(branch, str(tmp_path))
    assert out == str(tmp_path / 'LISTA STARTOWO-ZEGAROWA.pdf')


def test_build_html_preserves_existing_page_breaks_between_breeder_segments():
    s = StartClockPdfService()
    raw = (
        "  Hodowca -\x1bG\x1bW1 401\x1bH\x1bW0- TEST HODOWCA           Sek.nr  4  - KROSNO         \n"
        "ł GłPL-503-25---701ł        ł01ł          ł\x1bG\x1bW1  1\x1bH\x1bW0ł   ł       ł                 ł\n"
        "\f"
        "      401 - TEST HODOWCA      \n"
        "ÚÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÂÄÄÂÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÂÄÄÄÂÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄż\n"
        "łMPłOBR¤CZKA RODOWAł BARWA  łPťłOBR.GUMOWAł KOMP łSERłKOLEJNYł  CZAS PRZYLOTU  ł\n"
        "ĂÄÄĹÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄĹÄÄÄÄÄÄÄÄĹÄÄĹÄÄÄÄÄÄÄÄÄÄĹÄÄÄÄÄÄĹÄÄÄĹÄÄÄÄÄÄÄĹÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ´\n"
        "ł GłPL-503-25---702ł        ł01ł          ł\x1bG\x1bW1 21\x1bH\x1bW0ł   ł       ł                 ł\n"
    )
    out = s.build_html(raw)
    assert out.count('<div class="page"><div class="page-inner">') == 2
