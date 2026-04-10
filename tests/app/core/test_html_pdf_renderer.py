from types import SimpleNamespace

import pytest


def test_renderer_uses_wkhtmltopdf_from_path(monkeypatch):
    import app.core.html_pdf_renderer as mod

    config_calls = []
    monkeypatch.setattr(mod.shutil, 'which', lambda _: '/usr/bin/wkhtmltopdf')
    monkeypatch.setattr(mod.pdfkit, 'configuration', lambda wkhtmltopdf=None: config_calls.append(wkhtmltopdf) or object())

    renderer = mod.HtmlPdfRenderer()
    assert renderer.config is not None
    assert config_calls == ['/usr/bin/wkhtmltopdf']


def test_renderer_uses_windows_fallback_path(monkeypatch):
    import app.core.html_pdf_renderer as mod

    monkeypatch.setattr(mod.shutil, 'which', lambda _: None)
    monkeypatch.setattr(mod.platform, 'system', lambda: 'Windows')
    monkeypatch.setattr(mod.os.path, 'exists', lambda p: p.endswith('wkhtmltopdf.exe'))
    monkeypatch.setattr(mod.pdfkit, 'configuration', lambda wkhtmltopdf=None: SimpleNamespace(path=wkhtmltopdf))

    renderer = mod.HtmlPdfRenderer()
    assert renderer.config.path.endswith('wkhtmltopdf.exe')


def test_renderer_raises_when_wkhtmltopdf_missing(monkeypatch):
    import app.core.html_pdf_renderer as mod

    monkeypatch.setattr(mod.shutil, 'which', lambda _: None)
    monkeypatch.setattr(mod.platform, 'system', lambda: 'Linux')

    with pytest.raises(FileNotFoundError):
        mod.HtmlPdfRenderer()


def test_render_passes_html_and_output_to_pdfkit(monkeypatch):
    import app.core.html_pdf_renderer as mod

    calls = []
    monkeypatch.setattr(mod.shutil, 'which', lambda _: '/usr/bin/wkhtmltopdf')
    monkeypatch.setattr(mod.pdfkit, 'configuration', lambda wkhtmltopdf=None: 'CFG')
    monkeypatch.setattr(mod.pdfkit, 'from_string', lambda html, output_path, configuration=None: calls.append((html, output_path, configuration)))

    renderer = mod.HtmlPdfRenderer()
    renderer.render('<html>x</html>', '/tmp/out.pdf')

    assert calls == [('<html>x</html>', '/tmp/out.pdf', 'CFG')]
