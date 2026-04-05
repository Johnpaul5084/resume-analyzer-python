"""
Domain Classifier v2.0 — Enhanced AI Domain Intelligence
========================================================

UPGRADED from 3 domains/30 keywords to 8 domains/150+ keywords.
Uses weighted scoring with primary and secondary keyword matching.

Domains:
  1. Software & AI          (core IT)
  2. Data & Analytics       (data-centric roles)
  3. DevOps & Cloud         (infrastructure)
  4. Cybersecurity          (security-focused)
  5. Core Engineering       (mechanical, civil, electrical, electronics)
  6. Business & Management  (product, project, operations)
  7. Design & Creative      (UI/UX, graphic design)
  8. Finance & Commerce     (finance, accounting, banking)
"""

from typing import List, Dict, Tuple


class DomainClassifier:
    """
    AI Domain Intelligence v2.0
    Classifies profile into 8 career domains using weighted keyword matching.
    """

    DOMAINS = {
        "Software & AI": {
            "primary": ["python", "java", "javascript", "react", "node.js", "machine learning",
                       "deep learning", "fastapi", "django", "spring boot", "c++", "rust",
                       "typescript", "angular", "vue", "tensorflow", "pytorch",
                       "full stack", "backend", "frontend", "software engineer",
                       "algorithm", "data structure", "system design", "microservices"],
            "secondary": ["git", "sql", "api", "rest", "graphql", "docker",
                         "npm", "webpack", "vite", "jsx", "json", "oauth",
                         "jwt", "cors", "websocket", "http", "tcp"],
        },
        "Data & Analytics": {
            "primary": ["data analysis", "data science", "machine learning", "statistics",
                       "pandas", "numpy", "scikit-learn", "tableau", "power bi",
                       "data engineering", "etl", "data warehouse", "spark", "airflow",
                       "bigquery", "snowflake", "databricks", "data pipeline",
                       "a/b testing", "regression", "classification", "clustering"],
            "secondary": ["excel", "sql", "r programming", "jupyter", "matplotlib",
                         "seaborn", "plotly", "dbt", "redshift", "hadoop",
                         "feature engineering", "data visualization", "analytics"],
        },
        "DevOps & Cloud": {
            "primary": ["docker", "kubernetes", "aws", "azure", "gcp", "terraform",
                       "ci/cd", "jenkins", "gitlab ci", "github actions", "ansible",
                       "prometheus", "grafana", "linux", "devops", "sre",
                       "cloud architect", "infrastructure", "containerization"],
            "secondary": ["bash", "shell", "nginx", "apache", "helm", "istio",
                         "vault", "consul", "argocd", "cloudformation", "pulumi",
                         "monitoring", "logging", "elk stack", "datadog", "splunk"],
        },
        "Cybersecurity": {
            "primary": ["cybersecurity", "network security", "penetration testing",
                       "vulnerability assessment", "ethical hacking", "siem", "soc",
                       "incident response", "malware analysis", "cryptography",
                       "firewall", "ids", "ips", "threat hunting", "zero trust"],
            "secondary": ["wireshark", "metasploit", "nessus", "burp suite", "nmap",
                         "kali linux", "owasp", "iso 27001", "gdpr", "compliance",
                         "security audit", "pci dss", "risk assessment"],
        },
        "Core Engineering": {
            "primary": ["solidworks", "autocad", "catia", "ansys", "matlab", "simulink",
                       "mechanical", "civil", "electrical", "electronics", "embedded",
                       "vlsi", "fpga", "microcontroller", "pcb", "plc", "scada",
                       "staad", "etabs", "revit", "thermodynamics", "fea", "cfd"],
            "secondary": ["gd&t", "engineering drawing", "3d printing", "iot",
                         "arduino", "raspberry pi", "rtos", "vhdl", "verilog",
                         "signal processing", "control system", "power electronics",
                         "structural analysis", "manufacturing", "automobile"],
        },
        "Business & Management": {
            "primary": ["product management", "project management", "business analysis",
                       "stakeholder management", "agile", "scrum", "kanban",
                       "roadmapping", "okr", "kpi", "strategy", "operations",
                       "supply chain", "six sigma", "lean", "pmp", "consulting"],
            "secondary": ["jira", "confluence", "trello", "asana", "monday.com",
                         "requirements", "process mapping", "bpmn", "risk management",
                         "change management", "training", "hr", "recruitment",
                         "performance management", "vendor management"],
        },
        "Design & Creative": {
            "primary": ["figma", "adobe xd", "sketch", "user research", "wireframing",
                       "prototyping", "visual design", "interaction design",
                       "ui design", "ux design", "graphic design", "design system",
                       "design thinking", "user interface", "user experience"],
            "secondary": ["illustrator", "photoshop", "after effects", "invision",
                         "miro", "framer", "zeplin", "typography", "color theory",
                         "responsive design", "accessibility", "motion design",
                         "branding", "logo design", "web design"],
        },
        "Finance & Commerce": {
            "primary": ["financial modeling", "valuation", "dcf", "accounting",
                       "investment banking", "portfolio management", "risk analysis",
                       "chartered accountant", "cfa", "tally", "sap fico",
                       "financial statements", "taxation", "auditing", "banking"],
            "secondary": ["excel", "bloomberg", "capital iq", "derivatives",
                         "mutual funds", "equity research", "credit analysis",
                         "insurance", "fintech", "quickbooks", "gaap", "ifrs",
                         "e-commerce", "marketing", "seo", "google ads", "crm"],
        },
    }

    @staticmethod
    def classify_profile(skills: List[str]) -> str:
        """Classify profile into best-fit domain using weighted keyword matching."""
        skills_lower = [s.lower() for s in skills]
        skill_text = " ".join(skills_lower)

        scores = {}
        for domain, keyword_groups in DomainClassifier.DOMAINS.items():
            score = 0
            # Primary keywords get weight 3
            for kw in keyword_groups["primary"]:
                if kw in skill_text:
                    score += 3
            # Secondary keywords get weight 1
            for kw in keyword_groups["secondary"]:
                if kw in skill_text:
                    score += 1
            scores[domain] = score

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary_domain, best_score = sorted_scores[0]

        if best_score == 0:
            return "General Professional"
        return primary_domain

    @staticmethod
    def classify_with_confidence(skills: List[str]) -> List[Dict]:
        """
        Classify profile with confidence scores for top 3 matching domains.
        Returns sorted list: [{domain, confidence, matched_keywords}]
        """
        skills_lower = [s.lower() for s in skills]
        skill_text = " ".join(skills_lower)

        results = []
        max_possible = 0

        for domain, keyword_groups in DomainClassifier.DOMAINS.items():
            matched_primary = [kw for kw in keyword_groups["primary"] if kw in skill_text]
            matched_secondary = [kw for kw in keyword_groups["secondary"] if kw in skill_text]

            score = len(matched_primary) * 3 + len(matched_secondary) * 1
            total_possible = len(keyword_groups["primary"]) * 3 + len(keyword_groups["secondary"]) * 1
            max_possible = max(max_possible, score)

            results.append({
                "domain": domain,
                "score": score,
                "total_possible": total_possible,
                "matched_primary": matched_primary[:5],
                "matched_secondary": matched_secondary[:3],
            })

        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)

        # Convert to confidence percentages (relative to best match)
        if max_possible > 0:
            for r in results:
                r["confidence"] = round((r["score"] / max_possible) * 100, 1)
        else:
            for r in results:
                r["confidence"] = 0

        return results[:3]

    @staticmethod
    def classify_from_text(text: str) -> str:
        """Classify domain directly from resume text (not just extracted skills)."""
        text_lower = text.lower()

        scores = {}
        for domain, keyword_groups in DomainClassifier.DOMAINS.items():
            score = 0
            for kw in keyword_groups["primary"]:
                if kw in text_lower:
                    score += 3
            for kw in keyword_groups["secondary"]:
                if kw in text_lower:
                    score += 1
            scores[domain] = score

        best_domain = max(scores, key=scores.get)
        return best_domain if scores[best_domain] > 0 else "General Professional"
