# Watermark: Living_Sin (intricos777-dot) + AI agents (Hermes, Lia, opencode) - collaborative work
"""Lead scoring engine - scores leads based on multiple weighted signals."""

from models import Lead, LeadScore, HiringSignal, Company
from company_research import compute_ai_readiness_signals, AI_READINESS_SIGNALS


# Scoring weights (total max = 100)
WEIGHTS = {
    "hiring_signal": 25,      # Are they actively hiring AI/ML/automation talent?
    "company_size": 15,       # Right size to need outside help?
    "tech_stack": 20,         # Do they have infrastructure to support AI?
    "funding_growth": 15,     # Are they growing / funded?
    "industry_fit": 15,       # Is their industry a good fit for AI automation?
    "recency": 10,            # How recent are the signals?
}

# Industries with high AI automation demand
HIGH_DEMAND_INDUSTRIES = {
    "finance": 15,
    "healthcare": 15,
    "insurance": 14,
    "logistics": 13,
    "manufacturing": 13,
    "legal": 12,
    "real_estate": 12,
    "e-commerce": 11,
    "marketing": 11,
    "saas": 10,
    "retail": 10,
    "education": 9,
    "consulting": 9,
    "government": 8,
    "nonprofit": 6,
}

# Company size sweet spot for AI consulting (mid-market)
SIZE_SCORES = {
    "1-50": 5,        # May lack budget
    "51-200": 12,     # Sweet spot for initial projects
    "201-1000": 15,   # Ideal - enough budget, real problems
    "1001-5000": 13,  # Great but sales cycle longer
    "5000+": 10,      # Enterprise - slow but high value
}


def score_hiring_signals(lead: Lead) -> tuple[int, dict]:
    """Score based on hiring signals. Returns (score, breakdown)."""
    if not lead.hiring_signals:
        return 0, {"count": 0, "signals": []}
    
    signal_scores = {
        HiringSignal.AI_ENGINEER: 25,
        HiringSignal.ML_ENGINEER: 22,
        HiringSignal.CHIEF_AI_OFFICER: 25,
        HiringSignal.AUTOMATION_ENGINEER: 20,
        HiringSignal.AI_CONSULTANT: 18,
        HiringSignal.RPA_DEVELOPER: 15,
        HiringSignal.DATA_SCIENTIST: 12,
        HiringSignal.PRODUCT_MANAGER_AI: 16,
    }
    
    total = 0
    signal_names = []
    for signal in lead.hiring_signals:
        pts = signal_scores.get(signal.signal_type, 5)
        total += pts
        signal_names.append(f"{signal.signal_type.value} ({signal.source_platform})")
    
    # Cap at max weight
    score = min(total, WEIGHTS["hiring_signal"])
    # Bonus for multiple signals (they're serious about AI)
    if len(lead.hiring_signals) >= 3:
        score = min(score + 3, WEIGHTS["hiring_signal"])
    elif len(lead.hiring_signals) >= 2:
        score = min(score + 1, WEIGHTS["hiring_signal"])
    
    return score, {"count": len(lead.hiring_signals), "signals": signal_names}


def score_company_size(lead: Lead) -> tuple[int, dict]:
    """Score based on company size."""
    size = lead.company.company_size
    score = SIZE_SCORES.get(size, 5)
    return score, {"size": size, "score": score}


def score_tech_stack(lead: Lead) -> tuple[int, dict]:
    """Score based on tech stack - more mature stack = better AI candidate."""
    tech = lead.company.tech_stack
    if not tech:
        return 5, {"count": 0, "assessment": "No tech stack data - assume minimal"}
    
    score = 0
    tech_lower = " ".join(tech).lower()
    
    # Cloud infrastructure = can deploy AI
    if any(t in tech_lower for t in ["aws", "azure", "gcp", "kubernetes", "docker"]):
        score += 6
    
    # Data infrastructure = has data to work with
    if any(t in tech_lower for t in ["spark", "airflow", "snowflake", "bigquery", "redshift", "kafka"]):
        score += 5
    
    # Modern languages = can integrate AI
    if any(t in tech_lower for t in ["python", "typescript", "node.js", "go", "rust"]):
        score += 4
    
    # Existing ML/AI tools
    if any(t in tech_lower for p in ["tensorflow", "pytorch", "langchain", "openai", "mlflow", "kubeflow"] for t in [p]):
        score += 5
    
    # API-first architecture
    if any(t in tech_lower for t in ["rest", "graphql", "grpc", "webhook"]):
        score += 3
    
    # Cap
    score = min(score, WEIGHTS["tech_stack"])
    return score, {"count": len(tech), "top_tech": tech[:5]}


