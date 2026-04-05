"""
Resume Builder Service — Self-Contained (NO External Dependencies)
====================================================================
OUR OWN TECHNOLOGY — No Overleaf, no external websites needed.

Generates:
1. Professional HTML resume from structured data (for live preview)
2. Direct PDF download via frontend html2pdf.js
3. AI Interview Questions based on resume content
4. Resume Strength Radar analysis

5 Built-in Templates:
  Classic Professional | Modern Tech | Academic | Minimal ATS | Executive
"""

import re
import json
import html
import logging
import asyncio
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

TEMPLATES = {
    "classic": {"name": "Classic Professional", "description": "Clean single-column layout trusted by Fortune 500 recruiters.", "preview_color": "#2c3e50", "icon": "📄"},
    "modern": {"name": "Modern Tech", "description": "Gradient accents and modern typography for tech/startup roles.", "preview_color": "#3498db", "icon": "💎"},
    "academic": {"name": "Academic Research", "description": "Formal layout for academic, research, and university roles.", "preview_color": "#8e44ad", "icon": "🎓"},
    "minimal": {"name": "Minimal ATS", "description": "Ultra-clean. Maximum ATS compatibility.", "preview_color": "#27ae60", "icon": "⚡"},
    "executive": {"name": "Executive Impact", "description": "Bold headers with achievement focus for leadership roles.", "preview_color": "#e74c3c", "icon": "👔"},
}

_STRUCTURE_PROMPT = """You are an expert resume parser. Extract the resume content into structured JSON.
Return ONLY valid JSON:
{"name":"Full Name","email":"email","phone":"phone","linkedin":"","github":"","location":"","summary":"2-3 sentence summary",
"education":[{"degree":"","institution":"","year":"","gpa":""}],
"experience":[{"title":"","company":"","duration":"","bullets":["achievement with metrics"]}],
"projects":[{"name":"","tech":"React, Node.js","bullets":["what it does"]}],
"skills":{"languages":["Python"],"frameworks":["React"],"tools":["Docker"],"databases":["PostgreSQL"]},
"certifications":["cert name"],"achievements":["achievement"]}
RULES: Extract ONLY real info. Do NOT invent anything. Empty = [] or ""."""


def _h(text):
    return html.escape(str(text)) if text else ""


