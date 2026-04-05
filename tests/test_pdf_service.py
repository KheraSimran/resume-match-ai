import pytest
import io
from unittest.mock import patch, MagicMock, mock_open
from app.services.pdf_service import extract_text_from_pdf, split_text_into_chunks
from fastapi import UploadFile


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_upload_file(content: bytes, filename: str = "resume.pdf") -> UploadFile:
    """
    Creates a fake UploadFile object for testing.
    """
    return UploadFile(
        filename=filename,
        file=io.BytesIO(content)
    )


# ── extract_text_from_pdf ─────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.services.pdf_service.os.unlink")
@patch("app.services.pdf_service.PyPDFLoader")
@patch("app.services.pdf_service.tempfile.NamedTemporaryFile")
async def test_extract_text_returns_string(mock_tempfile, mock_loader_class, mock_unlink):
    """
    Happy path — verify we get a text string back from a PDF.
    
    We mock PyPDFLoader because we don't want tests depending on
    real PDF parsing.
    """
    # Set up the fake temp file
    mock_tmp = MagicMock()
    mock_tmp.name = "/tmp/fake_resume.pdf"
    mock_tmp.__enter__ = MagicMock(return_value=mock_tmp)
    mock_tmp.__exit__ = MagicMock(return_value=False)
    mock_tempfile.return_value = mock_tmp

    # Set up what PyPDFLoader should return
    mock_page = MagicMock()
    mock_page.page_content = "Simran Khera\nPython Developer\nDjango REST Framework"
    mock_loader_class.return_value.load.return_value = [mock_page]
    
    # Run the function
    upload = make_upload_file(b"%PDF fake content")
    result = await extract_text_from_pdf(upload)

    # Verify
    print(result)
    assert isinstance(result, str)
    assert "Simran Khera" in result
    assert "Python Developer" in result
    mock_unlink.assert_called_once_with("/tmp/fake_resume.pdf")


@pytest.mark.asyncio
@patch("app.services.pdf_service.os.unlink")
@patch("app.services.pdf_service.PyPDFLoader")
@patch("app.services.pdf_service.tempfile.NamedTemporaryFile")
async def test_extract_text_joins_multiple_pages(mock_tempfile, mock_loader_class, mock_unlink):
    """
    Verify that multi-page PDFs get all pages joined into one string.
    """
    mock_tmp = MagicMock()
    mock_tmp.name = "/tmp/fake_resume.pdf"
    mock_tmp.__enter__ = MagicMock(return_value=mock_tmp)
    mock_tmp.__exit__ = MagicMock(return_value=False)
    mock_tempfile.return_value = mock_tmp

    # Two pages
    page1 = MagicMock()
    page1.page_content = "Page one content"
    page2 = MagicMock()
    page2.page_content = "Page two content"
    mock_loader_class.return_value.load.return_value = [page1, page2]

    upload = make_upload_file(b"%PDF fake")
    result = await extract_text_from_pdf(upload)

    assert "Page one content" in result
    assert "Page two content" in result
    # Pages should be separated by newline
    assert result == "Page one content\nPage two content"
    mock_unlink.assert_called_once_with("/tmp/fake_resume.pdf")

@pytest.mark.asyncio
@patch("app.services.pdf_service.os.unlink")
@patch("app.services.pdf_service.PyPDFLoader")
@patch("app.services.pdf_service.tempfile.NamedTemporaryFile")
async def test_temp_file_deleted_even_on_error(
    mock_tempfile, mock_loader_class, mock_unlink
):
    """
    Critical test — verify cleanup happens even when PyPDFLoader crashes.
    This tests our finally block is actually working.
    """
    mock_tmp = MagicMock()
    mock_tmp.name = "/tmp/fake_resume.pdf"
    mock_tmp.__enter__ = MagicMock(return_value=mock_tmp)
    mock_tmp.__exit__ = MagicMock(return_value=False)
    mock_tempfile.return_value = mock_tmp

    # Make PyPDFLoader crash
    mock_loader_class.return_value.load.side_effect = Exception("PDF is corrupted")

    upload = make_upload_file(b"%PDF fake")

    with pytest.raises(Exception, match="PDF is corrupted"):
        await extract_text_from_pdf(upload)

    # unlink MUST have been called despite the crash
    mock_unlink.assert_called_once_with("/tmp/fake_resume.pdf")


# ── split_text_into_chunks ────────────────────────────────────────────────────

def test_split_returns_list():
    """Verify chunking returns a list."""
    text = "Python developer with 3 years experience building REST APIs with Django."
    chunks = split_text_into_chunks(text)
    assert isinstance(chunks, list)
    assert len(chunks) > 0


def test_split_long_text_creates_multiple_chunks():
    """
    Long text should be split into multiple chunks.
    We use a text longer than chunk_size=500 chars.
    """
    long_text = "Python developer. " * 100  # ~1800 chars, well over 500
    chunks = split_text_into_chunks(long_text)
    assert len(chunks) > 1


def test_split_short_text_stays_as_one_chunk():
    """Short text under the chunk size should stay as one chunk."""
    short_text = "Python developer with Django experience."
    chunks = split_text_into_chunks(short_text)
    assert len(chunks) == 1


def test_split_chunks_have_page_content():
    """
    Each chunk should be a LangChain Document object with page_content.
    This verifies LangChain is giving us back the right object type.
    """
    text = "Experienced software developer skilled in Python and Django REST Framework."
    chunks = split_text_into_chunks(text)
    for chunk in chunks:
        assert hasattr(chunk, "page_content")
        assert isinstance(chunk.page_content, str)
        assert len(chunk.page_content) > 0