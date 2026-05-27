#!/usr/bin/env bash
set -euo pipefail

curl -s http://127.0.0.1:8765/api/dashboard | python -m json.tool

curl -s -X POST http://127.0.0.1:8765/api/jobs \
  -H 'Content-Type: application/json' \
  -d '{"goal":"Draft a sales follow-up email from call notes","agent_id":"sales_agent","inputs":{"prospect_name":"Maya","company_name":"Orion Labs","agreed_next_step":"review the pilot plan on Friday"},"human_edits":"Moved next step to opening lines."}' | python -m json.tool

curl -s -X POST http://127.0.0.1:8765/api/learn \
  -H 'Content-Type: application/json' \
  -d '{"min_support":3}' | python -m json.tool
