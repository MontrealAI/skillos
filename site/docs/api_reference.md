# API Reference

Run the server:

```bash
python -m skillos.cli serve
```

Base URL:

```text
http://127.0.0.1:8765
```

## Health

```http
GET /api/health
```

## Dashboard

```http
GET /api/dashboard
```

## Skills

```http
GET /api/skills
```

## Lessons

```http
GET /api/lessons
```

## Run job

```http
POST /api/jobs
```

```json
{
  "goal": "Draft a sales follow-up email from call notes",
  "agent_id": "sales_agent",
  "inputs": {
    "prospect_name": "Maya",
    "company_name": "Orion Labs",
    "agreed_next_step": "review the pilot plan on Friday"
  },
  "human_edits": "Moved the next step to the opening lines."
}
```

## Discover lessons

```http
POST /api/learn
```

```json
{
  "min_support": 3
}
```

## Train candidate skill

```http
POST /api/train
```

```json
{
  "lesson_id": "lesson_abc123"
}
```

## Approve release

```http
POST /api/approve
```

```json
{
  "skill_id": "sales_followup_email",
  "version": 2,
  "scope": "team",
  "rollout": "10_percent_canary"
}
```
