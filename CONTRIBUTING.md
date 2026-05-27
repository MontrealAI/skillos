# Contributing

Thank you for improving Agent SkillOS.

## Local setup

```bash
python -m skillos.cli demo
python -m unittest discover -s tests
```

## Development principles

1. Keep the core loop easy to understand.
2. Prefer small, inspectable skill artifacts over opaque behavior.
3. Every new skill update path needs tests.
4. Every release path needs rollback.
5. Do not mix private knowledge with shared skill.

## Pull request checklist

- [ ] Tests pass.
- [ ] New behavior is documented.
- [ ] New skill behavior is versioned.
- [ ] Permission changes are explicit.
- [ ] No local `.skillos` data is committed.
