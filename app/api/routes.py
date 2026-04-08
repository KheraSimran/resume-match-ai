import uuid
from app.core.logger import get_logger
from app.services.matcher_service import resume_jd_match
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.pdf_service import extract_text_from_pdf, split_text_into_chunks

logger = get_logger(__name__)

router = APIRouter()

@router.get('/health')
async def health_check():
    logger.info("Health check endpoint called.")
    return {'status': 'ok'}

@router.post('/analyze')
async def analyze_resume(resume: UploadFile = File(...), job_description: str = Form(...)):
    """
    Main endpoint: accepts a resume PDF and job description text,
    returns ATS analysis.
    """
    logger.info("Analyze resume endpoint called.")
    
    if resume.content_type != 'application/pdf':
        logger.warning("Invalid resume content type.")
        raise HTTPException(status_code=400, detail='Only PDF files are accepted.')
    
    if not job_description.strip():
        logger.warning("Empty job description received.")
        raise HTTPException(status_code=400, detail='Job description cannot be empty.')
    
    try:
        resume_text = await extract_text_from_pdf(resume)

        if not resume_text.strip():
            logger.warning("No text extracted from resume PDF.")
            raise HTTPException(status_code=400, detail="Couldn't extract text from pdf.")
        
        resume_chunks = split_text_into_chunks(resume_text)

        collection_name = f"resume_{uuid.uuid4().hex[:8]}"

        resume_analysis = resume_jd_match(resume_chunks, job_description, collection_name)

        return {'success': True, 'data': resume_analysis}
    except HTTPException as http_exc:
        logger.error(f"HTTP exception occurred: {http_exc.detail}")
        raise
    except Exception as e:
        logger.error(f"Error analyzing resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error.")