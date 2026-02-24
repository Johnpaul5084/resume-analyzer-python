from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from app.api import dependencies as deps
from app.models.all_models import User
from app.services.ai_rewrite_service import AIRewriteService

router = APIRouter()

class RewriteRequest(BaseModel):
    resume_text: str
    job_description: str
    mode: Optional[str] = "ATS"  # "ATS" or "Creative"

class GrammarRequest(BaseModel):
    text: str

@router.post("/transform")
async def transform_resume(
    request: Request,
    rewrite_req: RewriteRequest,
    current_user: User = Depends(deps.get_current_user),
):
    """
    AI JD → ATS Resume Transformer
    Aligns resume content with a specific Job Description.
    """
    from app.main import limiter
    @limiter.limit("5/minute")
    async def _run(request, rewrite_req):
        return await AIRewriteService.rewrite_resume(
            resume_text=rewrite_req.resume_text,
            job_description=rewrite_req.job_description,
            mode=rewrite_req.mode
        )
    return await _run(request, rewrite_req)

@router.post("/enhance-grammar")
async def enhance_grammar(
    request: Request,
    grammar_req: GrammarRequest,
    current_user: User = Depends(deps.get_current_user),
):
    """
    AI Grammar & Clarity Enhancer
    Polishes resume text while maintaining original meaning.
    """
    from app.main import limiter
    @limiter.limit("5/minute")
    async def _run(request, grammar_req):
        enhanced_text = await AIRewriteService.grammar_enhance(grammar_req.text)
        return {"enhanced_text": enhanced_text}
    return await _run(request, grammar_req)
