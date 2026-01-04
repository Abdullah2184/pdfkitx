import fitz
from pdf_manager.pdf_tools import split, extract_pages, delete_pages, combine
from pathlib import Path


def create_sample_pdf(path: Path, pages: int = 6):
    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page()
        page.insert_text((72, 72), f"Page {i+1}")
    doc.save(path)
    doc.close()


def test_split_and_extract_and_combine(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    create_sample_pdf(pdf_path, pages=6)

    out_dir = split(str(pdf_path), None, "1-2,3-4,5-6")
    files = list(Path(out_dir).iterdir())
    assert len(files) == 3

    # Extract pages 2-3 (should produce 2 pages)
    new_file = tmp_path / "extracted.pdf"
    extract_pages(str(pdf_path), str(new_file), "2-3")
    doc = fitz.open(new_file)
    assert doc.page_count == 2
    doc.close()

    # Delete pages 2 and 3
    delete_pages(str(pdf_path), "2-3", replace=False)
    mod_file = pdf_path.with_name(pdf_path.stem + "_mod" + pdf_path.suffix)
    doc2 = fitz.open(mod_file)
    assert doc2.page_count == 4
    doc2.close()

    # Combine two files
    combined = tmp_path / "combined.pdf"
    combine([str(new_file), str(mod_file)], str(combined))
    doc3 = fitz.open(combined)
    assert doc3.page_count == 6
    doc3.close()


def test_convert_txt_to_pdf(tmp_path):
    txt = tmp_path / "sample.txt"
    txt.write_text("Hello\nWorld\n" * 10)

    from pdf_manager.pdf_tools import convert_to_pdf

    out = convert_to_pdf(str(txt))
    assert isinstance(out, Path)
    assert out.exists()
    doc = fitz.open(out)
    assert doc.page_count >= 1
    doc.close()


def test_convert_multiple_and_combine(tmp_path):
    txt1 = tmp_path / "one.txt"
    txt1.write_text("One\n" * 50)
    txt2 = tmp_path / "two.txt"
    txt2.write_text("Two\n" * 50)

    from pdf_manager.pdf_tools import convert_to_pdf

    combined = tmp_path / "combined.pdf"
    out = convert_to_pdf([str(txt1), str(txt2)], output=str(combined))
    assert isinstance(out, Path)
    assert out.exists()
    doc = fitz.open(out)
    assert doc.page_count >= 2
    doc.close()


def test_handle_pdf_convert_cmd(tmp_path, capsys):
    txt = tmp_path / "cli.txt"
    txt.write_text("CLI Test\n" * 5)
    from pdf_manager.pdf_tools import handle_pdf_command

    handle_pdf_command(["convert", str(txt)])
    captured = capsys.readouterr()
    assert "Converted file:" in captured.out or "Converted" in captured.out
