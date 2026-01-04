from pathlib import Path
import os
from typing import List, Iterable, Optional, Union
import fitz  # PyMuPDF

# Optional import for DOCX support
try:
    import docx  # type: ignore
except Exception:
    docx = None

def handle_pdf_command(args: List[str]) -> None:
    """Dispatch PDF subcommands and validate arguments.

    Supported subcommands: split, merge, extract, delete, search
    """
    if not args:
        print("No PDF subcommand provided.")
        return
    sub = args[0]
    try:
        if sub == "split":
            # pdf split <file> <ranges> [delete]
            if len(args) < 3:
                print("Usage: pdf split <file> <ranges> [delete]")
                return
            filename, ranges = args[1], args[2]
            delete = (len(args) > 3 and args[3].lower() in ("true", "1", "yes", "delete"))
            outdir = split(filename, ranges, delete_og=delete)
            print(f"Split files created under: {outdir}")
        elif sub == "merge":
            # pdf merge <file1> <file2> ... <out>
            if len(args) < 3:
                print("Usage: pdf merge <file1> <file2> ... <out>")
                return
            *inputs, out = args[1:]
            combine(inputs, out)
            print(f"Merged file created: {out}")
        elif sub == "extract":
            # pdf extract <file> <pages> <new>
            if len(args) < 4:
                print("Usage: pdf extract <file> <pages> <new>")
                return
            filename, pages, new = args[1], args[2], args[3]
            extract_pages(filename, new, pages)
            print(f"Extracted pages saved to {new}")
        elif sub == "delete":
            # pdf delete <file> <pages> [replace]
            if len(args) < 3:
                print("Usage: pdf delete <file> <pages> [replace]")
                return
            filename, pages = args[1], args[2]
            replace = (len(args) > 3 and args[3].lower() in ("true", "1", "yes", "replace"))
            delete_pages(filename, pages, replace=replace)
            print("Pages removed.")
        elif sub == "search":
            print("Search functionality is not yet implemented.")
        elif sub == "convert":
            # pdf convert <file_or_dir> [out] [delete]
            if len(args) < 2:
                print("Usage: pdf convert <file|dir|file1 file2 ...> [out.pdf] [delete]")
                return
            inputs = args[1:]
            delete = False
            out = None
            # detect flags
            if "delete" in inputs:
                delete = True
                inputs = [i for i in inputs if i != "delete"]
            # if last arg looks like output pdf and more than one input, treat it as out
            if len(inputs) > 1 and inputs[-1].lower().endswith('.pdf'):
                out = inputs[-1]
                inputs = inputs[:-1]

            converted = convert_to_pdf(inputs, output=out, delete_og=delete)
            if isinstance(converted, list):
                print(f"Converted {len(converted)} files to PDF:")
                for p in converted:
                    print(f" - {p}")
            else:
                print(f"Converted file: {converted}")
        else:
            print(f"{sub} is not a valid PDF command.")
    except Exception as e:
        print(f"PDF command failed: {e}")

def split(filename, pdf_doc, pages, delete_og=False):
    """
    Split a PDF file into multiple PDFs according to comma-separated page ranges.

    Args:
        filename: Path to the PDF file to split.
        pdf_doc: (Not used) kept for compatibility with earlier signature.
        pages: String like "1-3,4,5-6" describing ranges to extract.
        delete_og: If True, delete the original file after splitting.

    Returns:
        Path to the directory where split files are stored.
    """
    filename = Path(filename)
    if not filename.is_file():
        raise FileNotFoundError(f"PDF not found: {filename}")

    new_dir = filename.stem + "_split"
    os.makedirs(new_dir, exist_ok=True)

    pdf_doc_obj = fitz.open(filename)
    page_ranges = pages.split(",")
    index = 1

    for p in page_ranges:
        new_fname = filename.stem + f"_{index}" + filename.suffix
        out_path = Path(new_dir) / new_fname

        # Parse range properly
        if "-" in p:
            start, end = map(int, p.split("-"))
            from_page = max(0, start - 1)
            to_page = max(0, end - 1)
        else:
            single = int(p)
            from_page = single - 1
            to_page = single - 1

        new_doc = fitz.open()
        # fitz.insert_pdf expects 0-indexed inclusive ranges
        new_doc.insert_pdf(pdf_doc_obj, from_page=from_page, to_page=to_page)
        new_doc.save(out_path)
        new_doc.close()
        index += 1

    pdf_doc_obj.close()
    if delete_og:
        os.remove(filename)

    return Path(new_dir)

def extract_pages(filename: str, new_filename: str, pages: str) -> None:
    """Extract specific pages or ranges from `filename` and write to `new_filename`.

    Pages are specified like "1,3,5-7" (1-indexed inclusive ranges).
    """
    filename = Path(filename)
    if not filename.is_file():
        raise FileNotFoundError(f"PDF not found: {filename}")

    pdf_doc = fitz.open(filename)
    pages_list: List[int] = []
    for token in pages.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            start, end = map(int, token.split("-"))
            pages_list.extend(list(range(start - 1, end)))
        else:
            pages_list.append(int(token) - 1)

    # Validate pages
    pages_list = [p for p in pages_list if 0 <= p < pdf_doc.page_count]
    if not pages_list:
        raise ValueError("No valid pages selected for extraction")

    new_doc = fitz.open()
    for p in pages_list:
        new_doc.insert_pdf(pdf_doc, from_page=p, to_page=p)
    new_doc.save(new_filename)
    new_doc.close()
    pdf_doc.close()

