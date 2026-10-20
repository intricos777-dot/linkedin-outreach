# Watermark: Living_Sin (intricos777-dot) + AI agents (Hermes, Lia, opencode) - collaborative work
"""Review queue system - manages human approval workflow for outreach messages."""

import os
import json
from datetime import datetime
from typing import Optional
from models import Lead, LeadStatus


class ReviewQueue:
    """
    Manages the human review workflow for outreach messages.
    
    Philosophy: Every message MUST be reviewed by a human before sending.
    This system creates a structured review queue and tracks decisions.
    """
    
    def __init__(self, workspace_dir: str):
        self.workspace = workspace_dir
        self.queue_path = os.path.join(workspace_dir, "data", "review_queue.json")
        self.decisions_path = os.path.join(workspace_dir, "data", "review_decisions.json")
        self._ensure_dirs()
        self.queue = self._load_queue()
        self.decisions = self._load_decisions()
    
    def _ensure_dirs(self):
        os.makedirs(os.path.dirname(self.queue_path), exist_ok=True)
    
    def _load_queue(self) -> list[dict]:
        if os.path.exists(self.queue_path):
            with open(self.queue_path, "r") as f:
                return json.load(f)
        return []
    
    def _load_decisions(self) -> list[dict]:
        if os.path.exists(self.decisions_path):
            with open(self.decisions_path, "r") as f:
                return json.load(f)
        return []
    
    def _save_queue(self):
        with open(self.queue_path, "w") as f:
            json.dump(self.queue, f, indent=2, default=str)
    
    def _save_decisions(self):
        with open(self.decisions_path, "w") as f:
            json.dump(self.decisions, f, indent=2, default=str)
    
    def enqueue(self, lead: Lead) -> str:
        """Add a lead's outreach message to the review queue."""
        entry = {
            "queue_id": f"REV-{lead.id[:8]}",
            "lead_id": lead.id,
            "company_name": lead.company.name,
            "industry": lead.company.industry,
            "priority_tier": self._get_tier(lead),
            "total_score": lead.lead_score.total_score if lead.lead_score else 0,
            "contact_person": lead.contact_person,
            "contact_title": lead.contact_title,
            "outreach_subject": lead.outreach_subject,
            "outreach_message": lead.outreach_message,
            "template_used": getattr(lead, '_template_used', 'unknown'),
            "status": "pending",
            "queued_at": datetime.now().isoformat(),
            "reviewed_at": None,
            "reviewed_by": None,
            "decision": None,  # "approved", "rejected", "needs_revision"
            "review_notes": None,
            "revision_notes": None,
        }
        self.queue.append(entry)
        self._save_queue()
        lead.status = LeadStatus.IN_REVIEW.value
        lead.updated_at = datetime.now().isoformat()
        return entry["queue_id"]
    
    def _get_tier(self, lead: Lead) -> str:
        from scoring import get_priority_tier
        return get_priority_tier(lead.lead_score.total_score if lead.lead_score else 0)
    
    def get_pending(self) -> list[dict]:
        """Get all pending review items."""
        return [item for item in self.queue if item["status"] == "pending"]
    
    def get_by_lead_id(self, lead_id: str) -> Optional[dict]:
        """Find queue entry by lead ID."""
        for item in self.queue:
            if item["lead_id"] == lead_id:
                return item
        return None
    
    def approve(self, queue_id: str, reviewer: str, notes: str = "") -> bool:
        """Approve a message for sending."""
        for item in self.queue:
            if item["queue_id"] == queue_id:
                item["status"] = "approved"
                item["decision"] = "approved"
                item["reviewed_by"] = reviewer
                item["reviewed_at"] = datetime.now().isoformat()
                item["review_notes"] = notes
                self._save_queue()
                self._record_decision(item, reviewer, "approved", notes)
                return True
        return False
    
    def reject(self, queue_id: str, reviewer: str, notes: str = "") -> bool:
        """Reject a message."""
        for item in self.queue:
            if item["queue_id"] == queue_id:
                item["status"] = "rejected"
                item["decision"] = "rejected"
                item["reviewed_by"] = reviewer
                item["reviewed_at"] = datetime.now().isoformat()
                item["review_notes"] = notes
                self._save_queue()
                self._record_decision(item, reviewer, "rejected", notes)
                return True
        return False
    
    def request_revision(self, queue_id: str, reviewer: str, revision_notes: str) -> bool:
        """Request changes to a message."""
        for item in self.queue:
            if item["queue_id"] == queue_id:
                item["status"] = "needs_revision"
                item["decision"] = "needs_revision"
                item["reviewed_by"] = reviewer
                item["reviewed_at"] = datetime.now().isoformat()
                item["revision_notes"] = revision_notes
                self._save_queue()
                self._record_decision(item, reviewer, "needs_revision", revision_notes)
                return True
        return False
    
    def _record_decision(self, item: dict, reviewer: str, decision: str, notes: str):
        """Record decision in the audit log."""
        self.decisions.append({
            "queue_id": item["queue_id"],
            "lead_id": item["lead_id"],
            "company_name": item["company_name"],
            "decision": decision,
            "reviewer": reviewer,
            "notes": notes,
            "timestamp": datetime.now().isoformat(),
        })
        self._save_decisions()
    
    def get_decision_log(self) -> list[dict]:
        """Get full audit log of all review decisions."""
        return self.decisions
    
    def get_statistics(self) -> dict:
        """Get review queue statistics."""
        pending = sum(1 for i in self.queue if i["status"] == "pending")
        approved = sum(1 for i in self.queue if i["status"] == "approved")
        rejected = sum(1 for i in self.queue if i["status"] == "rejected")
        needs_revision = sum(1 for i in self.queue if i["status"] == "needs_revision")
        return {
            "total_reviewed": len(self.queue),
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "needs_revision": needs_revision,
        }
    
    def print_review_card(self, queue_item: dict):
        """Print a formatted review card for a queue item."""
        print("=" * 70)
        print(f"  REVIEW CARD: {queue_item['queue_id']}")
        print(f"  Company: {queue_item['company_name']} ({queue_item['industry']})")
        print(f"  Priority: {queue_item['priority_tier']} | Score: {queue_item['total_score']}/100")
        print(f"  Contact: {queue_item['contact_person'] or 'TBD'} ({queue_item['contact_title'] or 'TBD'})")
        print(f"  Template: {queue_item['template_used']}")
        print("-" * 70)
        print(f"  SUBJECT: {queue_item['outreach_subject']}")
        print("-" * 70)
        print("  MESSAGE:")
        for line in queue_item['outreach_message'].split('\n'):
            print(f"    {line}")
        print("=" * 70)
