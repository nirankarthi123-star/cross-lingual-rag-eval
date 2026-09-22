import json
from pathlib import Path
import pytest
from backend.retrieval.loaders import (
    CSVLoader,
    DocumentLoadingError,
    JSONLoader,
    LoaderRegistry,
    PDFLoader,
    TXTLoader,
    UnsupportedFileTypeError,
)


def test_txt_loader(tmp_path: Path):
    txt_file = tmp_path / "sample.txt"
    txt_file.write_text("Title: Library Regulations\n\nBooks can be borrowed for 14 days.", encoding="utf-8")

    loader = TXTLoader()
    docs = loader.load(txt_file)

    assert len(docs) == 1
    doc = docs[0]
    assert doc.document_type == "txt"
    assert "Library Regulations" in doc.title
    assert "Books can be borrowed for 14 days." in doc.text
    assert doc.document_id is not None
    assert doc.ingestion_timestamp is not None


def test_csv_loader(tmp_path: Path):
    csv_file = tmp_path / "faq.csv"
    csv_file.write_text(
        "Question,Answer,Category\n"
        "How to apply for leave?,Submit form HR-1 to supervisor,HR\n"
        "What is wifi password?,Visit IT desk with student ID,IT\n",
        encoding="utf-8"
    )

    loader = CSVLoader()
    docs = loader.load(csv_file)

    assert len(docs) == 2
    assert docs[0].title == "How to apply for leave?"
    assert "Submit form HR-1" in docs[0].text
    assert docs[0].metadata["Category"] == "HR"
    assert docs[1].title == "What is wifi password?"


def test_json_loader(tmp_path: Path):
    json_file = tmp_path / "items.json"
    data = [
        {"title": "UPI Limits", "content": "Daily maximum limit is 100,000 INR.", "channel": "mobile"},
        {"topic": "ATM PIN", "body": "Never share your PIN with anyone.", "channel": "atm"},
    ]
    json_file.write_text(json.dumps(data), encoding="utf-8")

    loader = JSONLoader()
    docs = loader.load(json_file)

    assert len(docs) == 2
    assert docs[0].title == "UPI Limits"
    assert "100,000 INR" in docs[0].text
    assert docs[0].metadata["channel"] == "mobile"
    assert docs[1].title == "ATM PIN"


def test_malformed_json_error(tmp_path: Path):
    bad_json = tmp_path / "corrupt.json"
    bad_json.write_text("{ unclosed json: ", encoding="utf-8")

    loader = JSONLoader()
    with pytest.raises(DocumentLoadingError):
        loader.load(bad_json)


def test_loader_registry_unsupported_type(tmp_path: Path):
    registry = LoaderRegistry()
    fake_file = tmp_path / "archive.zip"
    fake_file.touch()

    with pytest.raises(UnsupportedFileTypeError):
        registry.load_file(fake_file)


def test_pdf_loader_existing_sample():
    sample_pdf = Path("data/documents/campus_library_guide.pdf")
    if sample_pdf.exists():
        loader = PDFLoader()
        docs = loader.load(sample_pdf)
        assert len(docs) == 1
        assert docs[0].document_type == "pdf"
        assert "Library" in docs[0].text or "Rules" in docs[0].text
