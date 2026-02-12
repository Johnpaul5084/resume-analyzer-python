# 🤖 Advanced AI Features Guide

This document describes the new AI-powered features added to the Resume Analyzer.

## 1. Real-Time AI Rewriting (`POST /api/v1/resumes/rewrite`)

Rewrites resume sections to meet MNC standards, focusing on grammar, clarity, and impact.

**Features:**
- **MNC Standard**: Automatically applies professional tone and terminology.
- **Role Specific**: Tailors content for specific roles (e.g., "Data Analytics", "Full Stack Developer").
- **Quantifiable Results**: Emphasizes metrics and achievements.

**Usage:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/resumes/rewrite" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -d '{
    "text": "i did data analysis stuff using python",
    "section_type": "Experience",
    "target_role": "Data Analyst",
    "company_type": "MNC"
  }'
```

## 2. Job Role Prediction (`POST /api/v1/resumes/predict-job`)

Uses a BERT-based Zero-Shot Classification model (Facebook BART) to analyze the resume and predict the most suitable job roles.

**Features:**
- **Zero-Shot Learning**: Can predict any job category without specific training.
- **Confidence Scores**: Returns the probability for each role.

**Usage:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/resumes/predict-job" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -d '{
    "text": "Experienced web developer with React and Node.js skills...",
    "candidate_labels": ["Frontend Lead", "Backend Engineer", "Product Manager"]
  }'
```

**Note**: The first time you run this, it will download the model (~1.5GB). Subsequent requests will be fast.

## 3. Role Fit Validation (`POST /api/v1/resumes/validate-fit`)

Validates if a resume specifically fits a target role and provides detailed feedback.

**Features:**
- **Match Score**: 0-100 score.
- **Gap Analysis**: Identifies missing critical skills.
- **Improvement Areas**: Specific advice for MNC applications.

**Usage:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/resumes/validate-fit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -d '{
    "text": "Resume content here...",
    "target_role": "Data Scientist"
  }'
```

## ⏳ Setup Requirements

1. **Google Gemini API Key**: Ensure `GEMINI_API_KEY` is set in `.env` for Rewriting and Validation.
2. **Hugging Face Model**: The prediction service downloads `facebook/bart-large-mnli` automatically. Ensure you have internet access.

## 🚀 Testing

You can use the Swagger UI at `http://127.0.0.1:8000/docs` to test these endpoints interactively.
