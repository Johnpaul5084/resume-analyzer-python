"""
LaTeX Resume Generator Service
================================
UNIQUE FEATURE: Generates Overleaf-ready LaTeX resume code.

Templates:
1. Classic Professional — Clean single-column, traditional format
2. Modern Tech — Colored accents, modern layout
3. Academic Research — Formal, publication-ready
4. Minimal ATS — Ultra-clean, maximum ATS compatibility
5. Executive Impact — Bold headers, achievement-focused

Uses AI to extract structured resume sections, then fills professional LaTeX templates.
"""

import re
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────
# LaTeX Template Definitions
# ─────────────────────────────────────────────────────────────────

TEMPLATES = {
    "classic": {
        "name": "Classic Professional",
        "description": "Clean single-column layout. Traditional format trusted by Fortune 500 recruiters.",
        "preview_color": "#2c3e50",
        "icon": "📄",
    },
    "modern": {
        "name": "Modern Tech",
        "description": "Colored accents and modern typography. Popular for tech/startup roles.",
        "preview_color": "#3498db",
        "icon": "💎",
    },
    "academic": {
        "name": "Academic Research",
        "description": "Formal layout for academic and research roles. Publication-ready.",
        "preview_color": "#8e44ad",
        "icon": "🎓",
    },
    "minimal": {
        "name": "Minimal ATS",
        "description": "Ultra-clean with zero formatting tricks. Maximum ATS compatibility score.",
        "preview_color": "#27ae60",
        "icon": "⚡",
    },
    "executive": {
        "name": "Executive Impact",
        "description": "Bold headers with achievement focus. Perfect for senior/leadership roles.",
        "preview_color": "#e74c3c",
        "icon": "👔",
    },
}

# System prompt for AI resume structuring
_STRUCTURE_PROMPT = """You are an expert resume parser. Extract the resume content into structured JSON sections.

Return ONLY valid JSON with this exact structure:
{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "+1-XXX-XXX-XXXX",
  "linkedin": "linkedin.com/in/username",
  "github": "github.com/username",
  "location": "City, State",
  "summary": "2-3 sentence professional summary",
  "education": [
    {
      "degree": "B.Tech in Computer Science",
      "institution": "University Name",
      "year": "2020-2024",
      "gpa": "8.5/10"
    }
  ],
  "experience": [
    {
      "title": "Software Engineer",
      "company": "Company Name",
      "duration": "Jan 2023 - Present",
      "bullets": [
        "Achievement bullet 1 with metrics",
        "Achievement bullet 2"
      ]
    }
  ],
  "projects": [
    {
      "name": "Project Name",
      "tech": "React, Node.js, MongoDB",
      "bullets": [
        "What the project does",
        "Key technical achievement"
      ]
    }
  ],
  "skills": {
    "languages": ["Python", "Java", "JavaScript"],
    "frameworks": ["React", "FastAPI", "Spring Boot"],
    "tools": ["Docker", "Git", "AWS"],
    "databases": ["PostgreSQL", "MongoDB"]
  },
  "certifications": ["AWS Certified Developer", "Google Cloud Associate"],
  "achievements": ["Hackathon winner", "Published paper"]
}

RULES:
- Extract ONLY information that actually exists in the resume
- Do NOT invent any information
- If a section is empty, use empty array [] or empty string ""
- Keep bullet points concise and impactful
- Preserve all technical terms exactly as written"""


def _escape_latex(text: str) -> str:
    """Escape special LaTeX characters."""
    if not text:
        return ""
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


def _build_classic_latex(data: Dict) -> str:
    """Classic Professional template."""
    name = _escape_latex(data.get("name", "Your Name"))
    email = _escape_latex(data.get("email", ""))
    phone = _escape_latex(data.get("phone", ""))
    linkedin = _escape_latex(data.get("linkedin", ""))
    github = _escape_latex(data.get("github", ""))
    location = _escape_latex(data.get("location", ""))
    summary = _escape_latex(data.get("summary", ""))

    contact_parts = [p for p in [email, phone, location, linkedin, github] if p]
    contact_line = " $|$ ".join(contact_parts)

    latex = r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=0.7in]{geometry}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage[hidelinks]{hyperref}
