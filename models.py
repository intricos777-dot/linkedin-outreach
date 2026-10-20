# Watermark: Living_Sin (intricos777-dot) + AI agents (Hermes, Lia, opencode) - collaborative work
# Copyright (c) 2026 Living Sin (intricos777-dot) + AI agents (Hermes, Lia, opencode) - collaborative work
# Licensed under Living Sin Proprietary License (LSPL-1.0)
# See LICENSE file for details.
"""Data models for the LinkedIn Lead Research & Outreach Management System."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional


class LeadStatus(Enum):
    DISCOVERED = "discovered"
    RESEARCHED = "researched"
    SCORED = "scored"
    DRAFTED = "drafted"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT = "sent"
    RESPONDED = "responded"


class HiringSignal(Enum):
    AI_ENGINEER = "hiring_ai_engineer"
    ML_ENGINEER = "hiring_ml_engineer"
    AUTOMATION_ENGINEER = "hiring_automation_engineer"
    DATA_SCIENTIST = "hiring_data_scientist"
    AI_CONSULTANT = "hiring_ai_consultant"
    RPA_DEVELOPER = "hiring_rpa_developer"
    PRODUCT_MANAGER_AI = "hiring_pm_ai"
    CHIEF_AI_OFFICER = "hiring_chief_ai_officer"


@dataclass
class Company:
    name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None  # "1-50", "51-200", "201-1000", "1001-5000", "5000+"
    location: Optional[str] = None
    glassdoor_rating: Optional[float] = None
    linkedin_url: Optional[str] = None
    indeed_url: Optional[str] = None
    tech_stack: list = field(default_factory=list)
    funding_stage: Optional[str] = None
    revenue_range: Optional[str] = None
    description: Optional[str] = None


@dataclass
class HiringSignalData:
    signal_type: HiringSignal
    source_url: str
    source_platform: str  # "linkedin", "glassdoor", "indeed"
    job_title: str
    discovered_date: str = field(default_factory=lambda: datetime.now().isoformat())
    salary_range: Optional[str] = None
    is_remote: bool = False


@dataclass
class LeadScore:
    total_score: int = 0
    hiring_signal_score: int = 0
    company_size_score: int = 0
    tech_stack_score: int = 0
    funding_growth_score: int = 0
    industry_fit_score: int = 0
    recency_score: int = 0
    breakdown: dict = field(default_factory=dict)


@dataclass
class Lead:
    id: str
    company: Company
    hiring_signals: list = field(default_factory=list)
    lead_score: Optional[LeadScore] = None
    status: str = LeadStatus.DISCOVERED.value
    outreach_message: Optional[str] = None
    outreach_subject: Optional[str] = None
    contact_person: Optional[str] = None
    contact_title: Optional[str] = None
    contact_linkedin: Optional[str] = None
    notes: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    reviewed_by: Optional[str] = None
    review_date: Optional[str] = None
    review_notes: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MessageTemplate:
    name: str
    template_text: str
    subject_line: str
    industry_tags: list = field(default_factory=list)
    company_size_target: Optional[str] = None
    tone: str = "professional"  # professional, casual, technical, executive
    personalization_slots: list = field(default_factory=list)
