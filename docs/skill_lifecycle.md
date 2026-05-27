# Skill Lifecycle

Every skill follows a controlled lifecycle.

```text
Draft → Candidate → Tested → Approved → Canary → Released → Monitored → Improved
```

## 1. Draft

A user or system creates an initial skill.

## 2. Candidate

The Learning Engine discovers a lesson and the Skill Trainer proposes an update.

## 3. Tested

The Test Lab compares the candidate against the current version.

## 4. Approved

A user, owner, or policy approves the update.

## 5. Canary

The skill is released to a small scope.

## 6. Released

The skill becomes the default version for the approved scope.

## 7. Monitored

Runtime traces continue measuring whether the new skill performs better.

## 8. Improved

New traces create new lessons, and the loop repeats.

## Rollback

Every release stores a rollback version.

```text
Released v5 → regression detected → rollback to v4 → investigate → propose v6
```
