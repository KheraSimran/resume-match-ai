import os
import tempfile
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

async def extract_text_from_pdf(file: UploadFile) -> str:
    """
        Receives an uploaded PDF file, saves it temporarily (byte form),
        loads it with PyPDFLoader, and returns the text.
    """
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
    finally:
        os.unlink(tmp_path)

def split_text_into_chunks(text: str) -> list:
    """
    Splits a long text into smaller overlapping chunks.
    
    chunk_size=500: each chunk is ~500 characters
    chunk_overlap=50: chunks overlap by 50 chars so context isn't lost at boundaries
    """

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.create_documents([text])
