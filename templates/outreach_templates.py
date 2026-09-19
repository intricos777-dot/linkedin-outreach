"""Message template library and personalized outreach generation."""

from models import Lead, MessageTemplate
from company_research import generate_company_summary
from scoring import get_priority_tier


# ---- Template definitions ----

TEMPLATES = [
    MessageTemplate(
        name="hiring_signal_ai_engineer",
        subject_line="Saw you're hiring {job_title} — happy to help accelerate",
        template_text="""Hi {contact_first_name},

I noticed {company_name} is currently hiring for a {job_title} position. That's a strong signal you're investing in AI/automation capabilities — which is exactly the kind of work we specialize in.

We help companies like {company_name} bridge the gap between hiring and production AI systems. While you build out your team, we can deliver working AI agents and automation workflows in weeks, not months.

A few recent examples:
- Built a document-processing agent for a mid-size {industry} firm that cut processing time by 70%
- Automated customer onboarding workflows for a Series B fintech company
- Created an internal research agent that saves a 20-person data team 10+ hours/week

Would it make sense to hop on a 15-minute call this week? I'd love to learn about your AI roadmap and see if there's a way to help.

Best,
{sender_name}
{sender_title}""",
        industry_tags=["finance", "healthcare", "saas", "logistics", "insurance"],
        company_size_target="51-1000",
        tone="professional",
        personalization_slots=["contact_first_name", "company_name", "job_title", "industry", "sender_name", "sender_title"],
    ),

    MessageTemplate(
        name="industry_specific_roi",
        subject_line="AI automation opportunities for {industry} companies",
        template_text="""Hi {contact_first_name},

I've been researching {industry} companies that are ahead of the curve on AI adoption — {company_name} stands out.

{company_summary}

Based on your {company_size} team size and {tech_stack_summary} stack, I see some clear opportunities where AI agents could deliver ROI within the first quarter:

{roi_opportunities}

We specialize in building production-grade AI automation for {industry} companies — not demos or proofs-of-concept, but systems that run 24/7 and handle real workflows.

Open to a quick call to explore whether this is a priority for {company_name} right now?

Best,
{sender_name}""",
        industry_tags=["finance", "healthcare", "logistics", "legal", "insurance"],
        tone="consultative",
        personalization_slots=["contact_first_name", "company_name", "industry", "company_size",
                               "tech_stack_summary", "roi_opportunities", "company_summary", "sender_name"],
    ),

    MessageTemplate(
        name="tech_stack_integration",
        subject_line="Your {primary_tech} stack + AI agents",
        template_text="""Hi {contact_first_name},

I was looking at {company_name}'s engineering setup — particularly your {primary_tech} infrastructure. It's a great foundation for layering AI agents on top.

Companies with mature {primary_tech} deployments tend to get the fastest ROI from AI automation because:
1. The data pipelines are already in place
2. Your team understands API-first architecture
3. Integration points are well-documented

We've built AI agents that plug directly into stacks like yours, handling tasks like:
- Intelligent document processing
- Workflow orchestration
- Customer-facing chat/voice agents
- Data pipeline monitoring and remediation

Would you be open to a 15-minute technical conversation? I'd love to share what's possible with your current setup.

Best,
{sender_name}""",
        tone="technical",
        personalization_slots=["contact_first_name", "company_name", "primary_tech", "sender_name"],
    ),

    MessageTemplate(
        name="scaling_signal",
        subject_line="Scaling {company_name} with AI — quick thought",
        template_text="""Hi {contact_first_name},

Congrats on the growth at {company_name}. Hiring {open_roles_count} roles simultaneously is a clear signal you're scaling fast.

Here's a pattern I've seen with {company_size} {industry} companies: the operations team usually maxes out before the product team. While you're hiring engineers to build features, back-office workflows (customer support, data entry, reporting, compliance checks) start creating bottlenecks.

AI agents are uniquely suited to absorb that operational load without adding headcount. We typically help companies:
- Automate 30-50% of repetitive operational tasks in the first 90 days
- Free up existing staff for higher-value work
- Scale processes without scaling the team

Is operational efficiency on your radar this quarter? Happy to share a few relevant case studies.

Best,
{sender_name}""",
        tone="executive",
        personalization_slots=["contact_first_name", "company_name", "open_roles_count",
                               "company_size", "industry", "sender_name"],
    ),

    MessageTemplate(
        name="warm_intro_style",
        subject_line="Quick question about {company_name}'s AI plans",
        template_text="""Hi {contact_first_name},

I hope this finds you well. I've been following {company_name}'s work in the {industry} space and I'm impressed by {specific_observation}.

I'm reaching out because we help companies at your stage implement AI automation that delivers measurable ROI — typically within the first quarter.

Rather than a sales pitch, I'd love to simply learn about your current priorities and share a few ideas that might be relevant. No strings attached.

Would you have 15 minutes in the next week or two?

Best,
{sender_name}""",
        tone="casual",
        personalization_slots=["contact_first_name", "company_name", "industry",
                               "specific_observation", "sender_name"],
    ),
]


