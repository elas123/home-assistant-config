# Code Style Overview (Home Assistant + Pyscript)

This project uses a split style guide:

- **YAML Style** — `.agent-os/product/code-style/yaml-style.md`
- **Pyscript Style** — `.agent-os/product/code-style/pyscript-style.md`
- **Jinja2 Template Style** — `.agent-os/product/code-style/jinja2-style.md`

## Global Requirements

- **Schema**: Use Home Assistant 2025.8+ schema. Prefer `triggers / conditions / actions`. Avoid legacy `service:` blocks and legacy trigger `platform:` syntax.
- **Sectioning**: Output complete sections only. Clearly mark sections with single-line headers, e.g.  
  - YAML sections: `# --- HELPERS ---`, `# --- TEMPLATES ---`, `# --- AUTOMATIONS ---`, `# --- SCRIPTS ---`  
  - End markers when long: `# --- END AUTOMATIONS ---`  
  - Pyscript header lines use `# !!! ... !!!`
- **File Header** (every file): Title, Version (sequential), Author (ChatGPT/Gemini/Claude/Frank), Updated (YYYY-MM-DD HH:MM), Status.
- **Validation pipeline (out of context)**: After generating code, run:
  - YAML: yamllint → `ha core check`
  - Pyscript: `python -m py_compile` and linter
  - Complex templates: dry-render via template testing before inclusion
- **Replacement rule**: When asked to modify a section, output the **entire section** (not a snippet) bounded by the section markers.

See the detailed rules in the three sub-guides.
