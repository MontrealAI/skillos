# Governance

SkillOS is designed to make self-improvement safe and controllable.

## Rules

1. Agents may propose improvements.
2. Agents may not silently release global changes.
3. Every skill update must be versioned.
4. Every skill update must be tested.
5. High-impact actions require approval.
6. Private knowledge must not become shared skill.
7. Every release must be reversible.

## Sharing levels

```text
Private  → one user or agent
Team     → one team
Company  → one organization
Network  → authorized cross-organization network
```

## Permissions

A skill has explicit allowed and blocked tools.

Example:

```text
Allowed:
- crm.read_contact
- email.create_draft

Blocked:
- email.send_without_approval
- payments.initiate
- records.delete
```

## Why this matters

Self-improvement without governance becomes drift. SkillOS makes improvement measurable, reversible, and accountable.