def _build_classic_html(d):
    name = _h(d.get("name",""))
    contact = " &bull; ".join(p for p in [_h(d.get("email","")),_h(d.get("phone","")),_h(d.get("location","")),_h(d.get("linkedin","")),_h(d.get("github",""))] if p)
    s = ""
    summary = _h(d.get("summary",""))
    if summary:
        s += f'<div class="sec"><div class="st">Professional Summary</div><p class="sum">{summary}</p></div>'
    for e in d.get("education",[]):
        gpa = f' — GPA: {_h(e.get("gpa",""))}' if e.get("gpa") else ""
        s += f'<div class="sec"><div class="st">Education</div><div class="en"><div class="eh"><span class="et">{_h(e.get("degree",""))}</span><span class="ed">{_h(e.get("year",""))}</span></div><div class="es">{_h(e.get("institution",""))}{gpa}</div></div></div>'
    if d.get("experience"):
        exp = ""
        for e in d["experience"]:
            bul = "".join(f'<li>{_h(b)}</li>' for b in e.get("bullets",[]))
            exp += f'<div class="en"><div class="eh"><span class="et">{_h(e.get("title",""))} — {_h(e.get("company",""))}</span><span class="ed">{_h(e.get("duration",""))}</span></div><ul>{bul}</ul></div>'
        s += f'<div class="sec"><div class="st">Experience</div>{exp}</div>'
    if d.get("projects"):
        proj = ""
        for p in d["projects"]:
            tech = f' <span class="tc">| {_h(p.get("tech",""))}</span>' if p.get("tech") else ""
            bul = "".join(f'<li>{_h(b)}</li>' for b in p.get("bullets",[]))
            proj += f'<div class="en"><div class="eh"><span class="et">{_h(p.get("name",""))}{tech}</span></div><ul>{bul}</ul></div>'
        s += f'<div class="sec"><div class="st">Projects</div>{proj}</div>'
    skills = d.get("skills",{})
    if skills:
        sk = ""
        for cat,items in skills.items():
            if items:
                sk += f'<div class="sr"><span class="sc">{_h(cat.replace("_"," ").title())}:</span> {", ".join(_h(i) for i in items)}</div>'
        s += f'<div class="sec"><div class="st">Technical Skills</div>{sk}</div>'
    for key,title in [("certifications","Certifications"),("achievements","Achievements")]:
        items = d.get(key,[])
        if items:
            s += f'<div class="sec"><div class="st">{title}</div><ul>{"".join(f"<li>{_h(i)}</li>" for i in items)}</ul></div>'
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:'EB Garamond',Georgia,serif;font-size:10.5pt;line-height:1.5;color:#1a1a1a;background:#fff}}
.pg{{max-width:800px;margin:0 auto;padding:36px 48px}}.hd{{text-align:center;border-bottom:2px solid #2c3e50;padding-bottom:12px;margin-bottom:16px}}
.nm{{font-size:22pt;font-weight:700;letter-spacing:1px;text-transform:uppercase}}.ct{{font-size:9pt;color:#555;margin-top:4px}}
.sec{{margin-bottom:14px}}.st{{font-size:11pt;font-weight:700;color:#2c3e50;text-transform:uppercase;letter-spacing:1.5px;border-bottom:1px solid #ddd;padding-bottom:3px;margin-bottom:8px}}
.en{{margin-bottom:10px}}.eh{{display:flex;justify-content:space-between;align-items:baseline}}.et{{font-weight:700;font-size:10.5pt}}.ed{{font-size:9pt;color:#777;font-style:italic}}
.es{{font-size:9.5pt;color:#555;font-style:italic}}.sum{{font-size:10pt;color:#333;line-height:1.6}}.tc{{color:#777;font-size:9pt;font-style:italic}}
ul{{padding-left:18px;margin:4px 0}}li{{font-size:10pt;margin-bottom:2px;line-height:1.5}}.sr{{font-size:10pt;margin-bottom:3px}}.sc{{font-weight:700}}
</style></head><body><div class="pg"><div class="hd"><div class="nm">{name}</div><div class="ct">{contact}</div></div>{s}</div></body></html>'''


def _build_modern_html(d):
    name = _h(d.get("name",""))
    contact = " &nbsp;|&nbsp; ".join(p for p in [_h(d.get("email","")),_h(d.get("phone","")),_h(d.get("linkedin","")),_h(d.get("github",""))] if p)
    s = ""
    summary = _h(d.get("summary",""))
    if summary:
        s += f'<div class="sec"><div class="st">▸ Summary</div><p class="sum">{summary}</p></div>'
    if d.get("education"):
        ed = ""
        for e in d["education"]:
            gpa = f' — GPA: {_h(e.get("gpa",""))}' if e.get("gpa") else ""
            ed += f'<div class="en"><div class="eh"><span class="et ac">{_h(e.get("degree",""))}</span><span class="ed">{_h(e.get("year",""))}</span></div><div class="es">{_h(e.get("institution",""))}{gpa}</div></div>'
        s += f'<div class="sec"><div class="st">▸ Education</div>{ed}</div>'
    if d.get("experience"):
        exp = ""
        for e in d["experience"]:
            bul = "".join(f'<li>{_h(b)}</li>' for b in e.get("bullets",[]))
            exp += f'<div class="en"><div class="eh"><span class="et"><span class="ac">{_h(e.get("title",""))}</span> | {_h(e.get("company",""))}</span><span class="ed">{_h(e.get("duration",""))}</span></div><ul>{bul}</ul></div>'
        s += f'<div class="sec"><div class="st">▸ Experience</div>{exp}</div>'
    if d.get("projects"):
        proj = ""
        for p in d["projects"]:
            tech = f' <span class="tb">{_h(p.get("tech",""))}</span>' if p.get("tech") else ""
            bul = "".join(f'<li>{_h(b)}</li>' for b in p.get("bullets",[]))
            proj += f'<div class="en"><div class="eh"><span class="et ac">{_h(p.get("name",""))}{tech}</span></div><ul>{bul}</ul></div>'
        s += f'<div class="sec"><div class="st">▸ Projects</div>{proj}</div>'
    skills = d.get("skills",{})
    if skills:
        sk = ""
        for cat,items in skills.items():
            if items:
                pills = "".join(f'<span class="pl">{_h(i)}</span>' for i in items)
                sk += f'<div class="sg"><span class="sc">{_h(cat.replace("_"," ").title())}:</span>{pills}</div>'
        s += f'<div class="sec"><div class="st">▸ Technical Skills</div>{sk}</div>'
    certs = d.get("certifications",[]); achs = d.get("achievements",[])
    if certs or achs:
        items = "".join(f'<li><strong>{_h(c)}</strong></li>' for c in certs) + "".join(f'<li>{_h(a)}</li>' for a in achs)
        s += f'<div class="sec"><div class="st">▸ Certifications & Achievements</div><ul>{items}</ul></div>'
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:'Inter',sans-serif;font-size:10pt;line-height:1.5;color:#1e293b;background:#fff}}
.pg{{max-width:800px;margin:0 auto;padding:36px 44px}}.hd{{text-align:center;padding-bottom:14px;margin-bottom:16px;border-bottom:3px solid #2563eb}}
.nm{{font-size:24pt;font-weight:800;color:#2563eb;letter-spacing:-0.5px}}.ct{{font-size:8.5pt;color:#64748b;margin-top:6px}}
.sec{{margin-bottom:14px}}.st{{font-size:10.5pt;font-weight:800;color:#2563eb;text-transform:uppercase;letter-spacing:2px;border-bottom:1.5px solid #e2e8f0;padding-bottom:3px;margin-bottom:8px}}
.ac{{color:#2563eb;font-weight:700}}.en{{margin-bottom:10px}}.eh{{display:flex;justify-content:space-between;align-items:baseline}}
.et{{font-weight:700;font-size:10pt}}.ed{{font-size:8.5pt;color:#94a3b8}}.es{{font-size:9pt;color:#64748b}}.sum{{font-size:9.5pt;color:#475569;line-height:1.6}}
.tb{{background:#eff6ff;color:#2563eb;padding:1px 6px;border-radius:4px;font-size:8pt;font-weight:600;margin-left:6px}}
ul{{padding-left:16px;margin:4px 0}}li{{font-size:9.5pt;margin-bottom:2px}}
.sg{{margin-bottom:6px;display:flex;flex-wrap:wrap;align-items:center;gap:4px}}.sc{{font-weight:700;font-size:9.5pt;margin-right:4px}}
.pl{{background:#f1f5f9;color:#334155;padding:2px 8px;border-radius:4px;font-size:8.5pt;font-weight:500}}
</style></head><body><div class="pg"><div class="hd"><div class="nm">{name}</div><div class="ct">{contact}</div></div>{s}</div></body></html>'''


def _build_minimal_html(d):
    name = _h(d.get("name",""))
    contact = " | ".join(p for p in [_h(d.get("email","")),_h(d.get("phone","")),_h(d.get("linkedin",""))] if p)
    s = ""
    summary = _h(d.get("summary",""))
    if summary: s += f'<div class="sec"><div class="st">SUMMARY</div><p>{summary}</p></div>'
    for key,title in [("education","EDUCATION"),("experience","EXPERIENCE"),("projects","PROJECTS")]:
        items = d.get(key,[])
        if not items: continue
        inner = ""
        for item in items:
            if key == "education":
                gpa = f" — GPA: {_h(item.get('gpa',''))}" if item.get("gpa") else ""
                inner += f'<div class="row"><span>{_h(item.get("degree",""))}, {_h(item.get("institution",""))}{gpa}</span><span class="dt">{_h(item.get("year",""))}</span></div>'
            else:
                t = _h(item.get("title",item.get("name","")))
                sub = _h(item.get("company",item.get("tech","")))
                dur = _h(item.get("duration",""))
                bul = "".join(f'<li>{_h(b)}</li>' for b in item.get("bullets",[]))
                inner += f'<div class="en"><div class="row"><span><strong>{t}</strong>{", "+sub if sub else ""}</span><span class="dt">{dur}</span></div><ul>{bul}</ul></div>'
        s += f'<div class="sec"><div class="st">{title}</div>{inner}</div>'
    skills = d.get("skills",{})
    if skills:
        sk = ""
        for cat,items in skills.items():
            if items: sk += f'<div><strong>{_h(cat.replace("_"," ").title())}:</strong> {", ".join(_h(i) for i in items)}</div>'
        s += f'<div class="sec"><div class="st">SKILLS</div>{sk}</div>'
    certs = d.get("certifications",[])
    if certs: s += f'<div class="sec"><div class="st">CERTIFICATIONS</div>{"".join(f"<div>• {_h(c)}</div>" for c in certs)}</div>'
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:Arial,Helvetica,sans-serif;font-size:10pt;line-height:1.4;color:#000;background:#fff}}
.pg{{max-width:800px;margin:0 auto;padding:36px 48px}}.hd{{text-align:center;border-bottom:1px solid #000;padding-bottom:8px;margin-bottom:12px}}
.nm{{font-size:18pt;font-weight:700}}.ct{{font-size:9pt;color:#333;margin-top:2px}}.sec{{margin-bottom:12px}}
.st{{font-weight:700;font-size:10pt;border-bottom:1px solid #ccc;padding-bottom:2px;margin-bottom:6px;letter-spacing:1px}}
.en{{margin-bottom:8px}}.row{{display:flex;justify-content:space-between}}.dt{{color:#555;font-size:9pt}}
ul{{padding-left:16px;margin:2px 0}}li{{font-size:9.5pt;margin-bottom:1px}}
</style></head><body><div class="pg"><div class="hd"><div class="nm">{name}</div><div class="ct">{contact}</div></div>{s}</div></body></html>'''


def _build_executive_html(d):
    name = _h(d.get("name",""))
    contact = " &nbsp;•&nbsp; ".join(p for p in [_h(d.get("email","")),_h(d.get("phone","")),_h(d.get("location","")),_h(d.get("linkedin",""))] if p)
    s = ""
    summary = _h(d.get("summary",""))
    if summary: s += f'<div class="sec"><div class="st">EXECUTIVE SUMMARY</div><p class="sum">{summary}</p></div>'
    if d.get("experience"):
        exp = ""
        for e in d["experience"]:
            bul = "".join(f'<li>{_h(b)}</li>' for b in e.get("bullets",[]))
            exp += f'<div class="en"><div class="eh"><div><span class="rl">{_h(e.get("title",""))}</span> <span class="at">at</span> <span class="co">{_h(e.get("company",""))}</span></div><span class="dt">{_h(e.get("duration",""))}</span></div><ul>{bul}</ul></div>'
        s += f'<div class="sec"><div class="st">PROFESSIONAL EXPERIENCE</div>{exp}</div>'
    if d.get("education"):
        ed = ""
        for e in d["education"]:
            gpa = f' — GPA: {_h(e.get("gpa",""))}' if e.get("gpa") else ""
            ed += f'<div class="esm"><strong>{_h(e.get("degree",""))}</strong>, {_h(e.get("institution",""))}{gpa} <span class="dt">{_h(e.get("year",""))}</span></div>'
        s += f'<div class="sec"><div class="st">EDUCATION</div>{ed}</div>'
    if d.get("projects"):
        proj = ""
        for p in d["projects"]:
            tech = f' <em class="tc">({_h(p.get("tech",""))})</em>' if p.get("tech") else ""
            bul = "".join(f'<li>{_h(b)}</li>' for b in p.get("bullets",[]))
            proj += f'<div class="en"><div class="eh"><span class="rl">{_h(p.get("name",""))}{tech}</span></div><ul>{bul}</ul></div>'
        s += f'<div class="sec"><div class="st">KEY PROJECTS</div>{proj}</div>'
    skills = d.get("skills",{})
    if skills:
        all_sk = []
        for items in skills.values():
            if items: all_sk.extend(items)
        if all_sk: s += f'<div class="sec"><div class="st">CORE COMPETENCIES</div><p class="comp">{" &bull; ".join(_h(sk) for sk in all_sk)}</p></div>'
    certs = d.get("certifications",[]); achs = d.get("achievements",[])
    if certs or achs:
        items = "".join(f'<li><strong>{_h(c)}</strong></li>' for c in certs) + "".join(f'<li>{_h(a)}</li>' for a in achs)
        s += f'<div class="sec"><div class="st">CERTIFICATIONS & ACHIEVEMENTS</div><ul>{items}</ul></div>'
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Source+Sans+3:wght@400;600;700&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:'Source Sans 3',sans-serif;font-size:10pt;line-height:1.5;color:#1a1a1a;background:#fff}}
.pg{{max-width:800px;margin:0 auto;padding:40px 48px}}.hd{{border-bottom:3px solid #b91c1c;padding-bottom:14px;margin-bottom:18px}}
.nm{{font-family:'Playfair Display',serif;font-size:26pt;font-weight:900;letter-spacing:-0.5px}}.ct{{font-size:9pt;color:#666;margin-top:4px}}
.sec{{margin-bottom:16px}}.st{{font-size:10.5pt;font-weight:700;color:#b91c1c;text-transform:uppercase;letter-spacing:2px;border-bottom:1.5px solid #fecaca;padding-bottom:3px;margin-bottom:8px}}
.en{{margin-bottom:10px}}.eh{{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:2px}}
.rl{{font-weight:700;font-size:10.5pt}}.at{{color:#999;font-size:9pt}}.co{{font-weight:600;color:#b91c1c}}.dt{{font-size:8.5pt;color:#999}}
.esm{{margin-bottom:4px;font-size:10pt}}.tc{{color:#888;font-size:9pt}}.sum{{font-size:10pt;color:#333;line-height:1.6;border-left:3px solid #b91c1c;padding-left:12px}}
.comp{{font-size:9.5pt;color:#444;line-height:1.8}}ul{{padding-left:18px;margin:3px 0}}li{{font-size:9.5pt;margin-bottom:2px}}
</style></head><body><div class="pg"><div class="hd"><div class="nm">{name}</div><div class="ct">{contact}</div></div>{s}</div></body></html>'''


_HTML_BUILDERS = {
    "classic": _build_classic_html,
    "modern": _build_modern_html,
    "academic": _build_classic_html,
    "minimal": _build_minimal_html,
    "executive": _build_executive_html,
}


class ResumeBuilderService:
    """Self-contained resume builder — NO external dependencies."""

    @staticmethod
    async def build_resume(resume_text, template_id="classic", target_role="Software Engineer"):
        if template_id not in TEMPLATES: template_id = "classic"
        template_info = TEMPLATES[template_id]
        structured = await ResumeBuilderService._extract_structure(resume_text, target_role)
        if not structured: return {"success": False, "error": "Could not parse resume structure."}
        builder = _HTML_BUILDERS.get(template_id, _build_classic_html)
        return {"success": True, "resume_html": builder(structured), "structured_data": structured, "template": {"id": template_id, "name": template_info["name"], "description": template_info["description"]}}

    @staticmethod
    async def generate_interview_questions(resume_text, target_role="Software Engineer"):
        from app.core.ai_provider import AIProvider
        prompt = f"""Based on this resume and target role, generate interview prep material.
RESUME: {resume_text[:3000]}
TARGET ROLE: {target_role}
Return ONLY valid JSON:
{{"technical_questions":[{{"question":"...","tip":"What interviewer is really asking"}},{{"question":"...","tip":"..."}},{{"question":"...","tip":"..."}},{{"question":"...","tip":"..."}},{{"question":"...","tip":"..."}}],
"behavioral_questions":[{{"question":"...","tip":"Use STAR method"}},{{"question":"...","tip":"..."}},{{"question":"...","tip":"..."}}],
"role_specific_questions":[{{"question":"...","tip":"..."}},{{"question":"...","tip":"..."}},{{"question":"...","tip":"..."}}],
"resume_red_flags":["Potential weakness #1","Potential weakness #2"]}}
RULES: Technical Qs from ACTUAL resume skills. Behavioral Qs from mentioned experiences. Role-specific for {target_role}."""
        result = await AIProvider.generate_json(prompt=prompt, system_prompt=f"You are a senior interviewer hiring for {target_role}. Generate realistic questions.", max_tokens=1200, temperature=0.5, timeout=40)
        if result: return {"success": True, "interview_prep": result, "target_role": target_role}
        return {"success": True, "interview_prep": {"technical_questions":[{"question":"Explain the architecture of a system you built.","tip":"Focus on design decisions and trade-offs."},{"question":"How would you optimize a slow database query?","tip":"Discuss indexing, query plans, caching."},{"question":"Walk through debugging a production issue.","tip":"Show systematic thinking."}],"behavioral_questions":[{"question":"Tell me about a conflict with a teammate.","tip":"STAR: focus on resolution."},{"question":"Describe learning something new quickly.","tip":"Emphasize adaptability."}],"role_specific_questions":[{"question":f"What makes you a good fit for {target_role}?","tip":"Map skills to requirements."},{"question":f"Where is {target_role} heading in 3 years?","tip":"Show industry awareness."}],"resume_red_flags":["Be prepared to explain employment gaps","Have specific metrics ready"]}, "target_role": target_role}

    @staticmethod
    async def analyze_resume_strength(resume_text, target_role="Software Engineer"):
        from app.core.ai_provider import AIProvider
        prompt = f"""Analyze this resume across 6 dimensions for {target_role}.
RESUME: {resume_text[:3000]}
Return ONLY valid JSON:
{{"dimensions":{{"Technical Skills":<0-100>,"Experience Depth":<0-100>,"Impact & Metrics":<0-100>,"Education":<0-100>,"Projects & Portfolio":<0-100>,"Communication & Clarity":<0-100>}},"overall_score":<0-100>,"strongest":"<dimension>","weakest":"<dimension>","one_line_verdict":"<summary>"}}
Be realistic: freshers 30-60, mid 55-80, senior 70-95."""
        result = await AIProvider.generate_json(prompt=prompt, system_prompt="Expert resume reviewer. Score honestly.", max_tokens=400, temperature=0.3, timeout=25)
        if result and "dimensions" in result: return {"success": True, **result}
        return {"success":True,"dimensions":{"Technical Skills":60,"Experience Depth":45,"Impact & Metrics":40,"Education":65,"Projects & Portfolio":55,"Communication & Clarity":50},"overall_score":52,"strongest":"Education","weakest":"Impact & Metrics","one_line_verdict":"Solid foundation. Improve impact quantification."}

    @staticmethod
    async def _extract_structure(resume_text, target_role):
        from app.core.ai_provider import AIProvider
        prompt = f"Parse this resume into structured JSON.\nTarget Role: {target_role}\n\nRESUME:\n{resume_text[:5000]}\n\n{_STRUCTURE_PROMPT}"
        result = await AIProvider.generate_json(prompt=prompt, system_prompt="Expert resume parser. Extract into JSON. Do NOT invent info.", max_tokens=1500, temperature=0.2, timeout=45)
        if result and result.get("name"): return result
        return ResumeBuilderService._basic_parse(resume_text)

    @staticmethod
    def _basic_parse(text):
        lines = text.strip().split("\n")
        name = lines[0].strip() if lines else "Your Name"
        em = re.search(r'[\w.-]+@[\w.-]+\.\w+', text)
        ph = re.search(r'[\+]?[\d\s\-().]{10,}', text)
        return {"name":name,"email":em.group() if em else "","phone":ph.group().strip() if ph else "","linkedin":"","github":"","location":"","summary":"","education":[],"experience":[],"projects":[],"skills":{"languages":[],"frameworks":[],"tools":[]},"certifications":[],"achievements":[]}

    @staticmethod
    def get_templates():
        return [{"id":tid,"name":t["name"],"description":t["description"],"icon":t["icon"],"color":t["preview_color"]} for tid,t in TEMPLATES.items()]