def score_funding_and_growth(lead: Lead) -> tuple[int, dict]:
    """Score based on funding/growth signals."""
    score = 0
    details = {}
    
    funding = (lead.company.funding_stage or "").lower()
    funding_scores = {
        "bootstrapped": 4,
        "seed": 8,
        "series a": 12,
        "series b": 14,
        "series c": 13,
        "series d": 12,
        "pre-ipo": 10,
        "public": 10,
        "acquired": 8,
    }
    for key, pts in funding_scores.items():
        if key in funding:
            score = pts
            details["funding_stage"] = key
            break
    else:
        score = 6
        details["funding_stage"] = funding or "unknown"
    
    # Revenue range as growth signal
    revenue = (lead.company.revenue_range or "").lower()
    if "100m" in revenue or "1b" in revenue:
        score = min(score + 1, WEIGHTS["funding_growth"])
    elif "10m" in revenue or "50m" in revenue:
        score = min(score + 0, WEIGHTS["funding_growth"])
    
    return score, details


def score_industry_fit(lead: Lead) -> tuple[int, dict]:
    """Score based on how good an industry is for AI automation."""
    industry = (lead.company.industry or "").lower()
    score = HIGH_DEMAND_INDUSTRIES.get(industry, 5)
    return score, {"industry": industry}


def score_recency(lead: Lead) -> tuple[int, dict]:
    """Score based on how recent the hiring signals are."""
    if not lead.hiring_signals:
        return 3, {"assessment": "No hiring signals - base score"}
    
    # In a real system, parse dates. Here we assume signals are recent.
    # Score full marks since we discovered them now.
    return WEIGHTS["recency"], {"assessment": "All signals discovered within search window"}


def score_lead(lead: Lead) -> LeadScore:
    """Compute total lead score from all dimensions."""
    hiring_score, hiring_breakdown = score_hiring_signals(lead)
    size_score, size_breakdown = score_company_size(lead)
    tech_score, tech_breakdown = score_tech_stack(lead)
    funding_score, funding_breakdown = score_funding_and_growth(lead)
    industry_score, industry_breakdown = score_industry_fit(lead)
    recency_score, recency_breakdown = score_recency(lead)
    
    total = (
        hiring_score + size_score + tech_score +
        funding_score + industry_score + recency_score
    )
    
    return LeadScore(
        total_score=total,
        hiring_signal_score=hiring_score,
        company_size_score=size_score,
        tech_stack_score=tech_score,
        funding_growth_score=funding_score,
        industry_fit_score=industry_score,
        recency_score=recency_score,
        breakdown={
            "hiring_signals": hiring_breakdown,
            "company_size": size_breakdown,
            "tech_stack": tech_breakdown,
            "funding_growth": funding_breakdown,
            "industry_fit": industry_breakdown,
            "recency": recency_breakdown,
        }
    )


def get_priority_tier(score: int) -> str:
    """Return priority tier based on total score."""
    if score >= 80:
        return "HOT - Priority outreach"
    elif score >= 65:
        return "WARM - Strong candidate"
    elif score >= 50:
        return "LUKEWARM - Worth researching"
    else:
        return "COLD - Low priority"


def filter_qualified_leads(leads: list[Lead], min_score: int = 50) -> list[Lead]:
    """Filter leads that meet minimum score threshold."""
    return [l for l in leads if l.lead_score and l.lead_score.total_score >= min_score]
