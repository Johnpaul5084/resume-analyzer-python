# 🚀 IRIS AI – Intelligent Resume & Career Intelligence Platform

> From Resume Scoring to Career Intelligence Engineering
> Built with FastAPI, Semantic NLP, Vector Search, and Explainable AI

---

# 🌍 Vision

IRIS AI is not just a Resume Analyzer.

It is a **Semantic Resume Intelligence & Career Guidance Platform** designed to bridge the awareness gap for Tier-2/3/4 college students across IT, Core, and Non-IT domains.

The system combines:

* Transformer-based NLP
* Semantic embeddings
* Vector search (FAISS)
* Multi-metric ATS scoring
* AI-powered career mentorship
* Skill graph visualization
* Market demand analysis

Inspired by insights from **AI Impact Summit 2026 (Delhi)**.

---

# 🧠 Core System Capabilities

## 1️⃣ Semantic ATS 2.0

Unlike traditional keyword-based ATS systems, IRIS uses:

* Sentence-Transformers (MiniLM)
* Cosine Similarity Matching
* Context-aware evaluation

✔ Role Fit Score
✔ Skill Coverage Score
✔ Impact Quantification Score
✔ Experience Depth Score
✔ Composite Resume Strength Index

---

## 2️⃣ AI Career Mentor (IRIS Guru)

A conversational AI mentor that:

* Detects student domain (IT / Core / Non-IT)
* Recommends high-demand roles
* Identifies mandatory missing skills
* Generates personalized 6-month roadmap
* Suggests FAANG / MNC preparation strategy

Supports:

* CSE / IT
* Mechanical
* ECE
* Civil
* Business / MBA
* Multi-disciplinary profiles

---

## 3️⃣ Dynamic AI Roadmap Generator

Uses LLM with structured prompts to generate:

* Monthly learning plans
* Project suggestions
* Interview preparation guidance
* Resume improvement strategy

Format:

Month 1-2 → Foundation
Month 3-4 → Advanced Skills
Month 5 → Projects
Month 6 → Interview Preparation

---

## 4️⃣ Market Demand Detection Engine

Role demand intelligence powered by structured demand scoring:

* 🔥 Very High Demand
* 📈 High Demand
* Stable Demand
* Emerging / Niche

Helps students make informed career decisions.

---

## 5️⃣ Skill Graph Visualization

Graph-based skill progression using NetworkX.

Visualizes:

* Existing skills (Green)
* Missing mandatory skills (Red)
* Advanced future skills (Blue)

Shows career growth pathway instead of static lists.

---

## 6️⃣ Resume Strength Radar Chart

Plotly-powered visualization displaying:

* Technical Strength
* Experience Depth
* ATS Optimization
* Impact Quantification
* Role Fit

Professional analytics-style UI.

---

# 🏗 System Architecture

```text
Resume Upload
    ↓
Document Parsing (PDF/DOCX/OCR)
    ↓
NLP Extraction (spaCy + Transformers)
    ↓
Embedding Generation (MiniLM)
    ↓
Vector Retrieval (FAISS)
    ↓
Multi-Metric Scoring Engine
    ↓
Skill Gap Analysis
    ↓
Market Demand Engine
    ↓
AI Career Mentor
    ↓
Skill Graph + Radar Visualization
```

---

# 🛠 Technology Stack

## Backend

* FastAPI
* SQLAlchemy + PostgreSQL
* JWT Authentication
* Docker-ready architecture

## AI / ML

* spaCy (NER)
* Sentence-Transformers
* FAISS (Vector Search)
* scikit-learn
* XGBoost (optional expansion)
* Google Gemini (AI generation)

## Visualization

* Plotly (Radar Charts)
* NetworkX (Skill Graph)

## Frontend

* React 18
* Vite
* Tailwind CSS
* Recharts / Plotly

---

# 📊 Scoring Model

Composite Resume Strength Index:

```python
final_score = (
    0.35 * semantic_similarity +
    0.25 * skill_coverage +
    0.20 * experience_depth +
    0.20 * ats_format_score
)
```

Transparent & explainable scoring — no random percentages.

---

# 🎓 Academic & Research Relevance

This project demonstrates:

* Applied NLP
* Semantic Retrieval Systems
* Multi-metric Evaluation Models
* Explainable AI
* Vector Database Implementation
* Career Ontology Modeling

Bridges real-world recruitment systems with AI-based personalization.

---

# � Deployment

100% Free Production Stack:

* Frontend → Vercel
* Backend → Render
* Database → Supabase
* Vector Store → FAISS (local index)

No credit card required.

---

# 🔐 Security & Production Readiness

* JWT authentication
* Password hashing (bcrypt)
* ORM-based SQL injection protection
* File validation
* CORS configuration
* Docker containerization

---

# � Future Roadmap

* GitHub Profile Intelligence
* LinkedIn Resume Analyzer
* Career Probability Model (XGBoost)
* Interview Question Generator per Role
* Salary Prediction Engine
* RAG-based Career Advisor

---

# 🎤 For Final Year Presentation

Key Highlights:

✔ Semantic Resume Intelligence (not keyword matching)
✔ AI Career Mentor for multi-branch students
✔ Skill Graph Visualization
✔ Market Demand Awareness
✔ Explainable AI Feedback
✔ Production-Ready Full Stack Deployment

---

# 🏆 Project Positioning

IRIS AI transforms resume evaluation from:

“Keyword Matching Tool”

to

“AI-Powered Career Intelligence Platform”

---

# � License

MIT License

---

Built with ❤️ for innovation in AI-driven career intelligence.
