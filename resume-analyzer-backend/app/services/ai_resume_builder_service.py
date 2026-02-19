"""
AI Resume Builder Service - Generate professional resumes using AI
"""
import google.generativeai as genai
from app.core.config import settings
import json
from typing import Dict, Any, Optional

class AIResumeBuilderService:
    """Service for AI-powered resume generation"""
    
    @staticmethod
    async def generate_resume_from_chat(
        user_info: Dict[str, Any],
        target_role: str = "Software Engineer",
        experience_level: str = "Mid-Level"
    ) -> Dict[str, Any]:
        """
        Generate a complete resume from user information using conversational AI
        
        Args:
            user_info: Dictionary containing user's background info
            target_role: Target job role
            experience_level: Entry/Mid/Senior level
            
        Returns:
            Complete resume structure
        """
        
        if not settings.GEMINI_API_KEY:
            return AIResumeBuilderService._generate_template_resume(user_info, target_role)
        
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
You are an expert resume writer. Generate a professional, ATS-optimized resume for a {experience_level} {target_role}.

User Information:
{json.dumps(user_info, indent=2)}

Generate a complete resume with the following sections:
1. Professional Summary (3-4 lines, impactful)
2. Technical Skills (categorized)
3. Work Experience (3-4 positions with bullet points using STAR method)
4. Education
5. Projects (2-3 impressive projects)
6. Certifications (if applicable)

Requirements:
- Use action verbs (Developed, Implemented, Led, etc.)
- Include metrics and quantifiable achievements
- Optimize for ATS with relevant keywords
- Make it professional and modern
- Focus on {target_role} specific skills

Return ONLY a valid JSON object with this structure:
{{
    "summary": "Professional summary text",
    "skills": {{
        "technical": ["skill1", "skill2"],
        "soft": ["skill1", "skill2"]
    }},
    "experience": [
        {{
            "title": "Job Title",
            "company": "Company Name",
            "duration": "Jan 2020 - Present",
            "achievements": ["Achievement 1", "Achievement 2"]
        }}
    ],
    "education": [
        {{
            "degree": "Degree Name",
            "institution": "University Name",
            "year": "2020",
            "gpa": "3.8/4.0"
        }}
    ],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Brief description",
            "technologies": ["Tech1", "Tech2"],
            "link": "github.com/..."
        }}
    ],
    "certifications": ["Cert 1", "Cert 2"]
}}
"""
            
            response = model.generate_content(prompt)
            
            # Parse JSON from response
            response_text = response.text.strip()
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            resume_data = json.loads(response_text.strip())
            
            return {
                "success": True,
                "resume": resume_data,
                "target_role": target_role,
                "experience_level": experience_level
            }
            
        except Exception as e:
            print(f"AI Resume Generation Error: {e}")
            return AIResumeBuilderService._generate_template_resume(user_info, target_role)
    
    @staticmethod
    def _generate_template_resume(user_info: Dict[str, Any], target_role: str) -> Dict[str, Any]:
        """Fallback template-based resume generation"""
        
        name = user_info.get("name", "John Doe")
        email = user_info.get("email", "john@example.com")
        phone = user_info.get("phone", "+1-234-567-8900")
        
        return {
            "success": True,
            "resume": {
                "personal_info": {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "location": user_info.get("location", "San Francisco, CA")
                },
                "summary": f"Results-driven {target_role} with expertise in modern technologies and proven track record of delivering high-quality solutions. Passionate about innovation and continuous learning.",
                "skills": {
                    "technical": ["Python", "JavaScript", "React", "Node.js", "SQL", "AWS", "Docker", "Git"],
                    "soft": ["Leadership", "Communication", "Problem-Solving", "Team Collaboration"]
                },
                "experience": [
                    {
                        "title": f"Senior {target_role}",
                        "company": "Tech Corp",
                        "duration": "Jan 2021 - Present",
                        "achievements": [
                            "Led development of scalable microservices architecture serving 1M+ users",
                            "Improved system performance by 40% through optimization initiatives",
                            "Mentored team of 5 junior developers"
                        ]
                    },
                    {
                        "title": target_role,
                        "company": "StartupXYZ",
                        "duration": "Jun 2019 - Dec 2020",
                        "achievements": [
                            "Developed and deployed 10+ features using agile methodology",
                            "Reduced bug count by 30% through comprehensive testing",
                            "Collaborated with cross-functional teams"
                        ]
                    }
                ],
                "education": [
                    {
                        "degree": "Bachelor of Science in Computer Science",
                        "institution": "University of Technology",
                        "year": "2019",
                        "gpa": "3.7/4.0"
                    }
                ],
                "projects": [
                    {
                        "name": "AI-Powered Resume Analyzer",
                        "description": "Full-stack application for resume analysis and job matching",
                        "technologies": ["React", "FastAPI", "PostgreSQL", "AI/ML"],
                        "link": "github.com/user/resume-analyzer"
                    }
                ],
                "certifications": [
                    "AWS Certified Solutions Architect",
                    "Google Cloud Professional"
                ]
            },
            "target_role": target_role,
            "experience_level": "Mid-Level",
            "note": "Template-based generation (AI unavailable)"
        }
    
    @staticmethod
    async def optimize_bullet_point(
        bullet_point: str,
        target_role: str
    ) -> str:
        """
        Optimize a single bullet point for ATS and impact
        """
        
        if not settings.GEMINI_API_KEY:
            return bullet_point
        
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
Rewrite this resume bullet point to be more impactful and ATS-optimized for a {target_role} role:

Original: {bullet_point}

Requirements:
- Start with a strong action verb
- Include quantifiable metrics if possible
- Make it concise (1-2 lines max)
- Use keywords relevant to {target_role}
- Follow STAR method (Situation, Task, Action, Result)

Return ONLY the improved bullet point, nothing else.
"""
            
            response = model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"Bullet point optimization error: {e}")
            return bullet_point
    
    @staticmethod
    async def generate_professional_summary(
        experience_years: int,
        skills: list,
        target_role: str
    ) -> str:
        """Generate a compelling professional summary"""
        
        if not settings.GEMINI_API_KEY:
            return f"Experienced {target_role} with {experience_years}+ years of expertise in {', '.join(skills[:3])}. Proven track record of delivering high-quality solutions and driving business results."
        
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
Write a compelling professional summary for a {target_role} with {experience_years} years of experience.

Key Skills: {', '.join(skills)}

Requirements:
- 3-4 lines maximum
- Highlight key strengths and achievements
- Include relevant keywords for ATS
- Professional and confident tone
- Focus on value proposition

Return ONLY the summary text, nothing else.
"""
            
            response = model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"Summary generation error: {e}")
            return f"Experienced {target_role} with {experience_years}+ years of expertise in {', '.join(skills[:3])}."
