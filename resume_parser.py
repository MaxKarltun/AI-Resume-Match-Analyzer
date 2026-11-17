from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile

from docx import Document
from lxml.etree import XMLSyntaxError
from pypdf import PdfReader
from pypdf.errors import PdfReadError


MAX_UPLOAD_BYTES = 5 * 1024 * 1024


class ResumeReadError(ValueError):
    pass


def extract_resume_text(content: bytes, filename: str) -> str:
    if not content:
        raise ResumeReadError("This file is empty. Upload a resume with text.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise ResumeReadError("The resume must be 5 MB or smaller.")

    extension = Path(filename).suffix.lower()
    if extension == ".txt":
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise ResumeReadError(
                "This text file is not UTF-8 encoded. Save it as UTF-8 or paste "
                "your resume into the text box."
            ) from error
    elif extension == ".pdf":
        try:
            reader = PdfReader(BytesIO(content))
            if reader.is_encrypted:
                raise ResumeReadError(
                    "Password-protected PDFs are not supported. "
                    "Upload an unlocked copy or paste your resume."
                )
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except PdfReadError as error:
            raise ResumeReadError(
                "This PDF could not be read. Export a new copy or paste your resume."
            ) from error
    elif extension == ".docx":
        try:
            document = Document(BytesIO(content))
            parts = [paragraph.text for paragraph in document.paragraphs]
            for table in document.tables:
                for row in table.rows:
                    parts.extend(cell.text for cell in row.cells)
            text = "\n".join(parts)
        except (BadZipFile, KeyError, ValueError, XMLSyntaxError) as error:
            raise ResumeReadError(
                "This Word file could not be read. Save it as a new .docx "
                "file or paste your resume."
            ) from error
    else:
        raise ResumeReadError("Upload a PDF, Word (.docx), or plain text (.txt) file.")

    if not text.strip():
        raise ResumeReadError(
            "No readable text was found. Scanned or image-only resumes need "
            "OCR first. Upload a text-based file or paste your resume."
        )
    return text.strip()
