# YAML Style Guide

## Purpose
Standards for all Home Assistant package YAML under `packages/`.

## Formatting & Structure
- Indentation is 2 spaces; never use tabs.
- Keys are lowercase with underscores.
- Keep lists compact and readable; wrap long strings using folded style when needed.
- Each file begins with the required header (Title, Version, Author, Updated, Status).
- Use clear single-line section markers:
  - `# --- HELPERS ---`
  - `# --- TEMPLATES ---`
  - `# --- AUTOMATIONS ---`
  - `# --- SCRIPTS ---`
  - Add `# --- END <SECTION> ---` when a section is long.

## Schema (2025.8+)
- Prefer `triggers / conditions / actions` blocks.
- Avoid legacy `platform:` triggers and old `service:` usage. Inside actions, use `- action: domain.service`.
- Prefer `target:` for entity selection instead of raw `entity_id:` when possible.
- Each automation **must** define: `id`, `alias`, `description`, and `mode` (default `restart` unless parallelism is required).
- Use `choose:` for branching instead of deeply nested conditions.

## Entities & Naming
- Entity IDs: `domain.area_device_detail` where practical; all lowercase with `_`.
- Automation IDs: `room_purpose_detail` (e.g., `kitchen_motion_on`).
- Keep entity references consistent; do not mix groups when the spec requires individual entities.

## Template Usage in YAML
- Keep templates shallow; push complex logic to Pyscript.
- For state reads, always use helpers with defaults:
  - `states('sensor.foo') | int(0)` or `| float(0)`
  - Guard against `'unknown'` / `'unavailable'` before arithmetic or comparisons.
- Prefer small, composable template sensors over sprawling inline expressions.

## Safety & Reliability
- Add explicit fallbacks in automations (e.g., default brightness/temp) when upstream data is unavailable.
- Include guard conditions for `Away` and night modes where appropriate.
- Time-sensitive logic should reference sun elevation or time helpers already defined by the project.

## Validation
- Lint with yamllint and run `ha core check` before accepting changes.
- Agents must output **full sections** bounded by markers so maintainers can copy/replace without hunting.

