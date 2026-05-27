# Extending Agent SkillOS

## Add a new skill

1. Create a skill folder:

```text
skills/my_skill/v1/skill.md
```

2. Add seed logic in `skillos/seed.py`.
3. Add routing logic in `skillos/runtime.py`.
4. Add eval cases in `skillos/evals.py`.
5. Add tests.

## Add a new learning pattern

1. Add a detector method in `skillos/learning.py`.
2. Create lessons only when there is enough support.
3. Avoid duplicates.
4. Add an end-to-end test.

## Plug in a real LLM

Replace the deterministic render methods in `skillos/runtime.py` with an LLM provider that receives:

```text
Goal
Inputs
Relevant skill markdown
Allowed tools
Blocked tools
Retrieved context
```

The output should still create a trace.

## Plug in SkillOpt

The local `SkillTrainer` performs a bounded text edit. In production, replace it with a SkillOpt-style optimizer service:

```text
scored traces → rollout analysis → bounded skill edit → validation gate → candidate skill artifact
```

Keep SkillOS responsible for approval, release, permissions, and rollback.
