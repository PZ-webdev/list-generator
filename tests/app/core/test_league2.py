import os
from types import SimpleNamespace

import pytest

from app.core.lot_pdf_service import LotPdfService
from app.dto.branch import Branch


class DummyPdfGen2:
    def __init__(self):
        self.calls = []

    def generate_league2_only_to_path(self, *args, **kwargs):
        self.calls.append((args, kwargs))


def test_generate_league2_only_for_lot_calls_generator(tmp_path, monkeypatch):
    # Force young pigeons -> suffix M
    monkeypatch.setattr('app.core.lot_pdf_service._read_is_old_global', lambda: False)

    # Input structure with branch-level LKON and II-LIGA file
    lot_dir = tmp_path / 'INP' / 'LOT_M_01.001'
    (lot_dir).mkdir(parents=True)
    (lot_dir / 'LKON_M01.TXT').write_text('A')
    (lot_dir / 'II-LIGA').mkdir()
    (lot_dir / 'II-LIGA' / 'LKON_M01_II.TXT').write_text('B')

    dummy = DummyPdfGen2()
    svc = LotPdfService(dummy)
    branch = Branch(id='1', name='B', number='123', input=str(tmp_path / 'INP'), output=str(tmp_path / 'OUT'))

    # Silence notifier
    monkeypatch.setattr('app.utils.notifier.show_success', lambda *a, **k: None)
    monkeypatch.setattr('app.utils.notifier.show_warning', lambda *a, **k: None)

    svc.generate_league2_only_for_lot(branch, '1', additional_list=False)
    # Should attempt league2 generation for branch-level file
    assert len(dummy.calls) == 1


def test_generate_league2_only_to_path_outputs_files(tmp_path, monkeypatch):
    # Mock wkhtmltopdf and pdfkit
    import app.core.pdf_generator_service as mod
    calls = []
    monkeypatch.setattr('shutil.which', lambda x: '/usr/bin/wkhtmltopdf')
    monkeypatch.setattr(mod, 'pdfkit', SimpleNamespace(
        configuration=lambda wkhtmltopdf=None: object(),
        from_string=lambda html, output_path, configuration=None: calls.append(output_path)
    ))

    # Mock settings filenames
    monkeypatch.setattr('app.dto.settings_dto.SettingsDTO.from_json', lambda: SimpleNamespace(
        filename_branch='OPEN_{BRANCH}_{DATE}.pdf',
        filename_branch_closed='CLOSED_{BRANCH}_{DATE}.pdf',
        filename_section='OPEN_{BRANCH}_{DATE}_S{SECTION}.pdf',
        filename_section_closed='CLOSED_{BRANCH}_{DATE}_S{SECTION}.pdf',
        attached_files=[],
        ring_mask='#####',
        default_pdf_dir='' ,
        is_old_pigeon=False,
    ))

    svc = mod.PdfGeneratorService()

    # Build input with II-LIGA
    lot = tmp_path / 'LOT_M_01.001'
    lot.mkdir()
    main_txt = lot / 'LKON_M01.TXT'
    main_txt.write_bytes('MAIN'.encode('cp852'))
    league_dir = lot / 'II-LIGA'
    league_dir.mkdir()
    (league_dir / 'LKON_M01_EXTRA.TXT').write_bytes('LEAGUE2'.encode('cp852'))

    out_dir = tmp_path / 'OUT'
    out_dir.mkdir()
    branch = Branch(id='1', name='B', number='123', input=str(tmp_path), output=str(tmp_path))

    svc.generate_league2_only_to_path(branch, str(main_txt), str(out_dir), additional_list=True)

    # Expect two outputs: II liga and II liga - ZAMKNIĘTA
    assert any(p.endswith(' II liga.pdf') for p in calls)
    assert any(p.endswith(' II liga - ZAMKNIĘTA.pdf') for p in calls)
