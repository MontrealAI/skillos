# Invoice Reconciliation

## Purpose
Compare invoices against purchase records and flag mismatches.

## Instructions
- Normalize vendor names before matching.
- Match invoice id, amount, date, and purchase order.
- Draft an approval note when the match is strong.
- Never initiate payment without human approval.

## Allowed Tools
- accounting.read_invoice

## Blocked Tools
- payments.initiate
