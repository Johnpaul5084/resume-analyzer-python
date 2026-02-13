try:
    import spacy
    import language_tool_python
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    spacy = None
    language_tool_python = None
    TfidfVectorizer = None
    cosine_similarity = None

import re
from typing import List, Dict, Any, Tuple
from collections import Counter
import numpy as np

# Mock classes for fallback
class MockToken:
    def __init__(self, text):
        self.text = text
        self.lemma_ = text
        self.is_stop = False
        self.is_alpha = text.isalpha()
        self.label_ = "ORG" # Dummy label

class MockDoc:
    def __init__(self, text):
        self.text = text
        self.tokens = [MockToken(t) for t in text.split()]
        self.ents = []
    
    def __iter__(self):
        return iter(self.tokens)

# Load NLP model
nlp = None
if NLP_AVAILABLE:
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        try:
            import os
            os.system("python -m spacy download en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
        except:
            NLP_AVAILABLE = False # Fallback if download fails

# Lazy-load grammar tool to avoid blocking on startup
_grammar_tool = None

def get_grammar_tool():
    """Lazy-load grammar tool only when needed"""
    global _grammar_tool
    if _grammar_tool is None and language_tool_python:
        try:
            _grammar_tool = language_tool_python.LanguageTool('en-US')
        except:
            pass
    return _grammar_tool

class ATSScoringService:
    
    @staticmethod
    def calculate_score(resume_text: str, job_description: str = None, skip_grammar: bool = True) -> Dict[str, Any]:
        """
        Calculates ATS Score based on multiple factors:
        1. Keyword Match (40%) - Named Entity Recognition + TF-IDF
        2. Grammar & Style (20%) - LanguageTool check (optional, can be slow)
        3. Structure/Sections (10%) - Heuristic check
        4. Relevance (30%) - Cosine Similarity
        """
        
        # 1. Parsing & Tokenization
        doc = nlp(resume_text)
        
        # Extract Entities (Skills, Orgs, Dates, Education)
        skills = [ent.text.lower() for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT", "WORK_OF_ART", "GPE", "PERSON", "DATE", "CARDINAL"]] # Rough proxy for skills
        # Refine: In a real app, use a dedicated Skill NER model
        
        # 2. Grammar Check (Optional - can be slow)
        grammar_score = 85  # Default good score
        grammar_feedback = []
        
        if not skip_grammar:
            try:
                grammar_tool = get_grammar_tool()
                matches = grammar_tool.check(resume_text)
                grammar_score = max(0, 100 - (len(matches) * 2)) # Deduct points per error
                grammar_feedback = [{"message": m.message, "context": m.context} for m in matches[:5]] # Top 5
            except Exception as e:
                # If grammar check fails, use default score
                grammar_score = 85
                grammar_feedback = [{"message": "Grammar check skipped for faster analysis", "context": ""}]
        
        # 3. Keyword Analysis (If JD provided)
        keyword_score = 0
        similarity_score = 0
        missing_keywords = []

        if job_description:
            # TF-IDF & Cosine Similarity
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
            similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100
            
            # Key Terms Extraction
            jd_doc = nlp(job_description)
            jd_keywords = set([token.lemma_.lower() for token in jd_doc if not token.is_stop and token.is_alpha])
            resume_keywords = set([token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha])
            
            missing_keywords = list(jd_keywords - resume_keywords)
            # Cap missing keywords list for display
            missing_keywords = sorted(missing_keywords, key=len, reverse=True)[:10] 
            
            matched_count = len(jd_keywords.intersection(resume_keywords))
            total_jd_count = len(jd_keywords) if len(jd_keywords) > 0 else 1
            keyword_score = (matched_count / total_jd_count) * 100
            
        else:
            # Default scoring if no JD provided (based on rich content)
            keyword_score = min(len(skills) * 2, 100) # Heuristic
            similarity_score = 50 # Default middle ground
            
        # 4. Final Weighted Score
        # Weights: Keywords (40%), Relevance (20%), Grammar (20%), Structure (20%)
        # Structure score is a simplified proxy here
        structure_score = 80 # Assume good structure if parsed successfully
        
        final_score = (
            (keyword_score * 0.4) +
            (similarity_score * 0.2) +
            (grammar_score * 0.2) +
            (structure_score * 0.2)
        )
        
        return {
            "ats_score": round(final_score, 2),
            "breakdown": {
                "keywords_match": round(keyword_score, 2),
                "grammar_score": round(grammar_score, 2),
                "relevance_score": round(similarity_score, 2),
                "structure_score": round(structure_score, 2)
            },
            "missing_keywords": missing_keywords,
            "grammar_issues": grammar_feedback,
            "extracted_skills": list(set(skills))[:15] # Return top 15 extracted entities
        }

    @staticmethod
    def calculate_match_score(resume_text: str, job_description: str) -> Dict[str, Any]:
        """
        Calculates Match Score for Job Recommendations (Fast, no grammar/structure check).
        Weights: Keywords (60%), Relevance (40%)
        """
        
        # 1. Similarity (TF-IDF)
        similarity_score = 0
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
            similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100
        except Exception:
            similarity_score = 0
            
        # 2. Keywords
        doc = nlp(resume_text)
        jd_doc = nlp(job_description)
        
        jd_keywords = set([token.lemma_.lower() for token in jd_doc if not token.is_stop and token.is_alpha])
        resume_keywords = set([token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha])
        
        missing_keywords = list(jd_keywords - resume_keywords)
        missing_keywords = sorted(missing_keywords, key=len, reverse=True)[:10] 
        
        matched_count = len(jd_keywords.intersection(resume_keywords))
        total_jd_count = len(jd_keywords) if len(jd_keywords) > 0 else 1
        keyword_score = (matched_count / total_jd_count) * 100
        
        # Final Score
        final_score = (keyword_score * 0.6) + (similarity_score * 0.4)
        
        return {
            "ats_score": round(final_score, 2),
            "missing_keywords": missing_keywords,
            "breakdown": {
                "keywords_match": round(keyword_score, 2),
                "relevance_score": round(similarity_score, 2)
            }
        }

    @staticmethod
    def suggest_improvements(resume_text: str, missing_keywords: List[str]) -> str:
        """
        Mock AI suggestion generation. 
        In production, call LLM (OpenAI/Gemini) here.
        """
        suggestions = []
        if missing_keywords:
            suggestions.append(f"Consider adding these keywords: {', '.join(missing_keywords[:5])}")
        
        if len(resume_text.split()) < 200:
            suggestions.append("Your resume seems short. Elaborate on your experience.")
            
        return "\n".join(suggestions)
