from io import BytesIO
import unittest

from docx import Document
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from resume_parser import MAX_UPLOAD_BYTES, ResumeReadError, extract_resume_text


def make_pdf(text=None, password=None):
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    if text is not None:
        font = DictionaryObject({
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        })
        page[NameObject("/Resources")] = DictionaryObject({
            NameObject("/Font"): DictionaryObject({NameObject("/F1"): font}),
        })
        stream = DecodedStreamObject()
        stream.set_data(f"BT /F1 12 Tf 50 700 Td ({text}) Tj ET".encode("ascii"))
        page[NameObject("/Contents")] = stream
    if password is not None:
        writer.encrypt(password)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


class ResumeParserTests(unittest.TestCase):
    def test_utf8_text_and_bom(self):
        self.assertEqual(
            extract_resume_text(b"\xef\xbb\xbfPython SQL\n", "RESUME.TXT"),
            "Python SQL",
        )

    def test_docx_paragraphs_and_tables(self):
        document = Document()
        document.add_paragraph("Python and SQL")
        document.add_table(rows=1, cols=1).cell(0, 0).text = "AWS and Airflow"
        output = BytesIO()
        document.save(output)
        text = extract_resume_text(output.getvalue(), "resume.docx")
        self.assertIn("Python and SQL", text)
        self.assertIn("AWS and Airflow", text)

    def test_pdf_text(self):
        text = extract_resume_text(make_pdf("Python SQL AWS"), "resume.pdf")
        self.assertIn("Python SQL AWS", text)

    def test_encrypted_pdf(self):
        with self.assertRaisesRegex(ResumeReadError, "Password-protected"):
            extract_resume_text(make_pdf(password="test-password"), "resume.pdf")

    def test_pdf_without_text(self):
        with self.assertRaisesRegex(ResumeReadError, "No readable text"):
            extract_resume_text(make_pdf(), "resume.pdf")

    def test_invalid_inputs(self):
        cases = [
            (b"", "resume.txt", "empty"),
            (b" " * (MAX_UPLOAD_BYTES + 1), "resume.txt", "5 MB"),
            (b"\xff", "resume.txt", "UTF-8"),
            (b"   \n", "resume.txt", "No readable text"),
            (b"Python", "resume.doc", "Upload a PDF"),
            (b"not a pdf", "resume.pdf", "PDF could not be read"),
            (b"not a docx", "resume.docx", "Word file could not be read"),
        ]
        for content, filename, message in cases:
            with self.subTest(filename=filename, message=message):
                with self.assertRaisesRegex(ResumeReadError, message):
                    extract_resume_text(content, filename)


if __name__ == "__main__":
    unittest.main()
