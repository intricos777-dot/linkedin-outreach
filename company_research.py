"""Company research module - researches tech stack, funding, and signals."""

import re
import json
from typing import Optional
from models import Company, HiringSignalData, HiringSignal


# Known tech stacks by industry for inference when direct lookup fails
INDUSTRY_TECH_HINTS = {
    "finance": ["Python", "SQL", "AWS", "Kubernetes", "Spark", "Airflow"],
    "healthcare": ["Python", "R", "SQL", "AWS", "FHIR", "HIPAA-compliant infra"],
    "e-commerce": ["Python", "JavaScript", "AWS", "React", "Node.js", "PostgreSQL"],
    "logistics": ["Python", "Java", "AWS", "Kafka", "PostGIS", "IoT"],
    "insurance": ["Python", "SQL", "Azure", "Guidewire", "Duck Creek", "RPA"],
    "manufacturing": ["Python", "C++", "Azure", "IoT", "SCADA", "ROS"],
    "legal": ["Python", "NLP", "AWS", "Clio", "Kira", "eDiscovery"],
    "marketing": ["Python", "SQL", "GCP", "BigQuery", "Looker", "HubSpot"],
    "saas": ["Python", "TypeScript", "AWS", "Kubernetes", "PostgreSQL", "Terraform"],
    "education": ["Python", "JavaScript", "AWS", "Moodle", "Canvas", "React"],
    "real_estate": ["Python", "SQL", "AWS", "Salesforce", "CoStar", "Yardi"],
    "retail": ["Python", "SQL", "AWS", "SAP", "Oracle Retail", "Snowflake"],
}

# Signals that a company is ripe for AI automation
AI_READINESS_SIGNALS = {
    "has_data_team": 15,
    "uses_cloud": 10,
    "has_api_integrations": 10,
    "hiring_ml_talent": 20,
    "legacy_modernization": 15,
    "high_volume_operations": 15,
    "customer_facing_ops": 10,
    "compliance_heavy": 10,
}


def infer_tech_stack(company: Company) -> list:
    """Infer likely tech stack based on industry and available hints."""
    industry = (company.industry or "").lower()
    hints = INDUSTRY_TECH_HINTS.get(industry, ["Python", "SQL", "AWS", "JavaScript"])
    if company.tech_stack:
        existing = {t.lower() for t in company.tech_stack}
        for h in hints:
            if h.lower() not in existing:
                company.tech_stack.append(h)
        return company.tech_stack
    return hints


def compute_ai_readiness_signals(company: Company) -> dict:
    """Estimate AI readiness based on available company data."""
    signals = {}
    tech_lower = " ".join(company.tech_stack).lower()
    
    if any(t in tech_lower for t in ["python", "r ", "scala", "spark"]):
        signals["has_data_team"] = True
    if any(t in tech_lower for t in ["aws", "azure", "gcp", "cloud", "kubernetes"]):
        signals["uses_cloud"] = True
    if any(t in tech_lower for t in ["api", "rest", "graphql", "webhook"]):
        signals["has_api_integrations"] = True
    if any(s.signal_type in (HiringSignal.ML_ENGINEER, HiringSignal.AI_ENGINEER) 
           for s in getattr(company, '_hiring_signals', [])):
        signals["hiring_ml_talent"] = True
    if any(t in tech_lower for t in ["sap", "oracle", "mainframe", "legacy", "monolith"]):
        signals["legacy_modernization"] = True
    if company.company_size in ["1001-5000", "5000+"]:
        signals["high_volume_operations"] = True
    if company.industry and company.industry.lower() in ["finance", "healthcare", "insurance", "legal"]:
        signals["compliance_heavy"] = True
    
    return signals


def generate_company_summary(company: Company) -> str:
    """Generate a research summary paragraph about a company."""
    size_desc = {
        "1-50": "a small but growing",
        "51-200": "a mid-sized",
        "201-1000": "a scale-up",
        "1001-5000": "a large",
        "5000+": "an enterprise-grade",
    }
    
    size_word = size_desc.get(company.company_size, "a")
    industry = company.industry or "technology"
    location = company.location or "the US"
    
    summary_parts = [
        f"{company.name} is {size_word} {industry} company based in {location}.",
    ]
    
    if company.tech_stack:
        top_tech = ", ".join(company.tech_stack[:5])
        summary_parts.append(f"Technology stack includes: {top_tech}.")
    
    if company.description:
        summary_parts.append(company.description[:200])
    
    if company.funding_stage:
        summary_parts.append(f"Funding stage: {company.funding_stage}.")
    
    return " ".join(summary_parts)
