"""
AI Skill Ontology v2.0 — Comprehensive Career Intelligence
==========================================================

UPGRADED from 4 clusters to 10 clusters with 300+ skills.
Covers ALL major career domains including:
  IT, Data Science, DevOps, Mobile, Security, Design, Business, Core Engineering, Finance, Marketing

New Features:
  - Synonym matching (e.g., "ML" → "Machine Learning", "k8s" → "Kubernetes")
  - Weighted skill importance (Core > Advanced > Tools)
  - Industry-specific skill recommendations
  - Skill gap analysis with priority ordering
"""

import re
from typing import Dict, List, Set, Tuple


class SkillOntology:
    """
    AI Skill Ontology & Taxonomy v2.0
    Comprehensive skill definitions for semantic matching across all career domains.
    """

    CLUSTERS = {
        "Data Science & AI": {
            "Core": ["Python", "R", "SQL", "Statistics", "Machine Learning", "Mathematics", "Linear Algebra", "Probability"],
            "Libraries": ["Pandas", "NumPy", "Scikit-Learn", "TensorFlow", "PyTorch", "Keras", "XGBoost", "LightGBM", "OpenCV"],
            "Concepts": ["Feature Engineering", "A/B Testing", "Deep Learning", "NLP", "Computer Vision",
                        "Reinforcement Learning", "Time Series", "Recommendation Systems", "GANs", "Transformers", "LLMs"],
            "Tools": ["Jupyter", "MLflow", "Weights & Biases", "SageMaker", "Databricks", "Hugging Face"],
            "Visualization": ["Tableau", "Power BI", "Matplotlib", "Seaborn", "Plotly", "D3.js"],
        },
        "Web Development": {
            "Frontend": ["React", "Angular", "Vue", "Next.js", "Svelte", "JavaScript", "TypeScript", "HTML5", "CSS3",
                        "Tailwind CSS", "Bootstrap", "SASS", "Webpack", "Vite"],
            "Backend": ["Node.js", "Express", "Django", "FastAPI", "Flask", "Spring Boot", "Go", "Rust", "Ruby on Rails",
                       "NestJS", "GraphQL", "REST API", "gRPC"],
            "Database": ["PostgreSQL", "MongoDB", "MySQL", "Redis", "Elasticsearch", "DynamoDB", "Cassandra",
                        "Firebase", "Supabase", "SQLite"],
            "Fullstack": ["MERN", "MEAN", "JAMstack", "SSR", "SSG", "PWA", "WebSocket", "OAuth", "JWT"],
        },
        "DevOps & Cloud": {
            "Containers": ["Docker", "Kubernetes", "OpenShift", "Helm", "Podman", "Container Registry"],
            "CI/CD": ["Jenkins", "GitLab CI", "GitHub Actions", "CircleCI", "ArgoCD", "Tekton", "Spinnaker"],
            "Cloud": ["AWS", "Azure", "GCP", "Terraform", "Ansible", "CloudFormation", "Pulumi", "CDK"],
            "Monitoring": ["Prometheus", "Grafana", "Datadog", "ELK Stack", "Splunk", "New Relic", "PagerDuty"],
            "Infrastructure": ["Linux", "Bash", "Shell Scripting", "Nginx", "Apache", "HAProxy",
                              "Service Mesh", "Istio", "Consul", "Vault"],
        },
        "Software Engineering": {
            "Languages": ["C++", "Java", "C#", "Rust", "Go", "Scala", "Kotlin", "Haskell", "Erlang"],
            "Fundamentals": ["Algorithms", "Data Structures", "System Design", "Design Patterns",
                           "Object-Oriented Programming", "Functional Programming", "Concurrency", "Distributed Systems"],
            "Practices": ["Unit Testing", "Integration Testing", "Microservices", "TDD", "BDD", "Agile", "Scrum",
                         "Kanban", "Code Review", "Pair Programming", "Clean Code", "SOLID Principles"],
            "Architecture": ["Event Driven", "CQRS", "Domain Driven Design", "API Gateway", "Message Queue",
                           "Kafka", "RabbitMQ", "Load Balancing"],
        },
        "Mobile Development": {
            "Cross-Platform": ["React Native", "Flutter", "Dart", "Ionic", "Xamarin", "KMM"],
            "Native Android": ["Kotlin", "Java", "Android Studio", "Jetpack Compose", "Room DB", "Retrofit",
                              "Dagger/Hilt", "Android SDK", "Material Design"],
            "Native iOS": ["Swift", "SwiftUI", "UIKit", "Xcode", "Core Data", "Combine", "ARKit"],
            "Common": ["Firebase", "REST API", "Push Notifications", "App Store Optimization",
                      "Mobile CI/CD", "Fastlane", "TestFlight"],
        },
        "Cybersecurity": {
            "Core": ["Network Security", "Cryptography", "Firewalls", "IDS/IPS", "VPN", "Access Control",
                    "Identity Management", "Zero Trust"],
            "Offensive": ["Penetration Testing", "Vulnerability Assessment", "Ethical Hacking", "Social Engineering",
                        "Red Teaming", "Bug Bounty", "Exploitation"],
            "Defensive": ["SIEM", "Incident Response", "Threat Hunting", "Malware Analysis", "SOC Operations",
                        "Digital Forensics", "Threat Intelligence"],
            "Tools": ["Splunk", "Wireshark", "Metasploit", "Nessus", "Burp Suite", "OWASP ZAP",
                     "Nmap", "Kali Linux", "Snort"],
            "Compliance": ["SOC 2", "ISO 27001", "GDPR", "HIPAA", "PCI DSS", "NIST"],
        },
        "UI/UX Design": {
            "Research": ["User Research", "Usability Testing", "A/B Testing", "User Journey Mapping",
                        "Persona Development", "Heuristic Evaluation", "Card Sorting"],
            "Design": ["Wireframing", "Prototyping", "Visual Design", "Interaction Design", "Motion Design",
                      "Design Systems", "Responsive Design", "Accessibility"],
            "Tools": ["Figma", "Adobe XD", "Sketch", "InVision", "Miro", "Zeplin", "Framer",
                     "Adobe Illustrator", "Adobe Photoshop", "After Effects"],
            "Principles": ["Design Thinking", "Information Architecture", "Typography", "Color Theory",
                         "Grid Systems", "Gestalt Principles"],
        },
        "Product & Business": {
            "Product": ["Product Strategy", "Roadmapping", "User Stories", "Backlog Management",
                       "Feature Prioritization", "OKRs", "KPIs", "Sprint Planning", "PRD Writing"],
            "Analytics": ["Google Analytics", "Mixpanel", "Amplitude", "A/B Testing", "Cohort Analysis",
                        "Funnel Analysis", "Retention Metrics", "SQL", "Excel"],
            "Business": ["Business Analysis", "Requirements Gathering", "Process Mapping", "BPMN",
                        "Stakeholder Management", "ROI Analysis", "Six Sigma", "Lean"],
            "Project": ["Agile", "Scrum", "Kanban", "PMP", "Waterfall", "Risk Management",
                       "Resource Planning", "Gantt Charts"],
        },
        "Core Engineering": {
            "Mechanical": ["SolidWorks", "AutoCAD", "CATIA", "Creo", "ANSYS", "GD&T", "Engineering Drawing",
                         "FEA", "CFD", "3D Printing", "DFM/DFA", "Thermodynamics", "Material Science"],
            "Civil": ["STAAD Pro", "ETABS", "Revit", "Primavera", "MS Project", "Structural Analysis",
                     "RCC Design", "Surveying", "BIM", "Quantity Estimation"],
            "Electrical": ["MATLAB", "Simulink", "PLC Programming", "SCADA", "Power Systems",
                         "Control Systems", "Circuit Design", "PCB Design", "Embedded C"],
            "Electronics": ["VHDL", "Verilog", "FPGA", "Microcontrollers", "ARM", "RTOS",
                          "Signal Processing", "IoT", "Raspberry Pi", "Arduino"],
        },
        "Finance & Marketing": {
            "Finance": ["Financial Modeling", "Valuation", "DCF", "M&A", "Risk Analysis",
                       "Derivatives", "Portfolio Management", "Bloomberg Terminal", "Capital IQ"],
            "Accounting": ["GAAP", "IFRS", "Tally", "QuickBooks", "SAP FICO", "Taxation", "Auditing"],
            "Marketing": ["SEO", "SEM", "Google Ads", "Social Media Marketing", "Content Strategy",
                        "Email Marketing", "Marketing Automation", "CRM", "HubSpot", "Salesforce"],
            "Analytics Tools": ["Google Analytics", "Semrush", "Ahrefs", "Hootsuite", "Mailchimp",
                              "Notion", "Asana", "Monday.com"],
        },
    }

    # Skill synonyms — maps short/alternate names to canonical names
    SYNONYMS = {
        "ml": "Machine Learning",
        "dl": "Deep Learning",
        "ai": "Machine Learning",
        "k8s": "Kubernetes",
        "tf": "TensorFlow",
        "np": "NumPy",
        "pd": "Pandas",
        "js": "JavaScript",
        "ts": "TypeScript",
        "py": "Python",
        "rb": "Ruby",
        "rn": "React Native",
        "aws": "AWS",
        "gcp": "GCP",
        "ci/cd": "CI/CD",
        "cicd": "CI/CD",
        "oop": "Object-Oriented Programming",
        "dsa": "Data Structures",
        "dbms": "Databases",
        "os": "Operating Systems",
        "cn": "Computer Networks",
        "html": "HTML5",
        "css": "CSS3",
        "rdbms": "SQL",
        "nosql": "MongoDB",
        "express": "Express",
        "django": "Django",
        "postgres": "PostgreSQL",
        "mongo": "MongoDB",
        "sklearn": "Scikit-Learn",
        "opencv": "OpenCV",
        "nlp": "NLP",
        "cv": "Computer Vision",
        "rl": "Reinforcement Learning",
        "llm": "LLMs",
        "genai": "LLMs",
        "gen ai": "LLMs",
        "generative ai": "LLMs",
    }

    @staticmethod
    def normalize_skill(skill: str) -> str:
        """Normalize a skill name using synonyms."""
        lower = skill.strip().lower()
        return SkillOntology.SYNONYMS.get(lower, skill.strip())

    @staticmethod
    def normalize_skills(skills: List[str]) -> List[str]:
        """Normalize a list of skills."""
        return [SkillOntology.normalize_skill(s) for s in skills]

    @staticmethod
    def map_role_to_cluster(role: str) -> str:
        """Map a user-specified role to the best matching ontology cluster."""
        r = role.lower()

        # Data & AI
        if any(x in r for x in ["data scientist", "data analyst", "ml", "ai", "machine learning",
                                  "intelligence", "deep learning", "nlp", "data engineer", "analytics"]):
            return "Data Science & AI"

        # DevOps & Cloud
        if any(x in r for x in ["devops", "cloud", "infra", "sre", "reliability",
                                  "platform engineer", "kubernetes", "docker"]):
            return "DevOps & Cloud"

        # Mobile
        if any(x in r for x in ["mobile", "android", "ios", "flutter", "react native", "app developer"]):
            return "Mobile Development"

        # Security
        if any(x in r for x in ["security", "cyber", "penetration", "ethical hack", "soc ", "infosec"]):
            return "Cybersecurity"

        # Design
        if any(x in r for x in ["ui", "ux", "design", "graphic", "product design"]):
            return "UI/UX Design"

        # Business & Product
        if any(x in r for x in ["product manager", "business analyst", "project manager",
                                  "operations", "supply chain", "scrum", "management"]):
            return "Product & Business"

        # Finance & Marketing
        if any(x in r for x in ["financial", "finance", "accountant", "marketing",
                                  "seo", "digital market", "investment"]):
            return "Finance & Marketing"

        # Core Engineering
        if any(x in r for x in ["mechanical", "civil", "electrical", "electronics",
                                  "automobile", "embedded", "vlsi", "iot", "fpga"]):
            return "Core Engineering"

        # Web Development
        if any(x in r for x in ["web", "full stack", "fullstack", "frontend", "front-end",
                                  "backend", "back-end", "react", "node", "django"]):
            return "Web Development"

        # Software Engineering (broadest catch)
        if any(x in r for x in ["software", "developer", "engineer", "programmer",
                                  "backend", "system", "architect"]):
            return "Software Engineering"

        return "Software Engineering"  # Default fallback

    @staticmethod
    def identify_primary_cluster(skills: List[str]) -> str:
        """Determines the most likely career cluster based on skills."""
        scores = {}
        # Normalize user skills first
        skills_lower = [SkillOntology.normalize_skill(s).lower() for s in skills]

        for cluster, categories in SkillOntology.CLUSTERS.items():
            count = 0
            for cat_name, cat_skills in categories.items():
                weight = 2.0 if cat_name in ("Core", "Languages", "Fundamentals") else 1.0
                for s in cat_skills:
                    if s.lower() in skills_lower:
                        count += weight
            scores[cluster] = count

        return max(scores, key=scores.get) if any(scores.values()) else "Software Engineering"

    @staticmethod
    def get_missing_skills(cluster: str, user_skills: List[str], max_gaps: int = 8) -> List[str]:
        """
        Finds gaps in the user's skillset for a target cluster.
        Returns prioritized list: Core gaps first, then Advanced, then Tools.
        """
        if cluster not in SkillOntology.CLUSTERS:
            return []

        user_skills_lower = [SkillOntology.normalize_skill(s).lower() for s in user_skills]

        missing_core = []
        missing_other = []

        for cat_name, cat_skills in SkillOntology.CLUSTERS[cluster].items():
            for s in cat_skills:
                if s.lower() not in user_skills_lower:
                    if cat_name in ("Core", "Languages", "Fundamentals", "Frontend", "Backend"):
                        missing_core.append(s)
                    else:
                        missing_other.append(s)

        # Core gaps first (most impactful), then others
        return (missing_core + missing_other)[:max_gaps]

    @staticmethod
    def get_cluster_skills(cluster: str) -> List[str]:
        """Return ALL skills for a given cluster (flat list)."""
        if cluster not in SkillOntology.CLUSTERS:
            return ["Python", "Java", "Git", "Linux", "SQL", "Algorithms", "Data Structures"]

        skills = []
        for cat_skills in SkillOntology.CLUSTERS[cluster].values():
            skills.extend(cat_skills)
        return skills

    @staticmethod
    def get_skill_coverage_report(user_skills: List[str], target_cluster: str) -> Dict[str, any]:
        """
        Generate a detailed skill coverage report for a target cluster.
        Returns category-wise coverage percentages.
        """
        if target_cluster not in SkillOntology.CLUSTERS:
            return {"error": f"Unknown cluster: {target_cluster}"}

        user_lower = [SkillOntology.normalize_skill(s).lower() for s in user_skills]
        report = {}
        total_matched = 0
        total_skills = 0

        for cat_name, cat_skills in SkillOntology.CLUSTERS[target_cluster].items():
            matched = [s for s in cat_skills if s.lower() in user_lower]
            missing = [s for s in cat_skills if s.lower() not in user_lower]
            coverage = round((len(matched) / max(len(cat_skills), 1)) * 100, 1)

            report[cat_name] = {
                "coverage_pct": coverage,
                "matched": matched,
                "missing": missing[:5],  # Top 5 gaps per category
                "total": len(cat_skills),
            }
            total_matched += len(matched)
            total_skills += len(cat_skills)

        report["_summary"] = {
            "overall_coverage": round((total_matched / max(total_skills, 1)) * 100, 1),
            "total_matched": total_matched,
            "total_skills": total_skills,
            "cluster": target_cluster,
        }

        return report

    @staticmethod
    def extract_skills_from_text(text: str) -> List[str]:
        """
        Extract recognized skills from resume text using ontology matching.
        More accurate than simple keyword parsing.
        """
        text_lower = text.lower()
        found_skills = set()

        for cluster_name, categories in SkillOntology.CLUSTERS.items():
            for cat_skills in categories.values():
                for skill in cat_skills:
                    if skill.lower() in text_lower:
                        found_skills.add(skill)

        # Also check synonyms
        for synonym, canonical in SkillOntology.SYNONYMS.items():
            if synonym in text_lower and canonical not in found_skills:
                found_skills.add(canonical)

        return sorted(list(found_skills))
