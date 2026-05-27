# Quickstart

## Run locally

From the repository root:

```bash
python -m skillos.cli demo
python -m skillos.cli serve
```

Open:

```text
http://127.0.0.1:8765
```

## Useful commands

```bash
python -m skillos.cli init
python -m skillos.cli demo
python -m skillos.cli dashboard
python -m skillos.cli serve
python -m skillos.cli reset
python -m unittest discover -s tests
```

## A single job

```bash
python -m skillos.cli job "Draft a sales follow-up email from call notes" \
  --inputs '{"prospect_name":"Maya","company_name":"Orion Labs","agreed_next_step":"review the pilot plan on Friday"}' \
  --human-edits "Moved the next step to the opening lines."
```

## The local data store

SkillOS writes local data to:

```text
.skillos/skillos.db
```

Delete it with:

```bash
python -m skillos.cli reset
```
