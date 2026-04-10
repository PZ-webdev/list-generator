import os
import glob
import shutil
from unittest import SkipTest


wkhtmltopdf_path = shutil.which('wkhtmltopdf')


def test_oddzialowa_results_start_on_page_two(tmp_path):
    if wkhtmltopdf_path is None:
        raise SkipTest('wkhtmltopdf not available')

    try:
        from pdfminer import high_level as pdfminer_high_level
    except Exception:
        raise SkipTest('pdfminer not available')

    from app.core.pdf_generator_service import PdfGeneratorService
    from app.dto.branch import Branch

    svc = PdfGeneratorService()

    src_txt = os.path.join('example', 'LKON_M03.TXT')
    assert os.path.isfile(src_txt), 'missing example/LKON_M03.TXT'

    out_dir = tmp_path / 'out'
    out_dir.mkdir(parents=True, exist_ok=True)

    # Minimal branch; number/name do not affect layout, only filenames
    branch = Branch(id='t', name='Test', number='TEST', input=os.path.dirname(src_txt), output=str(out_dir))

    # Generate PDF to tmp folder (no additional closed list, no rating files)
    svc.generate_pdf_to_path(branch, src_txt, str(out_dir), additional_list=False, rating_list=False)

    pdfs = sorted(glob.glob(os.path.join(str(out_dir), '*.pdf')))
    assert pdfs, 'no PDF generated'
    pdf_path = pdfs[0]

    text = pdfminer_high_level.extract_text(pdf_path)
    # pdfminer inserts form feed (\x0c) between pages
    pages = text.split('\x0c')
    assert len(pages) >= 2, 'expected multi-page PDF'

    first_page = pages[0]
    second_page = pages[1]

    # First page contains section summary "RAZEM ODDZIA" and signature
    assert 'RAZEM ODDZIA' in first_page.upper()
    assert 'PREZES' in first_page.upper()

    # Second page begins the results table
    assert 'NAZWISKO HODOWCY' in second_page.upper() or 'LP.' in second_page.upper()

    # Ensure placeholder rows like "nr X ... 0  0  0  0.0" are gone
    assert ' NR ' not in first_page.upper() or ' 0.0' not in first_page
