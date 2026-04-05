from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from app.api import dependencies as deps
from app.models.all_models import User
from app.services.ai_rewrite_service import AIRewriteService
from app.services.company_ats_service import CompanyATSService
from app.services.latex_resume_service import LaTeXResumeService

router = APIRouter()

class RewriteRequest(BaseModel):
    resume_text: str
    job_description: str
    mode: Optional[str] = "ATS"  # "ATS" or "Creative"

class GrammarRequest(BaseModel):
    text: str

class CompanyATSRequest(BaseModel):
    resume_text: str
    target_role: Optional[str] = "Software Engineer"
    companies: Optional[List[str]] = None  # None = all companies

class SingleCompanyATSRequest(BaseModel):
    resume_text: str
    company_id: str
    target_role: Optional[str] = "Software Engineer"

class LaTeXRequest(BaseModel):
    resume_text: str
    template_id: Optional[str] = "classic"  # classic, modern, academic, minimal, executive
    target_role: Optional[str] = "Software Engineer"

class FullPipelineRequest(BaseModel):
    resume_text: str
    target_role: str
    template_id: Optional[str] = "classic"
    companies: Optional[List[str]] = None
    mode: Optional[str] = "ATS"


# ─────────────────────────────────────────────────────────────
# EXISTING ENDPOINTS
# ─────────────────────────────────────────────────────────────

@router.post("/transform")
async def transform_resume(
    request: Request,
    rewrite_req: RewriteRequest,
    current_user: User = Depends(deps.get_current_user),
):
    """AI Resume Transformer — rewrites resume for a specific role or JD."""
    from app.main import limiter

    @limiter.limit("20/minute")
    async def _run(request, rewrite_req):
        jd = rewrite_req.job_description or ""
        if len(jd.strip()) < 80:
            result = await AIRewriteService.rewrite_section(
                text=rewrite_req.resume_text,
                section_type="Entire Resume",
                target_role=jd.strip() or "Software Engineer",
                mode=rewrite_req.mode,
            )
        else:
            result = await AIRewriteService.rewrite_section(
                text=rewrite_req.resume_text,
                section_type="Entire Resume",
                job_description=jd,
                mode=rewrite_req.mode,
            )
        return {"success": True, "rewritten_resume": result}

    return await _run(request, rewrite_req)


@router.post("/enhance-grammar")
async def enhance_grammar(
    request: Request,
    grammar_req: GrammarRequest,
    current_user: User = Depends(deps.get_current_user),
):
    """AI Grammar & Clarity Enhancer."""
    from app.main import limiter
    @limiter.limit("20/minute")
    async def _run(request, grammar_req):
        enhanced_text = await AIRewriteService.grammar_enhance(grammar_req.text)
        return {"enhanced_text": enhanced_text}
    return await _run(request, grammar_req)


# ─────────────────────────────────────────────────────────────
# NEW: COMPANY-SPECIFIC ATS SCORING
# ─────────────────────────────────────────────────────────────

@router.post("/company-ats")
async def score_company_ats(
    ats_req: CompanyATSRequest,
    current_user: User = Depends(deps.get_current_user),
):
    """
    🏢 Company-Specific ATS Simulator
    Scores resume against multiple company ATS systems simultaneously.
    Shows how Google, Amazon, Microsoft, TCS, Infosys would score the same resume.
    """
    return await CompanyATSService.score_all_companies(
        resume_text=ats_req.resume_text,
        target_role=ats_req.target_role,
        companies=ats_req.companies,
    )


@router.post("/company-ats/single")
async def score_single_company(
    ats_req: SingleCompanyATSRequest,
    current_user: User = Depends(deps.get_current_user),
):
    """Score resume against a single company's ATS system."""
    return await CompanyATSService.score_for_company(
        resume_text=ats_req.resume_text,
        company_id=ats_req.company_id,
        target_role=ats_req.target_role,
    )


@router.get("/company-ats/companies")
async def list_companies(
    current_user: User = Depends(deps.get_current_user),
):
    """List available company ATS profiles."""
    return CompanyATSService.get_available_companies()


# ─────────────────────────────────────────────────────────────
# SELF-CONTAINED RESUME BUILDER (NO OVERLEAF NEEDED)
# ─────────────────────────────────────────────────────────────

@router.post("/build-resume")
async def build_resume(
    latex_req: LaTeXRequest,
    current_user: User = Depends(deps.get_current_user),
):
    """
    📝 Self-Contained Resume Builder (OUR OWN TECHNOLOGY)
    Generates professional HTML resume with live preview + PDF download.
    No Overleaf, no external dependencies.
    5 templates: Classic, Modern, Academic, Minimal ATS, Executive.
    """
    from app.services.resume_builder_service import ResumeBuilderService
    return await ResumeBuilderService.build_resume(
        resume_text=latex_req.resume_text,
        template_id=latex_req.template_id,
        target_role=latex_req.target_role,
    )


@router.post("/latex")
async def generate_latex_resume(
    latex_req: LaTeXRequest,
    current_user: User = Depends(deps.get_current_user),
):
    """LaTeX code export (bonus feature — for users who want Overleaf)."""
    return await LaTeXResumeService.generate_latex(
        resume_text=latex_req.resume_text,
        template_id=latex_req.template_id,
        target_role=latex_req.target_role,
    )


@router.get("/templates")
async def list_templates(
    current_user: User = Depends(deps.get_current_user),
):
    """List available resume templates."""
    from app.services.resume_builder_service import ResumeBuilderService
    return ResumeBuilderService.get_templates()


# ─────────────────────────────────────────────────────────────
# AI INTERVIEW PREP ENGINE (UNIQUE)
# ─────────────────────────────────────────────────────────────

