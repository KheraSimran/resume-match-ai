import os
import tempfile
from fastapi import UploadFile
from app.core.logger import get_logger
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = get_logger(__name__)

async def extract_text_from_pdf(file: UploadFile) -> str:
    """
    Receives an uploaded PDF file, saves it temporarily (byte form),
    loads it with PyPDFLoader, and returns the text.
    """
    logger.info(f"Starting PDF extraction for file: {file.filename}")
    # PyPDFLoader needs a path to a file on disk in order to parse the text, 
    # so we save the file temporarily.
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        loader = PyPDFLoader(tmp_path)
        pages = loader.load()

        full_text = "\n".join([page.page_content for page in pages])
        return full_text
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        raise
    finally:
        os.unlink(tmp_path)
        logger.info("Text extraction from PDF completed.")

def split_text_into_chunks(text: str) -> list:
    """
    Splits a long text into smaller overlapping chunks.
    
    chunk_size=500: each chunk is ~500 characters
    chunk_overlap=50: chunks overlap by 50 chars so context isn't lost at boundaries
    """
    logger.debug("Splitting text into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.create_documents([text])
    logger.info(f"Created {len(chunks)} chunks")
    return chunks