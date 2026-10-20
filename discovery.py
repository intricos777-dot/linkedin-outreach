# Watermark: Living_Sin (intricos777-dot) + AI agents (Hermes, Lia, opencode) - collaborative work
# Copyright (c) 2026 Living Sin (intricos777-dot) + AI agents (Hermes, Lia, opencode) - collaborative work
# Licensed under Living Sin Proprietary License (LSPL-1.0)
# See LICENSE file for details.
"""Lead discovery engine - searches for target companies and generates seed leads."""

import json
import uuid
from datetime import datetime
from models import Lead, Company, HiringSignal, HiringSignalData


# Seed target companies - these are realistic companies that hire AI/automation talent
# Based on market research (LinkedIn, Glassdoor, Indeed hiring signals)
SEED_TARGETS = [
    Company(
        name="Citi",
        website="citi.com",
        industry="finance",
        company_size="5000+",
        location="New York, NY",
        tech_stack=["Python", "SQL", "AWS", "Kubernetes", "Spark", "Airflow", "Kafka"],
        funding_stage="public",
        description="Global investment bank and financial services corporation actively expanding AI/ML teams for fraud detection, trading algorithms, and customer service automation.",
    ),
    Company(
        name="State Farm",
        website="statefarm.com",
        industry="insurance",
        company_size="5000+",
        location="Bloomington, IL",
        tech_stack=["Python", "SQL", "Azure", "Guidewire", "RPA", "Salesforce"],
        funding_stage="public",
        description="Insurance and financial services company with major AI initiatives in claims automation, underwriting, and customer service.",
    ),
    Company(
        name="Atlassian",
        website="atlassian.com",
        industry="saas",
        company_size="5000+",
        location="San Francisco, CA",
        tech_stack=["Python", "Java", "AWS", "Kubernetes", "PostgreSQL", "React", "GraphQL"],
        funding_stage="public",
        description="Collaboration software company with growing AI team focused on intelligent features across Jira, Confluence, and other products.",
    ),
    Company(
        name="Lenovo",
        website="lenovo.com",
        industry="manufacturing",
        company_size="5000+",
        location="Morrisville, NC",
        tech_stack=["Python", "C++", "Azure", "IoT", "SCADA", "SAP"],
        funding_stage="public",
        description="Global technology manufacturer investing in AI for supply chain optimization, quality control, and predictive maintenance.",
    ),
    Company(
        name="Leidos",
        website="leidos.com",
        industry="consulting",
        company_size="5000+",
        location="Reston, VA",
        tech_stack=["Python", "R", "AWS", "Azure", "Kubernetes", "Spark"],
        funding_stage="public",
        description="Defense, aviation, and IT services contractor building AI solutions for government and enterprise clients.",
    ),
    Company(
        name="Accenture",
        website="accenture.com",
        industry="consulting",
        company_size="5000+",
        location="Dublin, Ireland / New York, NY",
        tech_stack=["Python", "R", "AWS", "Azure", "GCP", "SAP", "Salesforce"],
        funding_stage="public",
        description="Global professional services company with dedicated AI practice implementing AI automation across enterprise clients.",
    ),
    Company(
        name="Automated Insights",
        website="automatedinsights.com",
        industry="saas",
        company_size="51-200",
        location="Durham, NC",
        tech_stack=["Python", "AWS", "Natural Language Generation", "APIs", "PostgreSQL"],
        funding_stage="acquired",
        description="AI-powered natural language generation platform. Hiring ML engineers to scale content automation capabilities.",
    ),
    Company(
        name="PathAI",
        website="pathai.com",
        industry="healthcare",
        company_size="201-1000",
        location="Boston, MA",
        tech_stack=["Python", "PyTorch", "AWS", "Computer Vision", "Kubernetes"],
        funding_stage="series c",
        description="AI-powered pathology platform. Actively hiring ML engineers to build diagnostic AI agents for clinical labs.",
    ),
    Company(
        name="DataRobot",
        website="datarobot.com",
        industry="saas",
        company_size="1001-5000",
        location="Boston, MA",
        tech_stack=["Python", "R", "AWS", "Kubernetes", "Docker", "Spark"],
        funding_stage="series g",
        description="Enterprise AI platform building AutoML tools. Expanding team for agentic AI capabilities.",
    ),
    Company(
        name="Cresta",
        website="cresta.com",
        industry="saas",
        company_size="201-1000",
        location="San Francisco, CA",
        tech_stack=["Python", "PyTorch", "AWS", "Kubernetes", "NLP", "LLMs"],
        funding_stage="series c",
        description="AI contact center platform. Hiring AI engineers to build real-time agent assistance and automation.",
    ),
    Company(
        name="Samsara",
        website="samsara.com",
        industry="logistics",
        company_size="1001-5000",
        location="San Francisco, CA",
        tech_stack=["Python", "Go", "AWS", "Kafka", "IoT", "Kubernetes", "Spark"],
        funding_stage="public",
        description="IoT platform for fleet and industrial operations. AI team focused on predictive maintenance and safety automation.",
    ),
    Company(
        name="Nuro",
        website="nuro.ai",
        industry="logistics",
        company_size="1001-5000",
        location="Mountain View, CA",
        tech_stack=["Python", "C++", "ROS", "Computer Vision", "TensorFlow", "Kubernetes"],
        funding_stage="series d",
        description="Autonomous delivery vehicle company. Expanding AI/ML engineering for perception and planning systems.",
    ),
]


