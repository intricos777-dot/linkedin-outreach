#!/usr/bin/env python3
"""Lead Research & Outreach Management System - Main Orchestrator.

Usage:
    python main.py discover    - Find and score new leads
    python main.py draft       - Generate outreach drafts for scored leads
    python main.py review      - Show review queue (pending approvals)
    python main.py approve ID  - Approve a message for sending
    python main.py reject ID   - Reject a message
    python main.py report      - Generate pipeline report
    python main.py stats       - Show quick statistics
    python main.py run-all     - Full pipeline: discover → score → draft → enqueue
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from discovery import discover_leads
from scoring import score_lead, get_priority_tier
from company_research import infer_tech_stack
from templates.outreach_templates import select_template, generate_outreach
from pipeline import Pipeline
from review_queue import ReviewQueue
from reports import ReportGenerator
from models import LeadStatus


WORKSPACE = os.path.dirname(os.path.abspath(__file__))


def cmd_discover(pipeline: Pipeline):
    """Discover new leads and score them."""
    print("\n🔍 Discovering leads from target company research...")
    leads = discover_leads()
    pipeline.add_leads(leads)
    
    print(f"\n📊 Scoring {len(leads)} leads...")
    for lead in leads:
        # Infer tech stack if not fully populated
        if not lead.company.tech_stack:
            lead.company.tech_stack = infer_tech_stack(lead.company)
        
        # Score the lead
        lead.lead_score = score_lead(lead)
        lead.status = LeadStatus.SCORED.value
    
    # Show results
    scored_leads = sorted(
        [l for l in pipeline.leads if l.lead_score],
        key=lambda l: l.lead_score.total_score,
        reverse=True
    )
    
    print(f"\n{'='*70}")
    print(f"  LEAD SCORING RESULTS ({len(scored_leads)} total)")
    print(f"{'='*70}")
    for i, lead in enumerate(scored_leads, 1):
        score = lead.lead_score.total_score
        tier = get_priority_tier(score)
        tier_emoji = "🔥" if score >= 80 else "🟡" if score >= 65 else "⚪" if score >= 50 else "❄️"
        print(f"  {i:2d}. {tier_emoji} {lead.company.name:<25s} Score: {score:2d}/100  [{tier}]")
        signals = ", ".join(s.signal_type.value.replace("hiring_", "") for s in lead.hiring_signals[:2])
        print(f"       Signals: {signals}")
    
    # Save
    pipeline.save_csv()
    pipeline.save_json()
    print(f"\n✅ Pipeline saved ({len(pipeline.leads)} leads)")
    return pipeline


def cmd_draft(pipeline: Pipeline):
    """Generate outreach drafts for scored leads."""
    print("\n✍️  Generating personalized outreach messages...")
    
    # Get scored leads that haven't been drafted yet
    candidates = [
        l for l in pipeline.leads
        if l.lead_score and l.status in (LeadStatus.SCORED.value, LeadStatus.DISCOVERED.value)
        and l.lead_score.total_score >= 50
    ]
    
    drafted_count = 0
    for lead in candidates:
        subject, message = generate_outreach(lead)
        lead.outreach_subject = subject
        lead.outreach_message = message
        lead._template_used = select_template(lead).name
        lead.status = LeadStatus.DRAFTED.value
        lead.updated_at = datetime.now().isoformat()
        drafted_count += 1
        
        # Print preview
        tier = get_priority_tier(lead.lead_score.total_score)
        print(f"\n  [{tier}] {lead.company.name} (Score: {lead.lead_score.total_score})")
        print(f"  Subject: {subject[:70]}")
        print(f"  Preview: {message[:150].replace(chr(10), ' ')}...")
    
    pipeline.save_csv()
    pipeline.save_json()
    print(f"\n✅ {drafted_count} messages drafted")
    return pipeline


def cmd_enqueue(pipeline: Pipeline, review_queue: ReviewQueue):
    """Add drafted messages to the review queue."""
    print("\n📋 Adding messages to review queue...")
    
    drafted = [l for l in pipeline.leads if l.outreach_message and l.status == LeadStatus.DRAFTED.value]
    
    for lead in drafted:
        queue_id = review_queue.enqueue(lead)
        print(f"  📨 {lead.company.name} → Review Queue ({queue_id})")
    
    print(f"\n✅ {len(drafted)} messages queued for human review")
    return pipeline


def cmd_review(pipeline: Pipeline, review_queue: ReviewQueue):
    """Show review queue with pending items."""
    pending = review_queue.get_pending()
    
    if not pending:
        print("\n📋 Review Queue: No pending items! 🎉")
        return
    
    print(f"\n{'='*70}")
    print(f"  📋 REVIEW QUEUE ({len(pending)} pending)")
    print(f"{'='*70}\n")
    
    for item in pending:
        review_queue.print_review_card(item)
        print("\n  Options:")
        print(f"    Approve: python main.py approve {item['queue_id']}")
        print(f"    Reject:  python main.py reject {item['queue_id']}")
        print()


def cmd_approve(review_queue: Pipeline, queue_id: str, reviewer: str = "human_user"):
    """Approve a message for sending."""
    rq = review_queue if isinstance(review_queue, ReviewQueue) else ReviewQueue(WORKSPACE)
    if rq.approve(queue_id, reviewer):
        print(f"✅ {queue_id} APPROVED for sending")
        print("   ⚠️  Remember: Send manually through LinkedIn - no automation!")
    else:
        print(f"❌ Could not find {queue_id} in queue")


def cmd_reject(review_queue, queue_id: str, reviewer: str = "human_user"):
    """Reject a message."""
    rq = review_queue if isinstance(review_queue, ReviewQueue) else ReviewQueue(WORKSPACE)
    if rq.reject(queue_id, reviewer):
        print(f"❌ {queue_id} REJECTED")
    else:
        print(f"⚠️  Could not find {queue_id} in queue")


def cmd_report(pipeline: Pipeline, review_queue: ReviewQueue):
    """Generate comprehensive pipeline report."""
    print("\n📊 Generating reports...")
    
    stats = pipeline.get_statistics()
    queue_stats = review_queue.get_statistics()
    
    reporter = ReportGenerator(WORKSPACE)
    
    # Full pipeline report
    report = reporter.generate_full_report(pipeline.leads, stats, queue_stats)
    print(report)
    
    # Outreach drafts report
    reporter.generate_outreach_drafts_report(pipeline.leads)
    
    print(f"\n📁 Reports saved to: {os.path.join(WORKSPACE, 'output')}/")
    print("   - pipeline_report.txt")
    print("   - outreach_drafts.txt")


def cmd_stats(pipeline: Pipeline, review_queue: ReviewQueue):
    """Show quick statistics."""
    stats = pipeline.get_statistics()
    queue_stats = review_queue.get_statistics()
    
    print(f"\n{'='*50}")
    print(f"  📊 PIPELINE STATISTICS")
    print(f"{'='*50}")
    print(f"  Total Leads:     {stats['total_leads']}")
    print(f"  Scored:          {stats['scored']}")
    print(f"  Messages Drafted: {stats['with_messages']}")
    print(f"  Average Score:   {stats['average_score']}/100")
    print(f"  In Review Queue: {stats['in_review']}")
    print(f"  Approved:        {stats['approved']}")
    print(f"{'='*50}")
    print(f"  📋 REVIEW QUEUE")
    print(f"  Pending:         {queue_stats['pending']}")
    print(f"  Approved:        {queue_stats['approved']}")
    print(f"  Rejected:        {queue_stats['rejected']}")
    print(f"  Needs Revision:  {queue_stats['needs_revision']}")
    print(f"{'='*50}")


def cmd_run_all():
    """Run the full pipeline end-to-end."""
    print("=" * 70)
    print("  🚀 LEAD RESEARCH & OUTREACH MANAGEMENT SYSTEM")
    print("  Full Pipeline Execution")
    print("=" * 70)
    
    pipeline = Pipeline(WORKSPACE)
    review_queue = ReviewQueue(WORKSPACE)
    
    # Step 1: Discover
    print("\n━━━ STEP 1: DISCOVER & SCORE ━━━")
    cmd_discover(pipeline)
    
    # Step 2: Draft
    print("\n━━━ STEP 2: DRAFT OUTREACH ━━━")
    cmd_draft(pipeline)
    
    # Step 3: Enqueue for review
    print("\n━━━ STEP 3: ENQUEUE FOR REVIEW ━━━")
    cmd_enqueue(pipeline, review_queue)
    
    # Step 4: Show review queue
    print("\n━━━ STEP 4: REVIEW QUEUE ━━━")
    cmd_review(pipeline, review_queue)
    
    # Step 5: Generate report
    print("\n━━━ STEP 5: GENERATE REPORT ━━━")
    cmd_report(pipeline, review_queue)
    
    print("\n" + "=" * 70)
    print("  ✅ PIPELINE COMPLETE")
    print("  Next steps: Review messages and approve/reject in the queue")
    print("=" * 70)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    pipeline = Pipeline(WORKSPACE)
    review_queue = ReviewQueue(WORKSPACE)
    
    if command == "run-all":
        cmd_run_all()
    elif command == "discover":
        cmd_discover(pipeline)
    elif command == "draft":
        cmd_draft(pipeline)
    elif command == "enqueue":
        cmd_enqueue(pipeline, review_queue)
    elif command == "review":
        cmd_review(pipeline, review_queue)
    elif command == "approve":
        if len(sys.argv) < 3:
            print("Usage: python main.py approve <queue_id>")
            sys.exit(1)
        cmd_approve(review_queue, sys.argv[2])
    elif command == "reject":
        if len(sys.argv) < 3:
            print("Usage: python main.py reject <queue_id>")
            sys.exit(1)
        cmd_reject(review_queue, sys.argv[2])
    elif command == "report":
        cmd_report(pipeline, review_queue)
    elif command == "stats":
        cmd_stats(pipeline, review_queue)
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
