from __future__ import annotations

from .storage import SkillOSStorage


SALES_SKILL_V1 = """
# Sales Follow-Up Email

## Purpose
Write concise follow-up emails from sales call notes.

## Instructions
- Thank the prospect for the call.
- Mention the company and main pain point.
- Provide a short recap.
- Include the next step before closing.
- Keep the email under 180 words.

## Permissions
Allowed tools:
- crm.read_contact
- email.create_draft

Blocked tools:
- email.send_without_approval
""".strip()

INVOICE_SKILL_V1 = """
# Invoice Reconciliation

## Purpose
Compare invoices against purchase records and flag mismatches.

## Instructions
- Normalize vendor names before matching.
- Match invoice id, amount, date, and purchase order.
- Draft an approval note when the match is strong.
- Never initiate payment without human approval.

## Permissions
Allowed tools:
- accounting.read_invoice

Blocked tools:
- payments.initiate
""".strip()

RESEARCH_SKILL_V1 = """
# Research Summary

## Purpose
Create concise research briefs with claims, evidence needs, and next steps.

## Instructions
- Start with the core claim.
- Separate facts from assumptions.
- Highlight missing evidence.
- Recommend the next validation step.

## Permissions
Allowed tools:
- search.read

Blocked tools:
- external.publish
""".strip()


def seed_demo(storage: SkillOSStorage) -> None:
    storage.init()
    storage.upsert_agent(
        "sales_agent",
        "Sales Agent",
        "Drafts follow-ups, extracts next steps, and updates CRM drafts.",
        permissions=["crm.read_contact", "email.create_draft"],
        installed_skills=["sales_followup_email"],
    )
    storage.upsert_agent(
        "finance_agent",
        "Finance Agent",
        "Reviews invoices and drafts reconciliation notes.",
        permissions=["accounting.read_invoice"],
        installed_skills=["invoice_reconciliation"],
    )
    storage.upsert_agent(
        "research_agent",
        "Research Agent",
        "Creates concise research briefs and validation plans.",
        permissions=["search.read"],
        installed_skills=["research_summary"],
    )

    if not storage.get_skill("sales_followup_email"):
        storage.create_skill("sales_followup_email", "Sales Follow-Up Email", "Writes follow-up emails from call notes.")
        storage.add_skill_version(
            "sales_followup_email",
            SALES_SKILL_V1,
            status="approved",
            quality_score=0.74,
            allowed_tools=["crm.read_contact", "email.create_draft"],
            blocked_tools=["email.send_without_approval"],
            tests=[{"name": "includes_next_step"}, {"name": "under_180_words"}],
            set_current=True,
        )

    if not storage.get_skill("invoice_reconciliation"):
        storage.create_skill("invoice_reconciliation", "Invoice Reconciliation", "Matches invoices against purchase records.")
        storage.add_skill_version(
            "invoice_reconciliation",
            INVOICE_SKILL_V1,
            status="approved",
            quality_score=0.86,
            allowed_tools=["accounting.read_invoice"],
            blocked_tools=["payments.initiate"],
            tests=[{"name": "no_payment_without_approval"}],
            set_current=True,
        )

    if not storage.get_skill("research_summary"):
        storage.create_skill("research_summary", "Research Summary", "Creates concise research briefs.")
        storage.add_skill_version(
            "research_summary",
            RESEARCH_SKILL_V1,
            status="approved",
            quality_score=0.84,
            allowed_tools=["search.read"],
            blocked_tools=["external.publish"],
            tests=[{"name": "separates_fact_from_assumption"}],
            set_current=True,
        )