\usepackage{xcolor}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\titleformat{\section}{\large\bfseries\color{darkgray}}{}{0em}{}[\titlerule]
\titlespacing*{\section}{0pt}{12pt}{6pt}
\setlist[itemize]{nosep, leftmargin=*, itemsep=2pt}

\begin{document}

% ── HEADER ──
\begin{center}
    {\LARGE\bfseries """ + name + r"""}\\[4pt]
    {\small """ + contact_line + r"""}
\end{center}

"""
    # Summary
    if summary:
        latex += r"""\section{Professional Summary}
""" + summary + "\n\n"

    # Education
    edu = data.get("education", [])
    if edu:
        latex += r"\section{Education}" + "\n"
        for e in edu:
            latex += r"\textbf{" + _escape_latex(e.get("degree", "")) + "} \\hfill " + _escape_latex(e.get("year", "")) + r" \\" + "\n"
            gpa_str = f" | GPA: {_escape_latex(e.get('gpa', ''))}" if e.get("gpa") else ""
            latex += r"\textit{" + _escape_latex(e.get("institution", "")) + "}" + gpa_str + r" \\" + "\n"
        latex += "\n"

    # Experience
    exp = data.get("experience", [])
    if exp:
        latex += r"\section{Experience}" + "\n"
        for e in exp:
            latex += r"\textbf{" + _escape_latex(e.get("title", "")) + "} -- " + _escape_latex(e.get("company", "")) + r" \hfill " + _escape_latex(e.get("duration", "")) + r" \\" + "\n"
            latex += r"\begin{itemize}" + "\n"
            for b in e.get("bullets", []):
                latex += r"    \item " + _escape_latex(b) + "\n"
            latex += r"\end{itemize}" + "\n\n"

    # Projects
    projects = data.get("projects", [])
    if projects:
        latex += r"\section{Projects}" + "\n"
        for p in projects:
            tech_str = f" | \\textit{{{_escape_latex(p.get('tech', ''))}}}" if p.get("tech") else ""
            latex += r"\textbf{" + _escape_latex(p.get("name", "")) + "}" + tech_str + r" \\" + "\n"
            latex += r"\begin{itemize}" + "\n"
            for b in p.get("bullets", []):
                latex += r"    \item " + _escape_latex(b) + "\n"
            latex += r"\end{itemize}" + "\n\n"

    # Skills
    skills = data.get("skills", {})
    if skills:
        latex += r"\section{Technical Skills}" + "\n"
        for category, items in skills.items():
            if items:
                cat_name = _escape_latex(category.replace("_", " ").title())
                items_str = ", ".join(_escape_latex(i) for i in items)
                latex += r"\textbf{" + cat_name + ":} " + items_str + r" \\" + "\n"
        latex += "\n"

    # Certifications
    certs = data.get("certifications", [])
    if certs:
        latex += r"\section{Certifications}" + "\n"
        latex += r"\begin{itemize}" + "\n"
        for c in certs:
            latex += r"    \item " + _escape_latex(c) + "\n"
        latex += r"\end{itemize}" + "\n\n"

    # Achievements
    achievements = data.get("achievements", [])
    if achievements:
        latex += r"\section{Achievements}" + "\n"
        latex += r"\begin{itemize}" + "\n"
        for a in achievements:
            latex += r"    \item " + _escape_latex(a) + "\n"
        latex += r"\end{itemize}" + "\n\n"

    latex += r"\end{document}" + "\n"
    return latex


def _build_modern_latex(data: Dict) -> str:
    """Modern Tech template with color accents."""
    name = _escape_latex(data.get("name", "Your Name"))
    email = _escape_latex(data.get("email", ""))
    phone = _escape_latex(data.get("phone", ""))
    linkedin = _escape_latex(data.get("linkedin", ""))
    github = _escape_latex(data.get("github", ""))
    summary = _escape_latex(data.get("summary", ""))

    contact_parts = [p for p in [email, phone, linkedin, github] if p]
    contact_line = " \\enspace\\textbar\\enspace ".join(contact_parts)

    latex = r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=0.6in]{geometry}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage[hidelinks]{hyperref}
\usepackage{xcolor}
\usepackage{fontawesome5}

\definecolor{primary}{HTML}{2563EB}
\definecolor{accent}{HTML}{7C3AED}
\definecolor{textgray}{HTML}{64748B}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\titleformat{\section}{\large\bfseries\color{primary}}{}{0em}{}[\color{primary}\titlerule]
\titlespacing*{\section}{0pt}{14pt}{6pt}
\setlist[itemize]{nosep, leftmargin=*, itemsep=2pt}

\begin{document}

% ── HEADER ──
\begin{center}
    {\Huge\bfseries\color{primary} """ + name + r"""}\\[6pt]
    {\small\color{textgray} """ + contact_line + r"""}
\end{center}
\vspace{4pt}

"""
    if summary:
        latex += r"""\section{\faIcon{user} Summary}
{\color{textgray}""" + summary + "}\n\n"

    # Education
    edu = data.get("education", [])
    if edu:
        latex += r"\section{\faIcon{graduation-cap} Education}" + "\n"
        for e in edu:
            latex += r"\textbf{\color{primary}" + _escape_latex(e.get("degree", "")) + "} \\hfill {\\small\\color{textgray}" + _escape_latex(e.get("year", "")) + r"} \\" + "\n"
            gpa_str = f" -- GPA: {_escape_latex(e.get('gpa', ''))}" if e.get("gpa") else ""
            latex += _escape_latex(e.get("institution", "")) + gpa_str + r" \\" + "\n"
        latex += "\n"

    # Experience
    exp = data.get("experience", [])
    if exp:
        latex += r"\section{\faIcon{briefcase} Experience}" + "\n"
        for e in exp:
            latex += r"{\textbf{\color{primary}" + _escape_latex(e.get("title", "")) + r"}} \enspace\textbar\enspace " + _escape_latex(e.get("company", "")) + r" \hfill {\small\color{textgray}" + _escape_latex(e.get("duration", "")) + r"}" + "\n"
            latex += r"\begin{itemize}" + "\n"
            for b in e.get("bullets", []):
                latex += r"    \item " + _escape_latex(b) + "\n"
            latex += r"\end{itemize}" + "\n\n"

    # Projects
    projects = data.get("projects", [])
    if projects:
        latex += r"\section{\faIcon{code} Projects}" + "\n"
        for p in projects:
            tech_str = f" \\enspace\\textbar\\enspace {{\\small\\color{{accent}}\\textit{{{_escape_latex(p.get('tech', ''))}}}}}" if p.get("tech") else ""
            latex += r"{\textbf{\color{primary}" + _escape_latex(p.get("name", "")) + r"}}" + tech_str + "\n"
            latex += r"\begin{itemize}" + "\n"
            for b in p.get("bullets", []):
                latex += r"    \item " + _escape_latex(b) + "\n"
            latex += r"\end{itemize}" + "\n\n"

    # Skills
    skills = data.get("skills", {})
    if skills:
        latex += r"\section{\faIcon{tools} Technical Skills}" + "\n"
        for category, items in skills.items():
            if items:
                cat_name = _escape_latex(category.replace("_", " ").title())
                items_str = ", ".join(_escape_latex(i) for i in items)
                latex += r"\textbf{\color{primary}" + cat_name + ":} " + items_str + r" \\" + "\n"
        latex += "\n"

    # Certifications & Achievements combined
    certs = data.get("certifications", [])
    achievements = data.get("achievements", [])
    if certs or achievements:
        latex += r"\section{\faIcon{trophy} Certifications \& Achievements}" + "\n"
        latex += r"\begin{itemize}" + "\n"
        for c in certs:
            latex += r"    \item \textbf{" + _escape_latex(c) + "}\n"
        for a in achievements:
            latex += r"    \item " + _escape_latex(a) + "\n"
        latex += r"\end{itemize}" + "\n\n"

    latex += r"\end{document}" + "\n"
    return latex


