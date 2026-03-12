from typing import List, Dict

class RoadmapGenerator:
    """
    AI Career Roadmap Generator
    Generates time-bound milestones for career goals.
    """

    @staticmethod
    def generate_roadmap(target_role: str, timeline_months: int = 6) -> List[Dict[str, str]]:
        role = target_role.lower()
        
        # 1. DATA SCIENCE & ANALYTICS
        if "data scientist" in role or "machine learning" in role or "ml engineer" in role:
            return [
                {"period": "Month 1", "focus": "Python for DS: NumPy, Pandas, Matplotlib + Statistical Foundations (Probability, Distros)"},
                {"period": "Month 2", "focus": "Machine Learning: Supervised Learning (Linear/Logistic, Trees) & Scikit-learn Mastery"},
                {"period": "Month 3", "focus": "Deep Learning: Neural Networks, CNNs, RNNs via PyTorch/TensorFlow & Unsupervised Learning"},
                {"period": "Month 4", "focus": "Data Engineering: SQL Mastery, Feature Engineering pipelines & Data Cleaning at scale"},
                {"period": "Month 5", "focus": "Deployment: MLOps Basics, Flask/FastAPI for models & Dockerization"},
                {"period": "Month 6", "focus": "End-to-End Capstone Project on GitHub & Portfolio/Interview prep"}
            ]
        elif "data analyst" in role:
            return [
                {"period": "Month 1", "focus": "Excel (Advanced), SQL Basics & Descriptive Statistics"},
                {"period": "Month 2", "focus": "Data Visualization: Tableau or PowerBI Mastery"},
                {"period": "Month 3", "focus": "Python for Data: Pandas, Seaborn for Exploratory Data Analysis (EDA)"},
                {"period": "Month 4", "focus": "Advanced SQL: Window Functions, CTEs & Database Performance"},
                {"period": "Month 5", "focus": "Business Intelligence: Creating meaningful dashboards for stakeholders"},
                {"period": "Month 6", "focus": "Business Communication & Case Study Practice for interviews"}
            ]

        # 2. WEB DEVELOPMENT (Frontend, Backend, Fullstack)
        elif "frontend" in role or "react" in role:
            return [
                {"period": "Month 1", "focus": "HTML5, CSS3 Semantic markup & Advanced CSS (Flexbox, Grid, Responsive Design)"},
                {"period": "Month 2", "focus": "JavaScript Mastery: ES6+, DOM Manipulation, Async/Await & Fetch API"},
                {"period": "Month 3", "focus": "React.js: Components, Hooks (useState, useEffect), Props & State Management (Redux/Zustand)"},
                {"period": "Month 4", "focus": "Advanced Tools: Tailwind CSS, Next.js, Framer Motion for animations"},
                {"period": "Month 5", "focus": "Testing & Auth: Unit testing with Vitest/Jest & JWT integration"},
                {"period": "Month 6", "focus": "Performance Optimization, PWA basics & Portfolio deployment on Vercel/Netlify"}
            ]
        elif "backend" in role or "node" in role or "python developer" in role or "java" in role:
            return [
                {"period": "Month 1", "focus": "Programming Language Deep Dive (Python/Node/Java/Go) & Data Structures"},
                {"period": "Month 2", "focus": "Web Frameworks: FastAPI/Django (Python) or Express (Node) or Spring Boot (Java)"},
                {"period": "Month 3", "focus": "Databases: SQL (PostgreSQL) vs NoSQL (MongoDB), Indexing & ORMs (SQLAlchemy/Prisma)"},
                {"period": "Month 4", "focus": "System Design: Microservices, Caching (Redis), Rate Limiting & API Security"},
                {"period": "Month 5", "focus": "Infrastructure: Docker Basics, CI/CD with GitHub Actions & Cloud Deployment"},
                {"period": "Month 6", "focus": "Advanced Concepts: Task Queues (Celery/RabbitMQ) & Backend Mock Interviews"}
            ]
        elif "full stack" in role:
            return [
                {"period": "Month 1", "focus": "Frontend Basics: React.js, Tailwind CSS & State Management"},
                {"period": "Month 2", "focus": "Backend Basics: Node.js/FastAPI, REST APIs & JWT Authentication"},
                {"period": "Month 3", "focus": "Database Management: PostgreSQL, MongoDB & Prisma/SQLAlchemy ORMs"},
                {"period": "Month 4", "focus": "Project Week: Build a complex fullstack application (e.g. E-commerce/Social Media)"},
                {"period": "Month 5", "focus": "Deployment: Docker, AWS/Render deployment & CI/CD Pipelines"},
                {"period": "Month 6", "focus": "DSA Prep + System Design Fundamentals for final tech interviews"}
            ]

        # 3. DEVOPS & INFRASTRUCTURE
        elif "devops" in role or "cloud" in role or "sre" in role:
            return [
                {"period": "Month 1", "focus": "Linux Administration (CLI, Shell Scripting, Networking Basics)"},
                {"period": "Month 2", "focus": "Infrastructure as Code: Terraform & Configuration Management with Ansible"},
                {"period": "Month 3", "focus": "Containerization: Docker Deep Dive & Writing optimized Dockerfiles"},
                {"period": "Month 4", "focus": "Container Orchestration: Kubernetes Fundamentals (Pods, Deployments, Services)"},
                {"period": "Month 5", "focus": "Cloud Platforms: AWS/Azure/GCP Mastery & CI/CD with GitLab/GitHub Actions"},
                {"period": "Month 6", "focus": "Monitoring: Prometheus, Grafana, ELK Stack & SRE Best Practices"}
            ]

        # 4. MOBILE DEVELOPMENT
        elif "mobile" in role or "android" in role or "ios" in role or "flutter" in role or "react native" in role:
            return [
                {"period": "Month 1", "focus": "Language Basics: Dart (Flutter) or Kotlin (Android) or Swift (iOS)"},
                {"period": "Month 2", "focus": "UI/UX Development: Widgets/Layouts, Navigation & Material/Cupertino design"},
                {"period": "Month 3", "focus": "State Management: Provider/Riverpod (Flutter) or Lifecycle/MVVM (Native)"},
                {"period": "Month 4", "focus": "Integration: REST APIs, Firebase Authentication & Firestore integration"},
                {"period": "Month 5", "focus": "Advanced Native: Push Notifications, Local DB (SQLite/Room) & Device APIs"},
                {"period": "Month 6", "focus": "App Store/Play Store Publishing process & Mobile App Performance"}
            ]

        # 5. CYBERSECURITY
        elif "security" in role or "cyber" in role or "tester" in role:
            return [
                {"period": "Month 1", "focus": "Networking Foundations (OSI, TCP/IP, DNS) & Linux Security"},
                {"period": "Month 2", "focus": "Security Principles: Encryption, IAM, OWASP Top 10 & Threat Modeling"},
                {"period": "Month 3", "focus": "Vulnerability Assessment: Nmap, Metasploit, Burp Suite basics"},
                {"period": "Month 4", "focus": "Defensive Security: SOC, SIEM (Splunk), Firewall configuration"},
                {"period": "Month 5", "focus": "Cloud Security: AWS Security, Identity Management in Cloud"},
                {"period": "Month 6", "focus": "Certification Prep: CompTIA Security+ or CEH & GRC Basics"}
            ]

        # 6. PRODUCT & BUSINESS
        elif "product manager" in role or "business analyst" in role:
            return [
                {"period": "Month 1", "focus": "Product Thinking: Market Research, User Interviews & Competitor Analysis"},
                {"period": "Month 2", "focus": "Design: Figma for PMs, User Journey Maps & Wireframing"},
                {"period": "Month 3", "focus": "Process: Agile/Scrum Mastery, PRD (Product Requirement Doc) Writing"},
                {"period": "Month 4", "focus": "Metrics: Product Analytics (Mixpanel/Amplitude) & SQL for PMs"},
                {"period": "Month 5", "focus": "Soft Skills: Stakeholder Management, Roadmap Communication & Prioritization"},
                {"period": "Month 6", "focus": "Mock Case Studies & Product Sense Interviews"}
            ]

        # DEFAULT / GENERAL SDE Roadmap
        return [
            {"period": "Month 1", "focus": "Data Structures & Algorithms: Strings, Arrays, Hashing, Linked Lists"},
            {"period": "Month 2", "focus": "DSA Intermediate: Trees, Graphs, Recursion, DP Foundations"},
            {"period": "Month 3", "focus": "Framework Mastery: Learning a modern stack (React/FastAPI/Node)"},
            {"period": "Month 4", "focus": "Version Control (Git), Database Basics (SQL) & Writing Clean Code"},
            {"period": "Month 5", "focus": "Building Portfolio Projects & Active Open Source Contribution"},
            {"period": "Month 6", "focus": "Mock Interivews (Coding + Behavioral) & Professional Networking"}
        ]
