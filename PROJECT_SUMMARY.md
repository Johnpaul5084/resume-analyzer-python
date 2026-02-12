# Resume Analyzer - Project Summary (Python Edition)

## ✅ Overview
This project is a Python-based implementation of the "Resume Analyzer" system, replicating all functionalities of the original Java Spring Boot architecture using **FastAPI** for high performance and modern async capabilities.

It includes the following enhancements:
-   **User Authentication**: JWT-based auth with OAuth2 password flow.
-   **Cloud Deployment Ready**: Dockerized and configured for easy deployment (Render/Railway).
-   **S3 Integration**: For scalable resume storage.
-   **Analytics & Rate Limiting**: Built-in tracking and usage limits.

## 📁 Project Structure

```
resume-analyzer-python/
├── resume-analyzer-backend/          # Python (FastAPI) Backend
│   ├── app/
│   │   ├── api/                      # API Endpoints
│   │   │   ├── endpoints/
│   │   │   │   ├── resume.py         # Resume upload & analysis
│   │   │   │   ├── auth.py           # Login & Registration
│   │   │   │   ├── users.py          # User management
│   │   │   │   ├── jobs.py           # Job matching logic
│   │   │   └── api.py                # Router configuration
│   │   ├── core/                     # Core Configuration
│   │   │   ├── config.py             # Environment variables & settings
│   │   │   ├── security.py           # JWT handling & password hashing
│   │   ├── db/                       # Database Layer
│   │   │   ├── base.py               # SQLAlchemy Base
│   │   │   ├── session.py            # DB engine & session maker
│   │   │   └── init_db.py            # Initial data seeding
│   │   ├── models/                   # SQLAlchemy Models (Database Tables)
│   │   │   ├── user.py               # User table
│   │   │   ├── resume.py             # Resume metadata & analysis
│   │   │   └── job.py                # Job descriptions
│   │   ├── schemas/                  # Pydantic Schemas (Data Validation)
│   │   │   ├── user.py
│   │   │   ├── resume.py
│   │   │   ├── token.py
│   │   ├── services/                 # Business Logic
│   │   │   ├── parser_service.py     # PDF/DOCX Parsing (PyPDF2, pdfplumber)
│   │   │   ├── ats_scoring_service.py# ATS Algorithm
│   │   │   ├── grammar_service.py    # Grammar checking (LanguageTool)
│   │   │   ├── ai_rewrite_service.py # LLM Integration (HuggingFace/OpenAI)
│   │   │   └── s3_service.py         # AWS S3 / Cloudinary upload
│   │   └── main.py                   # Application Entry Point
│   ├── requirements.txt              # Python Dependencies
│   ├── Dockerfile                    # Docker Image Config
│   └── alembic.ini                   # Database Migrations (Liquibase equivalent)
│
├── resume-analyzer-frontend/         # React Frontend (Unchanged or adapted)
│   ├── src/
│   │   ├── ...                       # Existing React components
│   └── ...
└── README.md
```

## 🔧 Technology Stack Comparison

| Component | Original Java Stack | New Python Stack | Note |
| :--- | :--- | :--- | :--- |
| **Framework** | Spring Boot 3.2.0 | **FastAPI** (Python 3.10+) | Faster dev speed, native async support |
| **Language** | Java 17 | **Python 3.10+** | Best ecosystem for AI/NLP libraries |
| **Database** | PostgreSQL | **PostgreSQL** | Same database engine |
| **ORM** | JPA / Hibernate | **SQLAlchemy** (Async) | Industry standard Python ORM |
| **Parsing** | Apache Tika / PDFBox | **PyPDF2 / pdfplumber / python-docx** | Robust PDF parsing libraries |
| **Grammar** | LanguageTool (Java Lib) | **language-tool-python** | Wrapper for the same engine |
| **AI / NLP** | HuggingFace Inference API | **Transformers / OpenAI / LangChain** | Direct integration with AI models |
| **Security** | Spring Security | **FastAPI Security + Passlib + JOSE** | OAuth2 standard implementation |
| **Migrations**| Flyway / Liquidbase | **Alembic** | Version control for DB schema |

## 🚀 Key Features Implemented

### 1. Core Infrastructure
-   **FastAPI Backend**: Robust, type-safe API with auto-generated Swagger docs (`/docs`).
-   **PostgreSQL + SQLAlchemy**: Relational data model with migration support.
-   **Docker**: Fully containerized for easy deployment.

### 2. Resume Upload & Parsing
-   **PDF/DOCX/TXT Support**: Using `pdfplumber` and `python-docx` for reliable text extraction.
-   **Section Parsing**: Heuristic-based segmentation (Contact, Summary, Skills, etc.).

### 3. ATS Scoring Engine
-   **Weighted Algorithm**: Replicated 6-component scoring.
-   **Keyword Matching**: NLP-based keyword extraction using `spacy` or `nltk`.

### 4. Grammar Checking
-   **LanguageTool Integration**: Detects errors and suggests fixes.

### 5. AI-Powered Rewriting
-   **LLM Integration**: Uses HuggingFace or OpenAI API to rewrite summary and experience sections.

## 📦 Python Dependencies
-   `fastapi`, `uvicorn`: Web framework & server
-   `sqlalchemy`, `alembic`, `psycopg2-binary`: Database
-   `pydantic`, `pydantic-settings`: Validation & Config
-   `python-jose`, `passlib`: Security (JWT, bcrypt)
-   `python-multipart`: File upload support
-   `spacy`, `nltk`, `language-tool-python`: NLP & Grammar
-   `pdfplumber`, `python-docx`: File parsing

