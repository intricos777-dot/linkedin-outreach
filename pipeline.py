# Watermark: Living_Sin (intricos777-dot) + AI agents (Hermes, Lia, opencode) - collaborative work
# Copyright (c) 2026 Living Sin (intricos777-dot) + AI agents (Hermes, Lia, opencode) - collaborative work
# Licensed under Living Sin Proprietary License (LSPL-1.0)
# See LICENSE file for details.
"""Pipeline management - CSV/JSON persistence and lead lifecycle management."""

import csv
import json
import os
from datetime import datetime
from typing import Optional
from models import Lead, LeadStatus
from company_research import generate_company_summary


CSV_COLUMNS = [
    "id", "company_name", "industry", "company_size", "location",
    "hiring_signals_count", "hiring_signal_types",
    "total_score", "priority_tier", "status",
    "contact_person", "contact_title", "contact_linkedin",
    "outreach_subject", "outreach_preview",
    "created_at", "updated_at",
    "reviewed_by", "review_date", "review_notes",
    "tech_stack", "funding_stage", "glassdoor_rating",
    "linkedin_url", "indeed_url", "website",
    "notes",
]


class Pipeline:
    """Manages lead data with CSV and JSON persistence."""
    
    def __init__(self, workspace_dir: str):
        self.workspace = workspace_dir
        self.csv_path = os.path.join(workspace_dir, "data", "leads_pipeline.csv")
        self.json_path = os.path.join(workspace_dir, "data", "leads_full.json")
        self.leads: list[Lead] = []
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
    
    def add_leads(self, leads: list[Lead]):
        """Add new leads to the pipeline, avoiding duplicates by company name."""
        existing_names = {l.company.name.lower() for l in self.leads}
        new_count = 0
        for lead in leads:
            if lead.company.name.lower() not in existing_names:
                self.leads.append(lead)
                existing_names.add(lead.company.name.lower())
                new_count += 1
        print(f"  Added {new_count} new leads ({len(leads) - new_count} duplicates skipped)")
    
    def save_csv(self):
        """Export leads to CSV for easy review in spreadsheet tools."""
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for lead in self.leads:
                writer.writerow(self._lead_to_csv_row(lead))
        print(f"  CSV saved: {self.csv_path} ({len(self.leads)} leads)")
    
    def save_json(self):
        """Export full lead data to JSON for programmatic access."""
        data = {
            "exported_at": datetime.now().isoformat(),
            "total_leads": len(self.leads),
            "leads": [lead.to_dict() for lead in self.leads],
        }
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"  JSON saved: {self.json_path}")
    
    def load_json(self) -> bool:
        """Load leads from JSON file."""
        if not os.path.exists(self.json_path):
            return False
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Note: In production, would reconstruct Lead objects from dict
        print(f"  Loaded {data.get('total_leads', 0)} leads from {self.json_path}")
        return True
    
    def _lead_to_csv_row(self, lead: Lead) -> dict:
        """Convert Lead to CSV row dict."""
        signal_types = "; ".join(s.signal_type.value for s in lead.hiring_signals)
        score_str = str(lead.lead_score.total_score) if lead.lead_score else ""
        
        from scoring import get_priority_tier
        tier = get_priority_tier(lead.lead_score.total_score) if lead.lead_score else ""
        
        return {
            "id": lead.id,
            "company_name": lead.company.name,
            "industry": lead.company.industry or "",
            "company_size": lead.company.company_size or "",
            "location": lead.company.location or "",
            "hiring_signals_count": str(len(lead.hiring_signals)),
            "hiring_signal_types": signal_types,
            "total_score": score_str,
            "priority_tier": tier,
            "status": lead.status,
            "contact_person": lead.contact_person or "",
            "contact_title": lead.contact_title or "",
            "contact_linkedin": lead.contact_linkedin or "",
            "outreach_subject": lead.outreach_subject or "",
            "outreach_preview": (lead.outreach_message or "")[:100],
            "created_at": lead.created_at,
            "updated_at": lead.updated_at,
            "reviewed_by": lead.reviewed_by or "",
            "review_date": lead.review_date or "",
            "review_notes": lead.review_notes or "",
            "tech_stack": "; ".join(lead.company.tech_stack),
            "funding_stage": lead.company.funding_stage or "",
            "glassdoor_rating": str(lead.company.glassdoor_rating or ""),
            "linkedin_url": lead.company.linkedin_url or "",
            "indeed_url": lead.company.indeed_url or "",
            "website": lead.company.website or "",
            "notes": "; ".join(lead.notes),
        }
    
    def get_leads_by_status(self, status: str) -> list[Lead]:
        return [l for l in self.leads if l.status == status]
    
    def get_leads_by_min_score(self, min_score: int) -> list[Lead]:
        return [l for l in self.leads if l.lead_score and l.lead_score.total_score >= min_score]
    
    def get_leads_by_industry(self, industry: str) -> list[Lead]:
        return [l for l in self.leads if l.company.industry and l.company.industry.lower() == industry.lower()]
    
    def get_leads_by_priority(self, min_score: int = 65) -> list[Lead]:
        """Get hot/warm leads sorted by score descending."""
        qualified = self.get_leads_by_min_score(min_score)
        return sorted(qualified, key=lambda l: l.lead_score.total_score if l.lead_score else 0, reverse=True)
    
    def update_lead(self, lead_id: str, **kwargs):
        """Update lead fields."""
        for lead in self.leads:
            if lead.id == lead_id:
                for key, value in kwargs.items():
                    if hasattr(lead, key):
                        setattr(lead, key, value)
                    elif hasattr(lead.company, key):
                        setattr(lead.company, key, value)
                lead.updated_at = datetime.now().isoformat()
                return True
        return False
    
    def get_statistics(self) -> dict:
        """Return pipeline statistics."""
        total = len(self.leads)
        scored = sum(1 for l in self.leads if l.lead_score)
        with_messages = sum(1 for l in self.leads if l.outreach_message)
        in_review = sum(1 for l in self.leads if l.status == LeadStatus.IN_REVIEW.value)
        approved = sum(1 for l in self.leads if l.status == LeadStatus.APPROVED.value)
        
        scores = [l.lead_score.total_score for l in self.leads if l.lead_score]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        industries = {}
        for l in self.leads:
            ind = l.company.industry or "unknown"
            industries[ind] = industries.get(ind, 0) + 1
        
        return {
            "total_leads": total,
            "scored": scored,
            "with_messages": with_messages,
            "in_review": in_review,
            "approved": approved,
            "average_score": round(avg_score, 1),
            "industry_distribution": industries,
        }