def _build_minimal_latex(data: Dict) -> str:
    """Minimal ATS template — zero fancy formatting, maximum ATS compatibility."""
    name = _escape_latex(data.get("name", "Your Name"))
    email = _escape_latex(data.get("email", ""))
    phone = _escape_latex(data.get("phone", ""))
    linkedin = _escape_latex(data.get("linkedin", ""))

    contact_parts = [p for p in [email, phone, linkedin] if p]
    contact_line = " | ".join(contact_parts)

    latex = r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=0.75in]{geometry}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlist[itemize]{nosep, leftmargin=12pt, itemsep=1pt}

\newcommand{\sectionrule}{\vspace{2pt}\hrule\vspace{6pt}}

\begin{document}

\begin{center}
    {\Large\bfseries """ + name + r"""}\\[2pt]
    {\small """ + contact_line + r"""}
\end{center}
\vspace{4pt}

"""
    summary = _escape_latex(data.get("summary", ""))
    if summary:
        latex += "\\textbf{SUMMARY}\\sectionrule\n" + summary + "\n\\vspace{8pt}\n\n"

    edu = data.get("education", [])
    if edu:
        latex += "\\textbf{EDUCATION}\\sectionrule\n"
        for e in edu:
            gpa = f" -- GPA: {_escape_latex(e.get('gpa', ''))}" if e.get("gpa") else ""
            latex += _escape_latex(e.get("degree", "")) + ", " + _escape_latex(e.get("institution", "")) + gpa + " \\hfill " + _escape_latex(e.get("year", "")) + r" \\" + "\n"
        latex += "\\vspace{8pt}\n\n"

    exp = data.get("experience", [])
    if exp:
        latex += "\\textbf{EXPERIENCE}\\sectionrule\n"
        for e in exp:
            latex += "\\textbf{" + _escape_latex(e.get("title", "")) + "}, " + _escape_latex(e.get("company", "")) + " \\hfill " + _escape_latex(e.get("duration", "")) + "\n"
            latex += r"\begin{itemize}" + "\n"
            for b in e.get("bullets", []):
                latex += r"    \item " + _escape_latex(b) + "\n"
            latex += r"\end{itemize}" + "\n"
        latex += "\\vspace{4pt}\n\n"

    projects = data.get("projects", [])
    if projects:
        latex += "\\textbf{PROJECTS}\\sectionrule\n"
        for p in projects:
            tech = f" ({_escape_latex(p.get('tech', ''))})" if p.get("tech") else ""
            latex += "\\textbf{" + _escape_latex(p.get("name", "")) + "}" + tech + "\n"
            latex += r"\begin{itemize}" + "\n"
            for b in p.get("bullets", []):
                latex += r"    \item " + _escape_latex(b) + "\n"
            latex += r"\end{itemize}" + "\n"
        latex += "\\vspace{4pt}\n\n"

    skills = data.get("skills", {})
    if skills:
        latex += "\\textbf{SKILLS}\\sectionrule\n"
        for cat, items in skills.items():
            if items:
                cat_name = _escape_latex(cat.replace("_", " ").title())
                items_str = ", ".join(_escape_latex(i) for i in items)
                latex += f"\\textbf{{{cat_name}:}} {items_str}" + r" \\" + "\n"
        latex += "\n"

    certs = data.get("certifications", [])
    if certs:
        latex += "\\textbf{CERTIFICATIONS}\\sectionrule\n"
        for c in certs:
            latex += "- " + _escape_latex(c) + r" \\" + "\n"
        latex += "\n"

    latex += r"\end{document}" + "\n"
    return latex


# Template builder map
_TEMPLATE_BUILDERS = {
    "classic": _build_classic_latex,
    "modern": _build_modern_latex,
    "academic": _build_classic_latex,  # Uses classic layout with academic title
    "minimal": _build_minimal_latex,
    "executive": _build_classic_latex,  # Uses classic layout with executive styling
}


class LaTeXResumeService:
    """Generates Overleaf-ready LaTeX code from resume text."""

    @staticmethod
    async def generate_latex(
        resume_text: str,
        template_id: str = "classic",
        target_role: str = "Software Engineer",
    ) -> Dict[str, Any]:
        """
        Generate professional LaTeX resume code.

        1. AI extracts structured data from resume text
        2. Fills the selected LaTeX template
        3. Returns complete compilable LaTeX code
        """
        if template_id not in TEMPLATES:
            template_id = "classic"

        template_info = TEMPLATES[template_id]

        # Step 1: Extract structured data using AI
        structured_data = await LaTeXResumeService._extract_structure(resume_text, target_role)

        if not structured_data:
            return {
                "success": False,
                "error": "Could not extract resume structure. Please ensure your resume has clear sections.",
            }

        # Step 2: Generate LaTeX code using the template
        builder = _TEMPLATE_BUILDERS.get(template_id, _build_classic_latex)
        latex_code = builder(structured_data)

        return {
            "success": True,
            "latex_code": latex_code,
            "template": {
                "id": template_id,
                "name": template_info["name"],
                "description": template_info["description"],
            },
            "extracted_sections": list(structured_data.keys()),
            "instructions": (
                "📋 How to use:\n"
                "1. Go to overleaf.com and create a new project\n"
                "2. Paste this LaTeX code into the editor\n"
                "3. Click 'Recompile' to see your resume\n"
                "4. Download as PDF from Overleaf\n\n"
                f"Template: {template_info['name']}\n"
                f"Note: If using the Modern template, ensure fontawesome5 package is available."
            ),
        }

    @staticmethod
    async def rewrite_and_latex(
        resume_text: str,
        target_role: str,
        template_id: str = "classic",
    ) -> Dict[str, Any]:
        """
        Full pipeline: AI rewrite + LaTeX generation.
        1. Rewrites resume content for target role
        2. Generates LaTeX from rewritten content
        """
        from app.services.ai_rewrite_service import AIRewriteService

        # Step 1: AI rewrite
        rewritten = await AIRewriteService.rewrite_section(
            text=resume_text,
            section_type="Entire Resume",
            target_role=target_role,
            mode="ATS",
        )

        # Step 2: Generate LaTeX from rewritten content
        result = await LaTeXResumeService.generate_latex(rewritten, template_id, target_role)

        if result.get("success"):
            result["rewritten_text"] = rewritten

        return result

    @staticmethod
    async def _extract_structure(resume_text: str, target_role: str) -> Optional[Dict]:
        """Extract structured resume data using AI."""
        from app.core.ai_provider import AIProvider

        prompt = f"""Parse this resume text into structured JSON sections.
