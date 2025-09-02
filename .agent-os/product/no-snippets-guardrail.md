# No-Snippets Output Policy

This project forbids partial code edits. Agents must always return complete, copy-pasteable sections.

## What “complete section” means
- **YAML packages:** Output the entire section bounded by our markers:
  - Start markers: `# --- HELPERS ---`, `# --- TEMPLATES ---`, `# --- AUTOMATIONS ---`, `# --- SCRIPTS ---`
  - Optional end markers for long blocks: `# --- END <SECTION> ---`
  - Example request: “replace AUTOMATIONS in kitchen package” → return the **entire** `automation:` block between `# --- AUTOMATIONS ---` and `# --- END AUTOMATIONS ---`, not just changed lines.
- **Pyscript files:** Use blue header markers, e.g. `# !!! PYSCRIPT FUNCTIONS (ALS/ILS) !!!`. When editing, return full functions or full logical groups—not excerpts.

## Replacement rules
- Never output inline diffs, patch formats, or “…” elisions.
- Do not return isolated lines or fragments; always return whole sections so a maintainer can replace in one paste.
- If multiple files are touched, clearly separate outputs and **start each with** a line:  
  `FILE: <relative/path/from/project/root>`
  followed by the full section(s) for that file.

## Headers
- Every file you generate must include the standard header at the top: Title, Version (sequential), Author (ChatGPT/Gemini/Claude/Frank), Updated (YYYY-MM-DD HH:MM), Status.

## Validation loop
- After producing code, run the project’s Validation Workflow (yamllint → HA config check → Python syntax/lint → template dry-run) **outside** the model context.
- If any step fails, return the **entire corrected section again**, bounded by markers.

## Token limits
- Do not truncate output due to length. If necessary, split across messages by section, but each message must still contain complete, bounded sections.

