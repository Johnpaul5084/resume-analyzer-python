from ..utils.constants import SKILLS_DB
import re

class ATSEngine:
    @staticmethod
    def calculate_score(resume_skills, job_description):
        """Compare resume skills with JD and calculate match %."""
        # 1. Extract skills from JD
        jd_skills = []
        for skill in SKILLS_DB:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, job_description, re.IGNORECASE):
                jd_skills.append(skill)
        
        jd_skills = list(set(jd_skills))
        
        if not jd_skills:
            return {"score": 0, "missing_skills": [], "matched_skills": []}

        # 2. Match skills
        matched = [s for s in resume_skills if s in jd_skills]
        missing = [s for s in jd_skills if s not in resume_skills]
        
        # 3. Calculate percentage
        score = (len(matched) / len(jd_skills)) * 100
        
        return {
            "score": round(score, 2),
            "matched_skills": matched,
            "missing_skills": missing,
            "total_jd_skills": len(jd_skills)
        }
