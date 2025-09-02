# Tech Stack

## Context

Global tech stack defaults for Agent OS projects, overridable in project-specific `.agent-os/product/tech-stack.md`.

- Automation Framework: Home Assistant (package-based configuration)
- Configuration Language: YAML (packages, helpers, automations, templates)
- Scripting Language: Python (via Pyscript integration in Home Assistant)
- Template Engine: Jinja2 (templating inside YAML sensors/attributes)
- Primary Database: SQLite (Home Assistant recorder/state history; local to HA instance; MariaDB optional)
- ORM: N/A (state is stored/retrieved via Home Assistant entities)
- JavaScript Framework: N/A (not used in this project)
- Build Tool: N/A
- Import Strategy: N/A
- Package Manager: N/A
- Node Version: N/A
- CSS Framework: N/A
- UI Components: N/A
- Icons: Material Design Icons (mdi) via Home Assistant
- Application Hosting: Local Home Assistant instance (HA OS/Supervised/Core)
- Hosting Region: N/A (local)
- Database Hosting: Local (bundled with HA; can be swapped to MariaDB later if desired)
- Database Backups: Home Assistant snapshots/backups
- Asset Storage: Managed within Home Assistant
- CDN: N/A
- Asset Access: Local (no signed URLs)
- CI/CD Platform: Home Assistant config checks & reloads (manual); restart for core changes
- CI/CD Trigger: Manual (config reloads / restarts)
- Tests: HA configuration check, yamllint, and manual verification via HA logs, Logbook, dashboards, and diagnostics sensors
- Production Environment: Live Home Assistant instance
- Staging Environment: N/A (iterate in `/config/packages/` with HA config validation)

### Domain Integrations & System Capabilities (project-specific)

- Presence Tracking: iPhone device trackers (`device_tracker.iphone15`, `device_tracker.work_iphone`)
- Weather Data: PirateWeather (`weather.pirateweather`) for adaptive lighting (e.g., `cloud_coverage`)
- Lighting Control: Home Assistant `light.*` entities with adaptive brightness & color temperature; smooth transitions
- WLED Integration: Preset control for sink/fridge strips (e.g., “night-100”) via `select.*_wled_preset`
- Home State System: Centralized `input_select.home_state` with Early Morning / Day / Evening / Night / Away and calculated transitions
- Adaptive Learning (ALS): Per-room learned brightness using `input_text.*` memory; confirmation thresholds; sun-elevation buckets; season/weather context
- Intelligent Lighting (ILS): Intelligent brightness/temperature sensors & automations layered with ALS and fallbacks (evening ramps, weather transitions)
- Diagnostics & Status: Per-room ALS Status sensors and messages; ready/blocked/away/error states for debugging and UX clarity