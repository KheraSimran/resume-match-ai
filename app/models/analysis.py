from pydantic import BaseModel, Field
from typing import List

class ResumeAnalysis(BaseModel):
    ats_score: int = Field(..., ge=0, le=100)
    missing_keywords: List[str]
    rewritten_bullets: List[str]
    score_explanation: str