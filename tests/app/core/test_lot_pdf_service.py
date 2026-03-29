import os
from typing import List, Tuple

from app.core.lot_pdf_service import LotPdfService
from app.dto.branch import Branch


class DummyPdfGen:
    def __init__(self):
        self.calls: List[Tuple] = []

    def generate_pdf_to_path(self, *args, **kwargs):
        self.calls.append((args, kwargs))

    def generate_start_clock_pdf_to_path(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return kwargs.get('output_dir', '')


def test_get_matching_lot_dir_and_txt_files(tmp_path, monkeypatch):
    # Force young pigeons -> suffix M
    monkeypatch.setattr('app.core.lot_pdf_service._read_is_old_global', lambda: False)
    svc = LotPdfService(DummyPdfGen())

    lot_dir = tmp_path / 'LOT_M_02.001'
    (lot_dir / 'sub').mkdir(parents=True)
    (lot_dir / 'sub' / 'LKON_M01.TXT').write_text('x')
    (lot_dir / 'sub' / 'OTHER.txt').write_text('y')

    matched = svc.get_matching_lot_dir(str(tmp_path), '2')
    assert matched == 'LOT_M_02.001'

    files = svc.get_txt_files(str(lot_dir))
    assert any(name == 'LKON_M01.TXT' for _, name in files)
    assert all(name.endswith('.TXT') for _, name in files)


def test_create_lot_dirs_m_and_s(tmp_path):
    svc = LotPdfService(DummyPdfGen())
    base = tmp_path
    final_m = svc.create_lot_dirs(output_dir=str(base), is_old_pigeon=False, lot_number='3', sections=3)[0]
    assert os.path.isdir(final_m)
    assert os.path.isdir(os.path.join(final_m, 'Sekcja 01'))
    # STARE
    final_s = svc.create_lot_dirs(output_dir=str(base), is_old_pigeon=True, lot_number='3', sections=2)[0]
    assert os.path.isdir(final_s)


def test_generate_pdfs_for_lot_happy_path(tmp_path, monkeypatch):
    monkeypatch.setattr('app.core.lot_pdf_service._read_is_old_global', lambda: False)
    dummy = DummyPdfGen()
    svc = LotPdfService(dummy)

    inp = tmp_path / 'INP'
    out = tmp_path / 'OUT'
    lot_dir = inp / 'LOT_M_02.001' / 'x'
    lot_dir.mkdir(parents=True)
    (lot_dir / 'LKON_M01.TXT').write_text('a')

    calls = []

    def progress(i, total):
        calls.append((i, total))

    branch = Branch(id='1', name='B', number='100', input=str(inp), output=str(out))
    # Silence notifier
    monkeypatch.setattr('app.utils.notifier.show_success', lambda *a, **k: None)
    monkeypatch.setattr('app.utils.notifier.show_warning', lambda *a, **k: None)
    svc.generate_pdfs_for_lot(branch, '2', additional_list=False, rating_list=False, progress_callback=progress)

    assert len(dummy.calls) == 1
    assert calls and calls[-1][0] == calls[-1][1] == 1


def test_get_start_clock_file_and_generate_pdf(tmp_path, monkeypatch):
    monkeypatch.setattr('app.core.lot_pdf_service._read_is_old_global', lambda: False)
    dummy = DummyPdfGen()
    svc = LotPdfService(dummy)

    inp = tmp_path / 'INP'
    out = tmp_path / 'OUT'
    data_dir = inp / 'DANE_GL'
    data_dir.mkdir(parents=True)
    (data_dir / '--DRLSTZEG.TXT').write_text('a')

    branch = Branch(id='1', name='B', number='100', input=str(inp), output=str(out))
    monkeypatch.setattr('app.utils.notifier.show_warning', lambda *a, **k: None)

    found = svc.get_start_clock_file(str(inp))
    assert found and found.endswith('--DRLSTZEG.TXT')

    output_path = svc.generate_start_clock_pdf_for_lot(branch)
    assert output_path == str(out)
    assert len(dummy.calls) == 1
    assert dummy.calls[0][1]['output_dir'] == str(out)
