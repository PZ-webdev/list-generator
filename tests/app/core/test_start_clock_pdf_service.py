from app.core.start_clock_pdf_service import StartClockPdfService


def test_normalize_start_clock_continuations_removes_internal_ff_and_headers():
    s = StartClockPdfService()
    src = (
        "│ G│PL-503-25---720│        │01│          │ 16│   │       │                 │\n"
        "└──┴───────────────┴────────┴──┴──────────┴──────┴───┴───────┴─────────────────┘\n"
        "\f"
        "      401 - ARGASIŃSKI PIOTR      \n"
        "┌──┬───────────────┬────────┬──┬──────────┬──────┬───┬───────┬─────────────────┐\n"
        "│MP│OBRĄCZKA RODOWA│ BARWA  │PŁ│OBR.GUMOWA│ KOMP │SER│KOLEJNY│  CZAS PRZYLOTU  │\n"
        "├──┼───────────────┼────────┼──┼──────────┼──────┼───┼───────┼─────────────────┤\n"
        "│ G│PL-503-25---721│        │01│          │ 17│   │       │                 │\n"
    )
    out = s._normalize_continuations(src)
    assert '\f' not in out
    assert '401 - ARGASIŃSKI PIOTR' not in out
    assert 'OBRĄCZKA RODOWA' not in out
    assert '├──┼' in out
    assert 'PL-503-25---721' in out


def test_normalize_start_clock_duplicate_headers_collapses_repeated_block():
    s = StartClockPdfService()
    src = (
        "┌──────────────────┬──┬──┐\n"
        "│NRY GOŁ. SERYJNYCH│  │  │\n"
        "├──────────────────┼──┼──┤\n"
        "│NRY GOŁ. SERYJNYCH│  │  │\n"
        "├──┬───────────────┼──┴──┤\n"
    )
    out = s._normalize_duplicate_headers(src)
    assert out.count("│NRY GOŁ. SERYJNYCH│  │  │\n") == 1
    assert out == (
        "┌──────────────────┬──┬──┐\n"
        "│NRY GOŁ. SERYJNYCH│  │  │\n"
        "├──┬───────────────┼──┴──┤\n"
    )


def test_wrap_page_segments_creates_separate_pages():
    s = StartClockPdfService()
    out = s._wrap_page_segments("A<div class=\"page-break\"></div>B")
    assert out.count('<div class="page">') == 2
    assert 'page-inner' in out
