# Jinja2 Template Style Guide

## Purpose
Rules for Jinja2 usage inside Home Assistant YAML to keep templates robust and maintainable.

## General Philosophy
- Prefer Pyscript for complex logic; keep templates short and composable.
- Templates must be resilient to missing or unavailable data.

## Reading State
- Use `states('domain.entity')` and `is_state('domain.entity', 'value')`.
- Always provide defaults (`| int(0)`, `| float(0)`, `| default('')`) before arithmetic or comparisons.
- Guard for `'unknown'` and `'unavailable'`. Do not chain filters on raw `.state`.

## Comparisons & Math
- Cast before comparing numeric thresholds.
- Avoid deeply nested ternaries; split logic or move to Pyscript.

## Structure & Clarity
- Keep expressions single-purpose. If it grows beyond a couple of operations, refactor.
- Document *why* the template exists with a short comment above it.

## Testing
- Test new or changed templates in HA Developer Tools → Template before commit.
- For scheduled jobs or sunrise/sunset logic, verify edge cases (pre-dawn, overcast days, DST changes).

## Output Discipline
- When returning values used by actions, ensure safe bounds (e.g., brightness 1–100).
- Never return non-numeric values where numbers are expected; provide sane defaults.

