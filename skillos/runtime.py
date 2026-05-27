from __future__ import annotations

import re
from typing import Any

from .storage import SkillOSStorage


class AgentRuntime:
    def __init__(self, storage: SkillOSStorage):
        self.storage = storage

    def choose_skill(self, goal: str) -> str:
        text = goal.lower()
        if any(word in text for word in ["invoice", "reconcile", "payment"]):
            return "invoice_reconciliation"
        if any(word in text for word in ["research", "memo", "brief", "source"]):
            return "research_summary"
        return "sales_followup_email"

    def run_job(self, goal: str, inputs: dict[str, Any] | None = None, agent_id: str = "sales_agent", human_edits: str = "") -> dict[str, Any]:
        inputs = inputs or {}
        skill_id = self.choose_skill(goal)
        skill = self.storage.get_skill_version(skill_id)
        if not skill:
            raise RuntimeError(f"Skill not found or has no current version: {skill_id}")
        output, score, tools = self._render_output(skill_id, skill["markdown"], inputs)
        job_id = self.storage.create_job(agent_id=agent_id, goal=goal, inputs=inputs, status="completed")
        trace_id = self.storage.create_trace(
            job_id=job_id,
            agent_id=agent_id,
            goal=goal,
            skills_used=[f"{skill_id}:v{skill['version']}"],
            tools_used=tools,
            inputs=inputs,
            output=output,
            human_edits=human_edits,
            score=score,
            failure_tags=[] if score >= 0.8 else ["needs_skill_improvement"],
        )
        return {
            "job_id": job_id,
            "trace_id": trace_id,
            "agent_id": agent_id,
            "skill_id": skill_id,
            "skill_version": skill["version"],
            "output": output,
            "score": score,
            "human_edits": human_edits,
        }

    def _render_output(self, skill_id: str, markdown: str, inputs: dict[str, Any]) -> tuple[str, float, list[str]]:
        if skill_id == "sales_followup_email":
            return self._sales_followup(markdown, inputs)
        if skill_id == "invoice_reconciliation":
            return self._invoice_reconciliation(markdown, inputs)
        if skill_id == "research_summary":
            return self._research_summary(markdown, inputs)
        return "I completed the requested task.", 0.65, []

    def _sales_followup(self, markdown: str, inputs: dict[str, Any]) -> tuple[str, float, list[str]]:
        prospect = inputs.get("prospect_name", "Alex")
        company = inputs.get("company_name", "Acme Corp")
        pain = inputs.get("pain_point", "scaling operations without adding manual overhead")
        next_step = inputs.get("agreed_next_step") or self._extract_next_step(inputs.get("call_notes", "")) or "schedule a 20-minute implementation review"
        first_three = "first three lines" in markdown.lower() or "opening section" in markdown.lower()
        if first_three:
            output = f"Hi {prospect},\n\nNext step: {next_step}.\n\nThanks for the conversation about {company}'s work on {pain}. I attached a concise recap and the proposed path forward.\n\nBest,\nAgent SkillOS"
            score = 0.91
        else:
            output = f"Hi {prospect},\n\nThanks for the conversation about {company}'s work on {pain}. I attached a concise recap and the proposed path forward.\n\nFor next steps, we can {next_step}.\n\nBest,\nAgent SkillOS"
            score = 0.73
        return output, score, ["crm.read_contact", "email.create_draft"]

    def _invoice_reconciliation(self, markdown: str, inputs: dict[str, Any]) -> tuple[str, float, list[str]]:
        vendor = inputs.get("vendor", "Northstar Supplies")
        invoice = inputs.get("invoice_id", "INV-1042")
        amount = inputs.get("amount", "$4,200")
        output = f"Invoice reconciliation result\n\nVendor: {vendor}\nInvoice: {invoice}\nAmount: {amount}\nStatus: matched after vendor-name normalization\nRecommended action: draft approval note; do not initiate payment without approval."
        return output, 0.86, ["accounting.read_invoice"]

    def _research_summary(self, markdown: str, inputs: dict[str, Any]) -> tuple[str, float, list[str]]:
        topic = inputs.get("topic", "agent skill systems")
        output = f"Research brief: {topic}\n\n1. Main claim: reusable skills turn repeated work into compound capability.\n2. Evidence needed: benchmark results, user edit reduction, release safety.\n3. Recommended next step: validate with a narrow workflow and held-out tests."
        return output, 0.84, ["search.read"]

    def _extract_next_step(self, notes: str) -> str | None:
        if not notes:
            return None
        match = re.search(r"next step[s]?:?\s*([^\.\n]+)", notes, re.I)
        return match.group(1).strip() if match else None
