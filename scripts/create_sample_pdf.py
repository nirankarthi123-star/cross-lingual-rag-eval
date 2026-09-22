"""Helper script to create a clean, valid sample PDF for testing PDFLoader."""
from pathlib import Path
import pypdf

def create_sample_pdf(output_path: Path):
    # Minimal valid PDF with standard text
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        b"4 0 obj\n<< /Length 260 >>\nstream\n"
        b"BT\n/F1 14 Tf\n50 720 Td\n(Campus Central Library Rules and Borrowing Guidelines) Tj\n"
        b"/F1 10 Tf\n0 -30 Td\n(Students may borrow up to 5 books simultaneously for a period of 14 calendar days.) Tj\n"
        b"0 -20 Td\n(Overdue fines accumulate at the rate of 10 INR per day per book after the due date.) Tj\n"
        b"0 -20 Td\n(Reference materials, journals, and thesis dissertations cannot be checked out.) Tj\n"
        b"ET\nendstream\nendobj\n"
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"xref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000244 00000 n \n0000000557 00000 n \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n626\n%%EOF\n"
    )
    with open(output_path, "wb") as f:
        f.write(pdf_content)

    # Validate with pypdf
    reader = pypdf.PdfReader(str(output_path))
    text = reader.pages[0].extract_text()
    print("Successfully generated and verified PDF. Extracted text preview:")
    print(text.strip())

if __name__ == "__main__":
    out = Path("data/documents/campus_library_guide.pdf")
    out.parent.mkdir(parents=True, exist_ok=True)
    create_sample_pdf(out)