# Hiring signals per company - mimics real LinkedIn/Glassdoor/Indeed data
HIRING_SIGNALS_MAP = {
    "Citi": [
        HiringSignalData(HiringSignal.AI_ENGINEER, "linkedin.com/jobs/citi-ai-engineer", "linkedin", "AI Engineer", salary_range="$150K-$210K"),
        HiringSignalData(HiringSignal.ML_ENGINEER, "linkedin.com/jobs/citi-mle", "linkedin", "Machine Learning Engineer", salary_range="$160K-$220K"),
        HiringSignalData(HiringSignal.DATA_SCIENTIST, "glassdoor.com/citi-data-scientist", "glassdoor", "Data Scientist", salary_range="$130K-$180K"),
    ],
    "State Farm": [
        HiringSignalData(HiringSignal.AUTOMATION_ENGINEER, "linkedin.com/jobs/statefarm-automation", "linkedin", "Automation Engineer", salary_range="$110K-$150K"),
        HiringSignalData(HiringSignal.RPA_DEVELOPER, "indeed.com/statefarm-rpa", "indeed", "RPA Developer", salary_range="$90K-$120K"),
    ],
    "Atlassian": [
        HiringSignalData(HiringSignal.AI_ENGINEER, "linkedin.com/jobs/atlassian-ai", "linkedin", "AI Engineer", salary_range="$180K-$260K"),
        HiringSignalData(HiringSignal.ML_ENGINEER, "linkedin.com/jobs/atlassian-mle", "linkedin", "Senior ML Engineer", salary_range="$200K-$280K"),
        HiringSignalData(HiringSignal.PRODUCT_MANAGER_AI, "glassdoor.com/atlassian-pm-ai", "glassdoor", "Product Manager, AI", salary_range="$170K-$230K"),
    ],
    "Lenovo": [
        HiringSignalData(HiringSignal.AI_ENGINEER, "linkedin.com/jobs/lenovo-ai", "linkedin", "AI Solutions Architect", salary_range="$140K-$190K"),
        HiringSignalData(HiringSignal.ML_ENGINEER, "indeed.com/lenovo-mle", "indeed", "Computer Vision Engineer", salary_range="$130K-$175K"),
    ],
    "Leidos": [
        HiringSignalData(HiringSignal.AI_ENGINEER, "linkedin.com/jobs/leidos-ai", "linkedin", "AI Engineer - Defense", salary_range="$130K-$180K"),
        HiringSignalData(HiringSignal.AI_CONSULTANT, "glassdoor.com/leidos-ai-consultant", "glassdoor", "AI Consultant", salary_range="$120K-$165K"),
    ],
    "Accenture": [
        HiringSignalData(HiringSignal.CHIEF_AI_OFFICER, "linkedin.com/jobs/accenture-caio", "linkedin", "Managing Director, AI", salary_range="$250K-$400K"),
        HiringSignalData(HiringSignal.AI_ENGINEER, "linkedin.com/jobs/accenture-ai-engineer", "linkedin", "AI Engineer", salary_range="$140K-$200K"),
        HiringSignalData(HiringSignal.AI_CONSULTANT, "indeed.com/accenture-ai-consultant", "indeed", "AI Strategy Consultant", salary_range="$130K-$190K"),
    ],
    "Automated Insights": [
        HiringSignalData(HiringSignal.ML_ENGINEER, "linkedin.com/jobs/ai-mle", "linkedin", "ML Engineer - NLP", salary_range="$120K-$160K"),
    ],
    "PathAI": [
        HiringSignalData(HiringSignal.ML_ENGINEER, "linkedin.com/jobs/pathai-mle", "linkedin", "Senior ML Engineer", salary_range="$180K-$240K"),
        HiringSignalData(HiringSignal.AI_ENGINEER, "linkedin.com/jobs/pathai-ai-eng", "linkedin", "AI Infrastructure Engineer", salary_range="$170K-$220K"),
    ],
    "DataRobot": [
        HiringSignalData(HiringSignal.AI_ENGINEER, "linkedin.com/jobs/datarobot-ai", "linkedin", "AI Engineer", salary_range="$170K-$230K"),
        HiringSignalData(HiringSignal.ML_ENGINEER, "glassdoor.com/datarobot-mle", "glassdoor", "ML Platform Engineer", salary_range="$160K-$210K"),
        HiringSignalData(HiringSignal.PRODUCT_MANAGER_AI, "indeed.com/datarobot-pm-ai", "indeed", "Product Manager, Agentic AI", salary_range="$150K-$200K"),
    ],
    "Cresta": [
        HiringSignalData(HiringSignal.AI_ENGINEER, "linkedin.com/jobs/cresta-ai", "linkedin", "AI Engineer - LLMs", salary_range="$180K-$250K"),
        HiringSignalData(HiringSignal.ML_ENGINEER, "linkedin.com/jobs/cresta-mle", "linkedin", "Applied ML Scientist", salary_range="$190K-$260K"),
    ],
    "Samsara": [
        HiringSignalData(HiringSignal.ML_ENGINEER, "linkedin.com/jobs/samsara-mle", "linkedin", "ML Engineer - IoT", salary_range="$170K-$230K"),
        HiringSignalData(HiringSignal.AI_ENGINEER, "indeed.com/samsara-ai-eng", "indeed", "AI Engineer - Edge", salary_range="$160K-$220K"),
    ],
    "Nuro": [
        HiringSignalData(HiringSignal.AI_ENGINEER, "linkedin.com/jobs/nuro-ai", "linkedin", "AI Planning Engineer", salary_range="$190K-$270K"),
        HiringSignalData(HiringSignal.ML_ENGINEER, "linkedin.com/jobs/nuro-mle", "linkedin", "Perception Engineer", salary_range="$180K-$250K"),
        HiringSignalData(HiringSignal.AUTOMATION_ENGINEER, "glassdoor.com/nuro-automation", "glassdoor", "Autonomy Test Engineer", salary_range="$150K-$200K"),
    ],
}


def discover_leads() -> list[Lead]:
    """Generate seed leads from target company list and hiring signals."""
    leads = []
    for company in SEED_TARGETS:
        lead_id = str(uuid.uuid4())[:12]
        signals = HIRING_SIGNALS_MAP.get(company.name, [])
        lead = Lead(id=lead_id, company=company, hiring_signals=signals)
        leads.append(lead)
    return leads


def search_additional_companies(query_industry: str, max_results: int = 5) -> list[dict]:
    """
    Stub for web-search-based lead discovery. 
    In production, this would use web_search to find companies hiring AI talent.
    Returns structured data ready for Lead creation.
    """
    # This represents what a web search would return
    return [
        {
            "name": "Example AI Hiring Company",
            "industry": query_industry,
            "hiring_signals": ["AI Engineer", "ML Engineer"],
            "source": "linkedin_search",
            "source_url": "linkedin.com/jobs/example",
        }
    ]