def delete_pages(filename: str, pages: str, replace: bool = False) -> None:
    """Delete one or more pages (or ranges) from a PDF.

    `pages` is comma-separated like "2,5-7" (1-indexed ranges).
    If `replace` is True, overwrite the original file; otherwise save as `<stem>_mod<suffix>`.
    """
    filename = Path(filename)
    if not filename.is_file():
        raise FileNotFoundError(f"PDF not found: {filename}")

    pdf_doc = fitz.open(filename)
    tokens = [t.strip() for t in pages.split(",") if t.strip()]
    # Collect ranges to delete in reverse-sorted order to avoid index shift problems
    to_delete: List[int] = []
    for tok in tokens:
        if "-" in tok:
            start, end = map(int, tok.split("-"))
            to_delete.extend(list(range(start - 1, end)))
        else:
            to_delete.append(int(tok) - 1)

    to_delete = sorted(set(p for p in to_delete if 0 <= p < pdf_doc.page_count), reverse=True)
    for p in to_delete:
        pdf_doc.delete_page(p)

    if replace:
        pdf_doc.save(filename)
    else:
        new_doc_name = filename.parent / (filename.stem + "_mod" + filename.suffix)
        pdf_doc.save(str(new_doc_name))
    pdf_doc.close()


def combine(filenames: List[str], new_filename: str, delete_og: bool = False) -> Path:
    # filenames is a list of pdf filenames to combine
    # new_filename is the name of the new combined pdf
    # if delete_og is True, the original files will be deleted after combining
    # otherwise, they will be kept
    # the order of the filenames in the list will be the order in the new pdf
    # returns the path to the new combined pdf 
    doc_new = fitz.open() # open the new document
    for pdf in filenames:
        if not Path(pdf).is_file():
            raise FileNotFoundError(f"PDF to merge not found: {pdf}")
        pdf_doc = fitz.open(pdf)
        doc_new.insert_pdf(pdf_doc)
        pdf_doc.close()
        if (delete_og):
            os.remove(pdf)

    doc_new.save(new_filename)
    doc_new.close()
    return Path(new_filename)


def convert_to_pdf(
    inputs: Union[str, Iterable[str]],
    output: Optional[str] = None,
    delete_og: bool = False,
) -> Union[Path, List[Path]]:
    """Convert one or more files to PDF.

    - If `inputs` is a single path to a file, convert that file and return the PDF path.
    - If `inputs` is a directory path, convert all files in that directory and return list of PDF paths.
    - If `inputs` is an iterable of files and `output` is provided and endswith .pdf, the converted PDFs will be
      combined into `output` and a single Path is returned. Otherwise a list of individual PDF Paths is returned.

    Supported conversions: image files (png/jpg/gif/bmp/tiff), text files, basic docx -> text conversion (if python-docx installed).
    """
    def _is_image(p: Path) -> bool:
        return p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif"}

    def _is_text(p: Path) -> bool:
        return p.suffix.lower() in {".txt", ".md"}

    def _is_docx(p: Path) -> bool:
        return p.suffix.lower() == ".docx"

    single_input = False
    if isinstance(inputs, str):
        inputs_list = [inputs]
        single_input = True
    else:
        inputs_list = list(inputs)

    resolved_inputs: List[Path] = []
    for item in inputs_list:
        p = Path(item)
        if p.is_dir():
            for f in p.iterdir():
                if f.is_file():
                    resolved_inputs.append(f)
        else:
            resolved_inputs.append(p)

    if not resolved_inputs:
        raise FileNotFoundError("No input files found to convert.")

    out_paths: List[Path] = []

    for src in resolved_inputs:
        if not src.exists():
            raise FileNotFoundError(f"Input not found: {src}")

        dest = None
        if single_input and output:
            dest = Path(output)
        else:
            dest = src.with_suffix('.pdf')

        # choose conversion method
        if _is_image(src):
            doc = fitz.open()
            # use pixmap to get image size
            pix = fitz.Pixmap(str(src))
            page = doc.new_page(width=pix.width, height=pix.height)
            page.insert_image(fitz.Rect(0, 0, pix.width, pix.height), filename=str(src))
            doc.save(dest)
            doc.close()
        elif _is_text(src):
            with open(src, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [l.rstrip('\n') for l in f]
            doc = fitz.open()
            # naive pagination: roughly 45 lines per page
            per_page = 45
            for i in range(0, len(lines), per_page):
                page = doc.new_page()
                text = "\n".join(lines[i:i+per_page])
                page.insert_text((72, 72), text)
            doc.save(dest)
            doc.close()
        elif _is_docx(src):
            if docx is None:
                raise RuntimeError("python-docx is required to convert .docx files to PDF (install python-docx)")
            d = docx.Document(str(src))
            paras = [p.text for p in d.paragraphs if p.text]
            doc = fitz.open()
            per_page = 45
            # flatten paragraphs into lines
            lines: List[str] = []
            for p in paras:
                for line in p.split('\n'):
                    lines.append(line)
            for i in range(0, len(lines), per_page):
                page = doc.new_page()
                page.insert_text((72, 72), "\n".join(lines[i:i+per_page]))
            doc.save(dest)
            doc.close()
        else:
            raise NotImplementedError(f"Conversion for {src.suffix} is not supported")

        out_paths.append(dest)
        if delete_og:
            try:
                os.remove(src)
            except Exception:
                pass

    # if an explicit output PDF was requested and multiple outputs were generated, combine
    if output and len(out_paths) > 1:
        combine([str(p) for p in out_paths], output)
        return Path(output)

    return out_paths[0] if single_input else out_paths