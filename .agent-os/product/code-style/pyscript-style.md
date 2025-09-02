# Pyscript Style Guide

## Purpose
Conventions for Python scripts under `pyscript/` that implement non-trivial logic, provide services, and reduce Jinja2 fragility.

## Module & Function Naming
- Modules: `area_or_system_purpose.py` (e.g., `als_memory_manager.py`).
- Functions: snake_case verbs with scope (e.g., `als_apply_target`, `ils_compute_room_level`).
- One behavior per function; keep functions focused and testable.

## Services & Interfaces
- Expose callable entry points via `@service` with self-describing names.
- Accept explicit parameters; do not hardcode entity IDs when a parameter can be passed or derived from a small config map.
- Return/emit clear success or failure states; log outcomes.

## State Access & Safety
- Read states defensively; provide defaults when absent.
- Validate inputs (types, ranges) and short-circuit when invalid.
- Never block indefinitely; use `task.sleep()` and cancellation-aware patterns for timers/loops.

## Logging & Diagnostics
- Log at appropriate levels: `info` for normal operations, `warning` for recoverable anomalies, `error` for failures.
- Include context: room/entity, thresholds, computed values.
- Surface important status via project diagnostics (ALS/ILS status sensors) where applicable.

## Error Handling
- Catch predictable exceptions and either retry safely or return a fallback.
- On failure, avoid partial state application; prefer “do nothing” over “apply wrong level”.

## Dependencies & Imports
- Keep imports minimal; prefer stdlib. If a third-party is needed, document it in the spec and tech stack.
- No long-lived global mutable state; use narrow-scope variables or HA helpers for persistence when truly needed.

## Testing & Validation (out-of-context)
- Syntax check: `python -m py_compile` on all `.py`.
- Static linting: Ruff/Flake8 with agreed rules.
- Logic sanity: dry-run functions with safe parameters (where possible) before wiring into YAML actions.

## Output & Sectioning
- Begin each file with a header and a prominent Pyscript banner line (e.g., `# !!! PYSCRIPT FUNCTIONS (ALS/ILS) !!!`).
- When asked to modify a function or group, output the **entire function or section** rather than a snippet.

