# 🚀 Resume Analyzer AI - User Guide

The application has been upgraded with a **Fully Automated AI Workflow**.

## 🌟 New Features

### 1. 🤖 Automatic Role Detection
When you upload a resume, the system now uses a **BERT AI Model** to instantly analyze your text and predict your best-fit job role (e.g., *Data Scientist, Civil Engineer, Nurse, Product Manager*).

### 2. ✨ AI Resume Rewriter (MNC Standards)
Based on the predicted role, our **Generative AI (Gemini)** automatically rewrites your *entire resume* to meet **Global MNC Standards**.
- It fixes grammar and clarity.
- It adds quantifiable metrics (e.g., *"Improved efficiency by 20%"*).
- It injects industry-specific keywords for the detected role.

### 3. 🎯 Real-Time Job Matching
The system predicts **Opening Job Roles** suitable for you across all domains (IT, Engineering, Medical, Arts) based on your resume content.

## 🛠️ How to Use

1. **Go to Dashboard**: [http://localhost:3000](http://localhost:3000)
2. **Upload Resume**: Click "Analyze Resume" and upload your PDF/DOCX.
3. **Wait**: The analysis might take 10-20 seconds (especially the first time as AI models initialize).
4. **View Results**: You will be redirected to the Analysis Report.
   - Scroll down to see the **"Predicted Job Role"** card.
   - Check the **"MNC-Ready Optimized Version"** card to see your improved resume!

## ⚠️ Important Note
- The first time you upload, the backend downloads a large AI model (~1.5GB) for job prediction. This might take a few minutes depending on your internet. **Please be patient.**
- Ensure your `GEMINI_API_KEY` is set in `.env` for the rewriter to work.
