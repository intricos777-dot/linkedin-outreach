<!-- Watermark: Living_Sin (intricos777-dot) + AI agents (Hermes, Lia, opencode) - collaborative work -->
# LinkedIn Lead Research & Outreach Management System

A legitimate lead research and outreach management system for AI automation services.

## Philosophy

- **NO automated LinkedIn messaging** — all messages require human review and manual sending
- **NO spam** — every message is personalized and reviewed before sending
- **Research-first** — find companies actively investing in AI/automation
- **Human-in-the-loop** — structured review queue with approval workflow

## Features

1. **Lead Discovery** — Searches for companies hiring AI/ML/automation talent
2. **Company Research** — Infers tech stack, industry signals, and AI readiness
3. **Lead Scoring** — Multi-dimensional scoring (hiring signals, company size, tech stack, funding, industry fit, recency)
4. **Message Templates** — Industry-specific, personalized outreach templates
5. **Review Queue** — Human approval workflow before any message is sent
6. **Pipeline Management** — CSV/JSON export for tracking and analysis
7. **Reporting** — Comprehensive pipeline analytics

## Usage

```bash
# Run full pipeline
python main.py run-all

# Individual steps
python main.py discover    # Find and score leads
python main.py draft       # Generate outreach drafts
python main.py enqueue     # Add to review queue
python main.py review      # Show pending reviews
python main.py approve ID  # Approve a message
python main.py reject ID   # Reject a message
python main.py report      # Generate report
python main.py stats       # Quick statistics
```

## Output Files

- `data/leads_pipeline.csv` — Spreadsheet-friendly lead data
- `data/leads_full.json` — Full lead data with all fields
- `data/review_queue.json` — Current review queue state
- `data/review_decisions.json` — Audit log of all review decisions
- `output/pipeline_report.txt` — Comprehensive pipeline report
- `output/outreach_drafts.txt` — All drafted messages

## Scoring System (100 points)

| Dimension | Max | Description |
|-----------|-----|-------------|
| Hiring Signals | 25 | Are they hiring AI/ML talent? |
| Company Size | 15 | Right size for consulting engagement? |
| Tech Stack | 20 | Do they have infrastructure for AI? |
| Funding/Growth | 15 | Are they growing/funded? |
| Industry Fit | 15 | Is their industry ripe for AI automation? |
| Recency | 10 | How recent are the signals? |

### Priority Tiers

- **🔥 HOT (80-100)** — Priority outreach
- **🟡 WARM (65-79)** — Strong candidate
- **⚪ LUKEWARM (50-64)** — Worth researching
- **❄️ COLD (0-49)** — Low priority

## Compliance Notes

- All messages require human review before sending
- No automated LinkedIn messaging — manual send only
- Respect opt-out and anti-spam regulations (CAN-SPAM, GDPR)
- Personalize each message — no bulk sending
- Track responses and update lead status accordingly
