# Watermark: Living_Sin (intricos777-dot) + AI agents (Hermes, Lia, opencode) - collaborative work
# Copyright (c) 2026 Living Sin (intricos777-dot) + AI agents (Hermes, Lia, opencode) - collaborative work
# Licensed under Living Sin Proprietary License (LSPL-1.0)
# See LICENSE file for details.
"""Report generator - creates summary reports and analytics."""

import os
from datetime import datetime
from typing import Optional
from models import Lead
from scoring import get_priority_tier


class ReportGenerator:
    """Generates human-readable reports from pipeline data."""
    
    def __init__(self, workspace_dir: str):
        self.workspace = workspace_dir
        self.report_dir = os.path.join(workspace_dir, "output")
        os.makedirs(self.report_dir, exist_ok=True)
    
    def generate_full_report(self, leads: list[Lead], stats: dict, queue_stats: dict) -> str:
        """Generate a comprehensive pipeline report."""
        lines = []
        lines.append("=" * 70)
        lines.append("  LINKEDIN LEAD RESEARCH & OUTREACH MANAGEMENT SYSTEM")
        lines.append(f"  Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 70)
        lines.append("")
        
        # Pipeline Overview
        lines.append("## PIPELINE OVERVIEW")
        lines.append(f"  Total Leads Discovered: {stats['total_leads']}")
        lines.append(f"  Leads Scored: {stats['scored']}")
        lines.append(f"  Messages Drafted: {stats['with_messages']}")
        lines.append(f"  Average Lead Score: {stats['average_score']}/100")
        lines.append("")
        
        # Review Queue
        lines.append("## REVIEW QUEUE STATUS")
        lines.append(f"  Pending Review: {queue_stats['pending']}")
        lines.append(f"  Approved: {queue_stats['approved']}")
        lines.append(f"  Rejected: {queue_stats['rejected']}")
        lines.append(f"  Needs Revision: {queue_stats['needs_revision']}")
        lines.append("")
        
        # Industry Distribution
        lines.append("## INDUSTRY DISTRIBUTION")
        for industry, count in sorted(stats['industry_distribution'].items(), key=lambda x: -x[1]):
            lines.append(f"  {industry}: {count} leads")
        lines.append("")
        
        # Top Leads
        lines.append("## TOP PRIORITY LEADS (Score >= 65)")
        top_leads = sorted(
            [l for l in leads if l.lead_score and l.lead_score.total_score >= 65],
            key=lambda l: l.lead_score.total_score,
            reverse=True
        )
        for i, lead in enumerate(top_leads[:10], 1):
            score = lead.lead_score.total_score
            tier = get_priority_tier(score)
            signals = ", ".join(s.signal_type.value.replace("hiring_", "") for s in lead.hiring_signals[:3])
            lines.append(f"  {i}. {lead.company.name} ({lead.company.industry}) - Score: {score} [{tier}]")
            lines.append(f"     Signals: {signals}")
            lines.append(f"     Size: {lead.company.company_size} | Location: {lead.company.location}")
            if lead.outreach_subject:
                lines.append(f"     Draft Subject: {lead.outreach_subject[:60]}")
            lines.append("")
        
        # Scoring Breakdown for Top Lead
        if top_leads:
            lines.append("## SCORING BREAKDOWN - TOP LEAD")
            top = top_leads[0]
            ls = top.lead_score
            lines.append(f"  Company: {top.company.name}")
            lines.append(f"  Total Score: {ls.total_score}/100")
            lines.append(f"    Hiring Signals: {ls.hiring_signal_score}/25")
            lines.append(f"    Company Size:  {ls.company_size_score}/15")
            lines.append(f"    Tech Stack:    {ls.tech_stack_score}/20")
            lines.append(f"    Funding/Growth: {ls.funding_growth_score}/15")
            lines.append(f"    Industry Fit:  {ls.industry_fit_score}/15")
            lines.append(f"    Recency:       {ls.recency_score}/10")
            lines.append("")
        
        # Action Items
        lines.append("## RECOMMENDED ACTIONS")
        lines.append("  1. Review pending messages in the review queue")
        lines.append("  2. Research contact persons for HOT leads (score >= 80)")
        lines.append("  3. Customize templates with specific company details")
        lines.append("  4. Schedule outreach for approved messages")
        lines.append("  5. Follow up on previously sent messages after 5-7 days")
        lines.append("")
        
        # Compliance Note
        lines.append("## COMPLIANCE & ETHICS NOTES")
        lines.append("  - All messages require human review before sending")
        lines.append("  - No automated LinkedIn messaging - manual send only")
        lines.append("  - Respect opt-out and anti-spam regulations (CAN-SPAM, GDPR)")
        lines.append("  - Personalize each message - no bulk sending")
        lines.append("  - Track responses and update lead status accordingly")
        lines.append("")
        lines.append("=" * 70)
        
        report_text = "\n".join(lines)
        
        # Save report
        report_path = os.path.join(self.report_dir, "pipeline_report.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        
        return report_text
    
    def generate_outreach_drafts_report(self, leads: list[Lead]) -> str:
        """Generate a report of all drafted outreach messages."""
        lines = []
        lines.append("=" * 70)
        lines.append("  OUTBOUND MESSAGE DRAFTS - READY FOR REVIEW")
        lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 70)
        lines.append("")
        
        drafted = [l for l in leads if l.outreach_message]
        for i, lead in enumerate(drafted, 1):
            lines.append(f"--- Message {i}/{len(drafted)} ---")
            lines.append(f"To: {lead.contact_person or '[CONTACT TBD]'} ({lead.contact_title or '[TITLE TBD]'})")
            lines.append(f"Company: {lead.company.name}")
            lines.append(f"Subject: {lead.outreach_subject or '[NO SUBJECT]'}")
            lines.append("")
            lines.append(lead.outreach_message or "[NO MESSAGE]")
            lines.append("")
            lines.append("=" * 70)
            lines.append("")
        
        report_text = "\n".join(lines)
        
        report_path = os.path.join(self.report_dir, "outreach_drafts.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        
        return report_text
