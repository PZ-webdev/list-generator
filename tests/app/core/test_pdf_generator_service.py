import os
from types import SimpleNamespace

import pytest


def make_pdf_service(monkeypatch):
    # Mock pdfkit configuration and from_string
    import app.core.pdf_generator_service as mod
    calls = []
    monkeypatch.setattr('shutil.which', lambda x: '/usr/bin/wkhtmltopdf')
    monkeypatch.setattr(mod, 'pdfkit', SimpleNamespace(
        configuration=lambda wkhtmltopdf=None: object(),
        from_string=lambda html, output_path, configuration=None: calls.append((html, output_path))
    ))
    # Build service
    svc = mod.PdfGeneratorService()
    return svc, calls


def test_get_output_filenames_section(monkeypatch, tmp_path):
    svc, _ = make_pdf_service(monkeypatch)
    # Mock settings
    from app.dto.branch import Branch
    monkeypatch.setattr('app.dto.settings_dto.SettingsDTO.from_json', lambda: SimpleNamespace(
        filename_section='OPEN_{BRANCH}_{DATE}_S{SECTION}.pdf',
        filename_section_closed='CLOSED_{BRANCH}_{DATE}_S{SECTION}.pdf',
        filename_branch='OPENB_{BRANCH}_{DATE}.pdf',
        filename_branch_closed='CLOSEDB_{BRANCH}_{DATE}.pdf',
    ))

    fpath = os.path.join(str(tmp_path), 'LOT_M_01.001', 'SEKCJA.03', 'LKON_M01.TXT')
    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    open(fpath, 'w').close()
    branch = Branch(id='1', name='B', number='123', input=str(tmp_path), output=str(tmp_path))
    out_open, out_closed = svc.get_output_filenames(branch, fpath, str(tmp_path))
    assert out_open.endswith('S03.pdf')
    assert out_closed.endswith('S03.pdf')


def test_get_output_filenames_branch(monkeypatch, tmp_path):
    svc, _ = make_pdf_service(monkeypatch)
    from app.dto.branch import Branch
    monkeypatch.setattr('app.dto.settings_dto.SettingsDTO.from_json', lambda: SimpleNamespace(
        filename_section='OPEN_{BRANCH}_{DATE}_S{SECTION}.pdf',
        filename_section_closed='CLOSED_{BRANCH}_{DATE}_S{SECTION}.pdf',
        filename_branch='OPENB_{BRANCH}_{DATE}.pdf',
        filename_branch_closed='CLOSEDB_{BRANCH}_{DATE}.pdf',
    ))
    # No SEKCJA.* in path -> branch filenames
    fpath = os.path.join(str(tmp_path), 'LOT_M_01.001', 'LKON_M01.TXT')
    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    open(fpath, 'w').close()
    branch = Branch(id='1', name='B', number='123', input=str(tmp_path), output=str(tmp_path))
    out_open, out_closed = svc.get_output_filenames(branch, fpath, str(tmp_path))
    assert out_open.endswith('.pdf') and '_S' not in os.path.basename(out_open)
    assert out_closed.endswith('.pdf') and '_S' not in os.path.basename(out_closed)


def test_generate_single_pdf_uses_default_dir(monkeypatch, tmp_path):
    svc, calls = make_pdf_service(monkeypatch)
    # template exists via resource_path; create input txt
    f = tmp_path / 'file.TXT'
    f.write_bytes('ABC'.encode('cp852'))
    # Mock settings to direct output to custom dir
    out_dir = tmp_path / 'out'
    out_dir.mkdir()
    monkeypatch.setattr('app.dto.settings_dto.SettingsDTO.from_json', lambda: SimpleNamespace(
        default_pdf_dir=str(out_dir)
    ))
    out_path = svc.generate_single_pdf(str(f))
    assert len(calls) == 1
    assert os.path.dirname(out_path) == str(out_dir)


def test_generate_pdf_to_path_calls_pdfkit(monkeypatch, tmp_path):
    svc, calls = make_pdf_service(monkeypatch)
    # Mock settings for output file names
    monkeypatch.setattr('app.dto.settings_dto.SettingsDTO.from_json', lambda: SimpleNamespace(
        filename_branch='OPEN_{BRANCH}_{DATE}.pdf',
        filename_branch_closed='CLOSED_{BRANCH}_{DATE}.pdf',
        filename_section='OPEN_{BRANCH}_{DATE}_S{SECTION}.pdf',
        filename_section_closed='CLOSED_{BRANCH}_{DATE}_S{SECTION}.pdf',
    ))
    # Create input file and branch
    txt = tmp_path / 'LOT_M_01.001' / 'LKON_M01.TXT'
    os.makedirs(txt.parent, exist_ok=True)
    txt.write_bytes('ABC'.encode('cp852'))
    from app.dto.branch import Branch
    branch = Branch(id='1', name='B', number='123', input=str(tmp_path), output=str(tmp_path))
    out_dir = tmp_path / 'out'
    out_dir.mkdir()
    svc.generate_pdf_to_path(branch, str(txt), str(out_dir), additional_list=False, rating_list=False)
    # One PDF generated
    assert len(calls) == 1
