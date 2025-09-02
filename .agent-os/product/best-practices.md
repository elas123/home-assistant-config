**Output policy:** Always return complete, bounded sections (no partial snippets or diffs).

# Development Best Practices

## Context

Global development guidelines for this Home Assistant project.

---

## File Headers
- Every YAML package and Pyscript file must begin with a standardized header block
- Header must always include:
  - Version (sequential: v1.1 → v1.2 → v1.3…)
  - Author (ChatGPT, Claude, Gemini, etc.)
  - Updated (YYYY-MM-DD HH:MM format, local time)
  - Status (✅ Finalized, 🚧 In Progress, 🐞 Bugfix, etc.)
- Header must be wrapped in a full-width hash box:
  ################################################################################

---

## YAML Standards
- Always use 2-space indentation, no tabs
- All files must pass `yamllint` before commit
- Keys must follow the new schema (2024.10+ / 2025.8):
  - triggers: not trigger:
  - conditions: not condition:
  - actions: not action:
- Use `target:` blocks instead of raw `entity_id:` where possible
- Automations must explicitly set `mode:` (single, restart, or parallel)
- Each automation must include `id:`, `alias:`, and `description:`

---

## Section Boundaries (YAML)
- All YAML sections must begin and end with a green comment header
- Format:  
  - `# --- SECTION NAME (brief description) ---`
- Required sections:
  - HELPERS (input_booleans, input_numbers, input_texts, input_selects)
  - TEMPLATES (sensors, binary_sensors, attributes)
  - AUTOMATIONS (all automation logic)
  - SCRIPTS (manual overrides, sequences)
- Section markers must always appear in consistent order

---

## Automations
- Must use new `actions:` schema (no `service:` shorthand)
- Prefer `choose:` blocks instead of nested conditions
- Always include a `description:` field
- Long-running states (e.g., night/hold modes) must include failsafes
- Automations should reference reusable sensors instead of duplicating logic

---

## Scripts
- Must use the `script:` section with clear `alias:` values
- Sequence blocks must use `choose:` where multiple paths exist
- Scripts should be limited to a single clear purpose
- Debug logs should be included for complex actions

---

## Templates
- Allowed only for simple, safe expressions:
  - Use `states('entity')` and `is_state()` (never `states.entity.state`)
  - Always provide defaults (`| int(0)`, `| float(0)`)
  - Guard against `'unknown'` / `'unavailable'`
- Complex or multi-branch templates must be written as Pyscript functions
- After generation, templates must be parsed with a Jinja2 linter outside the AI context window
- Complex templates must be tested in Developer Tools → Template before commit

---

## Pyscript Standards
- Section headers must use exclamation style for easy recognition:
  - `# !!! PYSCRIPT SECTION (brief description) !!!`
- Functions:
  - One clear function per behavior
  - Descriptive, namespaced names (e.g., `als_compute_brightness`)
  - No duplicate `@service` registrations
- Robustness:
  - Validate all inputs and handle missing/unknown states
  - Log via `log.info()` or `persistent_notification.create`, gated by debug flags
- External checks (must run outside AI context):
  - `python -m py_compile` for syntax validation
  - `ruff` or `flake8` for linting and undefined variable detection
  - Errors must be returned into context for correction

---

## Validation and Testing
- YAML:
  - All files must pass `yamllint` and `ha core check`
  - Checks must run outside the AI context window
  - Failures return only error messages to context for repair
- Pyscript:
  - All `.py` files must pass `py_compile` and `ruff`/`flake8`
  - Checks must run outside the AI context window
  - Failures return only error messages to context for repair
- Templates:
  - Must be parsed with a Jinja2 linter outside context
  - Failures return only error messages to context for repair

---

## Debugging and Logging
- Use `logbook.log` or `persistent_notification.create` for diagnostics
- Debug logs must be gated by `input_boolean.home_state_debug`
- Each adaptive/intelligent system must expose a diagnostic status sensor

---

## Entity References
- Prefer `target:` blocks over raw `entity_id:` where possible
- Group lights into `light.group` entities when practical
- Do not hardcode entity names where helpers or groups exist

---

## Versioning
- All packages and scripts must include metadata in their headers
- Version numbers must increment sequentially
- Deprecated schema (pre-2024.10) must not be used