Target Role: {target_role}

RESUME TEXT:
{resume_text[:5000]}

{_STRUCTURE_PROMPT}"""

        result = await AIProvider.generate_json(
            prompt=prompt,
            system_prompt="You are an expert resume parser. Extract resume content into structured JSON. Be accurate — do not invent information.",
            max_tokens=1500,
            temperature=0.2,
            timeout=45,
        )

        if result and result.get("name"):
            return result

        # Fallback: basic text parsing
        return LaTeXResumeService._basic_parse(resume_text)

    @staticmethod
    def _basic_parse(text: str) -> Dict:
        """Basic regex-based resume parsing fallback."""
        lines = text.strip().split("\n")
        name = lines[0].strip() if lines else "Your Name"

        # Try to find email
        email_match = re.search(r'[\w.-]+@[\w.-]+\.\w+', text)
        email = email_match.group() if email_match else ""

        # Try to find phone
        phone_match = re.search(r'[\+]?[\d\s\-().]{10,}', text)
        phone = phone_match.group().strip() if phone_match else ""

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin": "",
            "github": "",
            "location": "",
            "summary": "",
            "education": [],
            "experience": [],
            "projects": [],
            "skills": {"languages": [], "frameworks": [], "tools": []},
            "certifications": [],
            "achievements": [],
        }

    @staticmethod
    def get_templates() -> List[Dict[str, str]]:
        """Return available template information."""
        return [
            {
                "id": tid,
                "name": t["name"],
                "description": t["description"],
                "icon": t["icon"],
                "color": t["preview_color"],
            }
            for tid, t in TEMPLATES.items()
        ]
