import os
from types import SimpleNamespace

import pytest


def make_pdf_service(monkeypatch):
    # Mock pdfkit configuration and from_string
    import app.core.pdf_generator_service as mod
    calls = []
    monkeypatch.setattr(mod, 'HtmlPdfRenderer', lambda: SimpleNamespace(
        render=lambda html, output_path: calls.append((html, output_path))
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
    monkeypatch.setattr(svc.start_clock_service, 'build_html', lambda *_: (_ for _ in ()).throw(AssertionError('unexpected start-clock call')))
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


def test_generate_start_clock_pdf_to_path_calls_pdfkit(monkeypatch, tmp_path):
    svc, calls = make_pdf_service(monkeypatch)
    txt = tmp_path / 'LOT_M_01.001' / 'DRLSTZEG.TXT'
    os.makedirs(txt.parent, exist_ok=True)
    txt.write_bytes('ABC'.encode('cp852'))

    from app.dto.branch import Branch
    branch = Branch(id='1', name='B', number='123', input=str(tmp_path), output=str(tmp_path))
    out_dir = tmp_path / 'out'
    out_dir.mkdir()

    output_path = svc.generate_start_clock_pdf_to_path(branch, str(txt), str(out_dir))
    assert len(calls) == 1
    assert os.path.dirname(output_path) == str(out_dir)
    assert os.path.basename(output_path) == 'LISTA STARTOWO-ZEGAROWA.pdf'


def test_generate_single_pdf_falls_back_to_default_output_when_settings_fail(monkeypatch, tmp_path):
    svc, calls = make_pdf_service(monkeypatch)
    f = tmp_path / 'file.TXT'
    f.write_bytes('ABC'.encode('cp852'))
    monkeypatch.setattr('app.dto.settings_dto.SettingsDTO.from_json', lambda: (_ for _ in ()).throw(RuntimeError('boom')))

    out_path = svc.generate_single_pdf(str(f))

    assert len(calls) == 1
    assert out_path == str(tmp_path / 'file.pdf')


def test_generate_pdf_to_path_with_additional_and_rating_renders_two_files(monkeypatch, tmp_path):
    svc, calls = make_pdf_service(monkeypatch)
    monkeypatch.setattr('app.dto.settings_dto.SettingsDTO.from_json', lambda: SimpleNamespace(
        filename_branch='OPEN_{BRANCH}_{DATE}.pdf',
        filename_branch_closed='CLOSED_{BRANCH}_{DATE}.pdf',
        filename_section='OPEN_{BRANCH}_{DATE}_S{SECTION}.pdf',
        filename_section_closed='CLOSED_{BRANCH}_{DATE}_S{SECTION}.pdf',
        attached_files=['R1.TXT'],
        ring_mask='XXXXX',
    ))

    appended = []
    monkeypatch.setattr(svc.text_service, 'append_rating_files_to_content', lambda content, base_dir, names: appended.append((content, base_dir, names)) or 'RAW+RATING')
    monkeypatch.setattr(svc.text_service, 'transform_control_codes', lambda raw: f'HTML[{raw}]')
    monkeypatch.setattr(svc.text_service, 'center_only_first_page', lambda html: f'CENTER[{html}]')
    monkeypatch.setattr(svc.text_service, 'mask_pigeon_rings', lambda html: f'MASK[{html}]')

    txt = tmp_path / 'LOT_M_01.001' / 'LKON_M01.TXT'
    os.makedirs(txt.parent, exist_ok=True)
    txt.write_bytes('ABC'.encode('cp852'))

    from app.dto.branch import Branch
    branch = Branch(id='1', name='B', number='123', input=str(tmp_path), output=str(tmp_path))
    out_dir = tmp_path / 'out'
    out_dir.mkdir()

    svc.generate_pdf_to_path(branch, str(txt), str(out_dir), additional_list=True, rating_list=True)

    assert appended and appended[0][2] == ['R1.TXT']
    assert len(calls) == 2
    assert 'MASK[' in calls[1][0]


def test_generate_pdf_to_path_appends_matching_league2_file(monkeypatch, tmp_path):
    svc, calls = make_pdf_service(monkeypatch)
    monkeypatch.setattr('app.dto.settings_dto.SettingsDTO.from_json', lambda: SimpleNamespace(
        filename_branch='OPEN_{BRANCH}_{DATE}.pdf',
        filename_branch_closed='CLOSED_{BRANCH}_{DATE}.pdf',
        filename_section='OPEN_{BRANCH}_{DATE}_S{SECTION}.pdf',
        filename_section_closed='CLOSED_{BRANCH}_{DATE}_S{SECTION}.pdf',
    ))

    def fake_transform(raw):
        return f'HTML[{raw}]'

    monkeypatch.setattr(svc.text_service, 'transform_control_codes', fake_transform)
    monkeypatch.setattr(svc.text_service, 'center_only_first_page', lambda html: f'CENTER[{html}]')

    lot_dir = tmp_path / 'LOT_M_01.001'
    league_dir = lot_dir / 'II-LIGA'
    league_dir.mkdir(parents=True)
    txt = lot_dir / 'LKON_M01.TXT'
    txt.write_bytes('BASE'.encode('cp852'))
    (league_dir / 'LKON_M01_EXTRA.TXT').write_bytes('LEAGUE'.encode('cp852'))

    from app.dto.branch import Branch
    branch = Branch(id='1', name='B', number='123', input=str(tmp_path), output=str(tmp_path))
    out_dir = tmp_path / 'out'
    out_dir.mkdir()

    svc.generate_pdf_to_path(branch, str(txt), str(out_dir), additional_list=False, rating_list=False, league2_list=True)

    assert len(calls) == 1
    assert 'CENTER[HTML[BASE]]<div class="page-break"></div>CENTER[HTML[LEAGUE]]' in calls[0][0]


def test_generate_pdf_to_path_skips_league2_for_section(monkeypatch, tmp_path):
    svc, calls = make_pdf_service(monkeypatch)
    monkeypatch.setattr('app.dto.settings_dto.SettingsDTO.from_json', lambda: SimpleNamespace(
        filename_branch='OPEN_{BRANCH}_{DATE}.pdf',
        filename_branch_closed='CLOSED_{BRANCH}_{DATE}.pdf',
        filename_section='OPEN_{BRANCH}_{DATE}_S{SECTION}.pdf',
        filename_section_closed='CLOSED_{BRANCH}_{DATE}_S{SECTION}.pdf',
    ))
    monkeypatch.setattr(svc.text_service, 'transform_control_codes', lambda raw: f'HTML[{raw}]')
    monkeypatch.setattr(svc.text_service, 'center_only_first_page', lambda html: f'CENTER[{html}]')

    txt = tmp_path / 'LOT_M_01.001' / 'SEKCJA.03' / 'LKON_M01.TXT'
    os.makedirs(txt.parent, exist_ok=True)
    txt.write_bytes('BASE'.encode('cp852'))
    league_dir = tmp_path / 'LOT_M_01.001' / 'II-LIGA'
    league_dir.mkdir(parents=True)
    (league_dir / 'LKON_M01_EXTRA.TXT').write_bytes('LEAGUE'.encode('cp852'))

    from app.dto.branch import Branch
    branch = Branch(id='1', name='B', number='123', input=str(tmp_path), output=str(tmp_path))
    out_dir = tmp_path / 'out'
    out_dir.mkdir()

    svc.generate_pdf_to_path(branch, str(txt), str(out_dir), additional_list=False, rating_list=False, league2_list=True)

    assert len(calls) == 1
    assert 'LEAGUE' not in calls[0][0]


def test_generate_league2_only_to_path_raises_for_section(monkeypatch, tmp_path):
    svc, _ = make_pdf_service(monkeypatch)
    txt = tmp_path / 'LOT_M_01.001' / 'SEKCJA.03' / 'LKON_M01.TXT'
    os.makedirs(txt.parent, exist_ok=True)
    txt.write_bytes('BASE'.encode('cp852'))

    from app.dto.branch import Branch
    branch = Branch(id='1', name='B', number='123', input=str(tmp_path), output=str(tmp_path))

    with pytest.raises(ValueError):
        svc.generate_league2_only_to_path(branch, str(txt), str(tmp_path))


def test_generate_league2_only_to_path_raises_without_lot_root(monkeypatch, tmp_path):
    svc, _ = make_pdf_service(monkeypatch)
    txt = tmp_path / 'X' / 'LKON_M01.TXT'
    os.makedirs(txt.parent, exist_ok=True)
    txt.write_bytes('BASE'.encode('cp852'))

    from app.dto.branch import Branch
    branch = Branch(id='1', name='B', number='123', input=str(tmp_path), output=str(tmp_path))

    with pytest.raises(ValueError):
        svc.generate_league2_only_to_path(branch, str(txt), str(tmp_path))


def test_generate_league2_only_to_path_raises_when_no_matching_file(monkeypatch, tmp_path):
    svc, _ = make_pdf_service(monkeypatch)
    monkeypatch.setattr('app.dto.settings_dto.SettingsDTO.from_json', lambda: SimpleNamespace(
        filename_branch='OPEN_{BRANCH}_{DATE}.pdf',
        filename_branch_closed='CLOSED_{BRANCH}_{DATE}.pdf',
        filename_section='OPEN_{BRANCH}_{DATE}_S{SECTION}.pdf',
        filename_section_closed='CLOSED_{BRANCH}_{DATE}_S{SECTION}.pdf',
    ))
    lot_dir = tmp_path / 'LOT_M_01.001'
    txt = lot_dir / 'LKON_M01.TXT'
    os.makedirs(txt.parent, exist_ok=True)
    txt.write_bytes('BASE'.encode('cp852'))
    league_dir = lot_dir / 'II-LIGA'
    league_dir.mkdir()
    (league_dir / 'OTHER.TXT').write_bytes('LEAGUE'.encode('cp852'))
    (league_dir / 'SECOND.TXT').write_bytes('LEAGUE2'.encode('cp852'))

    from app.dto.branch import Branch
    branch = Branch(id='1', name='B', number='123', input=str(tmp_path), output=str(tmp_path))

    with pytest.raises(FileNotFoundError):
        svc.generate_league2_only_to_path(branch, str(txt), str(tmp_path))


def test_build_html_from_raw_without_centering(monkeypatch):
    svc, _ = make_pdf_service(monkeypatch)
    monkeypatch.setattr(svc.text_service, 'transform_control_codes', lambda raw: f'HTML[{raw}]')
    monkeypatch.setattr('app.core.pdf_generator_service.resource_path', lambda rel: rel)
    monkeypatch.setattr('app.core.pdf_generator_service.read_file_utf8', lambda path: 'TPL {{ content }}')

    out = svc._build_html_from_raw('RAW', center_first_page=False)

    assert out == 'TPL HTML[RAW]'