def select_template(lead: Lead) -> MessageTemplate:
    """Select the best template based on lead attributes."""
    industry = (lead.company.industry or "").lower()
    size = lead.company.company_size or ""
    signals = lead.hiring_signals
    
    # If they're hiring AI/ML talent, use the hiring signal template
    if any(s.signal_type.value in ("hiring_ai_engineer", "hiring_ml_engineer", "hiring_chief_ai_officer")
           for s in signals):
        return TEMPLATES[0]  # hiring_signal_ai_engineer
    
    # If they have a strong tech stack, use the integration template
    if len(lead.company.tech_stack) >= 4:
        return TEMPLATES[2]  # tech_stack_integration
    
    # If they have many open roles, use scaling template
    if len(signals) >= 3:
        return TEMPLATES[3]  # scaling_signal
    
    # If industry is a strong fit, use industry-specific
    if industry in ["finance", "healthcare", "logistics", "legal", "insurance"]:
        return TEMPLATES[1]  # industry_specific_roi
    
    # Default to warm intro style
    return TEMPLATES[4]  # warm_intro_style


def generate_roi_opportunities(lead: Lead) -> str:
    """Generate industry-specific ROI opportunities."""
    industry = (lead.company.industry or "").lower()
    
    opportunities = {
        "finance": """  • Automated KYC/AML document processing (saves 40+ hours/week per analyst)
  • AI-powered compliance report generation
  • Intelligent customer onboarding workflows
  • Fraud detection alert triage automation""",
        "healthcare": """  • Patient intake and records processing automation
  • Prior authorization workflow agents
  • Clinical documentation assistance
  • Appointment scheduling optimization""",
        "logistics": """  • Shipment tracking and exception handling agents
  • Automated carrier communication
  • Route optimization with real-time adjustments
  • Customs documentation processing""",
        "insurance": """  • Claims processing automation (first notice of loss)
  • Policy document analysis and extraction
  • Underwriting support agents
  • Regulatory compliance monitoring""",
        "legal": """  • Contract review and clause extraction
  • Legal research agents
  • Discovery document processing
  • Deadline and compliance tracking""",
        "saas": """  • Customer onboarding automation
  • Support ticket triage and resolution
  • Churn prediction and intervention workflows
  • Feature request analysis and routing""",
    }
    
    return opportunities.get(industry, """  • Document processing automation
  • Customer service workflow agents
  • Data entry and validation automation
  • Internal knowledge search and retrieval""")


def generate_outreach(lead: Lead, sender_name: str = "Your Name",
                      sender_title: str = "AI Automation Consultant") -> tuple[str, str]:
    """Generate a personalized outreach message for a lead."""
    template = select_template(lead)
    
    # Build personalization context
    contact_first_name = "there"
    if lead.contact_person:
        contact_first_name = lead.contact_person.split()[0]
    
    primary_tech = lead.company.tech_stack[0] if lead.company.tech_stack else "tech"
    
    # Get the most relevant job title from hiring signals
    job_title = "AI/ML Engineer"
    if lead.hiring_signals:
        job_title = lead.hiring_signals[0].job_title
    
    # Build specific observation
    observations = [
        f"your focus on {lead.company.industry or 'innovation'}",
        f"the team you're building",
        f"your growth trajectory",
    ]
    specific_observation = observations[0]
    
    context = {
        "contact_first_name": contact_first_name,
        "company_name": lead.company.name,
        "job_title": job_title,
        "industry": lead.company.industry or "your industry",
        "company_size": lead.company.company_size or "growing",
        "tech_stack_summary": ", ".join(lead.company.tech_stack[:3]) if lead.company.tech_stack else "modern",
        "roi_opportunities": generate_roi_opportunities(lead),
        "company_summary": generate_company_summary(lead.company),
        "primary_tech": primary_tech,
        "open_roles_count": str(len(lead.hiring_signals)),
        "specific_observation": specific_observation,
        "sender_name": sender_name,
        "sender_title": sender_title,
    }
    
    # Fill template
    message = template.template_text
    subject = template.subject_line
    for key, value in context.items():
        placeholder = "{" + key + "}"
        message = message.replace(placeholder, str(value))
        subject = subject.replace(placeholder, str(value))
    
    return subject, message