class InterviewPrepRequest(BaseModel):
    resume_text: str
    target_role: Optional[str] = "Software Engineer"

@router.post("/interview-prep")
async def generate_interview_prep(
    req: InterviewPrepRequest,
    current_user: User = Depends(deps.get_current_user),
):
    """
    🎯 AI Interview Prep Engine
    Generates technical, behavioral, and role-specific interview questions
    based on resume content. Includes preparation tips for each question.
    """
    from app.services.resume_builder_service import ResumeBuilderService
    return await ResumeBuilderService.generate_interview_questions(
        resume_text=req.resume_text,
        target_role=req.target_role,
    )


# ─────────────────────────────────────────────────────────────
# RESUME STRENGTH RADAR (UNIQUE)
# ─────────────────────────────────────────────────────────────

@router.post("/strength-radar")
async def resume_strength_radar(
    req: InterviewPrepRequest,
    current_user: User = Depends(deps.get_current_user),
):
    """
    📊 Resume Strength Radar
    Analyzes resume across 6 dimensions and returns scores for spider chart.
    Dimensions: Technical Skills, Experience, Impact, Education, Projects, Communication.
    """
    from app.services.resume_builder_service import ResumeBuilderService
    return await ResumeBuilderService.analyze_resume_strength(
        resume_text=req.resume_text,
        target_role=req.target_role,
    )


# ─────────────────────────────────────────────────────────────
# FULL AUTO-PIPELINE (SELF-CONTAINED)
# ─────────────────────────────────────────────────────────────

@router.post("/pipeline")
async def full_pipeline(
    req: FullPipelineRequest,
    current_user: User = Depends(deps.get_current_user),
):
    """
    🚀 FULL AUTO-PIPELINE (Our Own Technology)
    1. Company ATS scoring
    2. Grammar enhancement
    3. AI rewrite for target role
    4. Professional HTML resume (self-contained, downloadable)
    5. Interview prep questions
    6. Resume strength analysis
    """
    import asyncio
    from app.services.resume_builder_service import ResumeBuilderService

    # Step 1+2: ATS scoring AND grammar enhancement (concurrent)
    ats_task = CompanyATSService.score_all_companies(
        resume_text=req.resume_text,
        target_role=req.target_role,
        companies=req.companies,
    )
    grammar_task = AIRewriteService.grammar_enhance(req.resume_text)

    ats_results, grammar_text = await asyncio.gather(ats_task, grammar_task)

    # Step 3: AI rewrite the grammar-enhanced text
    rewritten_text = await AIRewriteService.rewrite_section(
        text=grammar_text,
        section_type="Entire Resume",
        target_role=req.target_role,
        mode=req.mode,
    )

    # Step 4+5+6: Resume build, interview prep, strength radar (concurrent)
    build_task = ResumeBuilderService.build_resume(rewritten_text, req.template_id, req.target_role)
    interview_task = ResumeBuilderService.generate_interview_questions(req.resume_text, req.target_role)
    strength_task = ResumeBuilderService.analyze_resume_strength(req.resume_text, req.target_role)

    build_result, interview_result, strength_result = await asyncio.gather(
        build_task, interview_task, strength_task
    )

    return {
        "success": True,
        "pipeline_results": {
            "step_1_ats": ats_results,
            "step_2_grammar": {
                "original": req.resume_text[:500] + "...",
                "enhanced": grammar_text,
            },
            "step_3_rewrite": {
                "rewritten_resume": rewritten_text,
                "target_role": req.target_role,
                "mode": req.mode,
            },
            "step_4_resume": build_result,
            "step_5_interview": interview_result,
            "step_6_strength": strength_result,
        }
    }


# ─────────────────────────────────────────────────────────────
# AUTO-APPLY ENGINE (12+ PLATFORMS)
# ─────────────────────────────────────────────────────────────

class AutoApplyRequest(BaseModel):
    resume_text: str
    target_role: str
    location: Optional[str] = "India"
    platforms: Optional[List[str]] = None  # None = all platforms
    max_jobs: Optional[int] = 10

@router.post("/auto-apply")
async def search_and_auto_apply(
    req: AutoApplyRequest,
    current_user: User = Depends(deps.get_current_user),
):
    """
    🚀 Auto-Apply Engine
    Searches real jobs via SerpAPI + generates apply links for 12 platforms:
    LinkedIn, Indeed, Glassdoor, Naukri, Monster, Wellfound, Dice,
    Internshala, Instahyre, SimplyHired, Foundit, Hirist.
    Also generates an AI cover letter optimized for the target role.
    """
    from app.services.auto_apply_service import AutoApplyService
    return await AutoApplyService.search_and_apply(
        resume_text=req.resume_text,
        target_role=req.target_role,
        location=req.location,
        max_jobs=req.max_jobs,
    )


@router.post("/apply-links")
async def generate_apply_links(
    req: AutoApplyRequest,
    current_user: User = Depends(deps.get_current_user),
):
    """
    🔗 Quick Apply Links
    Generates optimized apply URLs for all 12 job platforms.
    No SerpAPI needed — instant link generation.
    """
    from app.services.auto_apply_service import AutoApplyService
    return await AutoApplyService.generate_apply_links(
        resume_text=req.resume_text,
        target_role=req.target_role,
        location=req.location,
        platforms=req.platforms,
    )


@router.get("/platforms")
async def list_job_platforms(
    current_user: User = Depends(deps.get_current_user),
):
    """List all supported job platforms for auto-apply."""
    from app.services.auto_apply_service import AutoApplyService
    return AutoApplyService.get_platforms()
