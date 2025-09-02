# Technical Stack

## Core Platform

### Application Framework
- **Home Assistant** (Latest LTS)
- Package-based configuration architecture
- Modular YAML packages for organized automation logic
- 18 specialized packages covering all rooms and systems

### Scripting and Automation
- **Configuration Language:** YAML (packages, helpers, automations, templates)
- **Scripting Language:** Python 3.11+ (via Pyscript integration)
- **Template Engine:** Jinja2 (templating inside YAML sensors/attributes)
- **7 Python Services:** Advanced logic and machine learning algorithms

### Database System
- **Primary:** SQLite (Home Assistant recorder/state history)
- **Alternative:** MariaDB (optional upgrade path)
- **Storage:** Local to Home Assistant instance
- **Backups:** Home Assistant snapshots/automated backups
- **Special Storage:** SQLite for adaptive learning data persistence

## Development and Deployment

### Hosting and Infrastructure
- **Application Hosting:** Local Home Assistant instance (HA OS/Supervised/Core)
- **Database Hosting:** Local (bundled with HA; MariaDB upgrade optional)
- **Asset Storage:** Managed within Home Assistant
- **Hosting Region:** Local/on-premises

### Testing and Validation
- **Configuration Validation:** Home Assistant config check, yamllint
- **Python Validation:** Python compile/lint for Pyscript services
- **Automated Testing:** Parallel test engine for validation and regression detection
- **Manual Verification:** HA logs, Logbook, dashboards, and diagnostics sensors
- **Production Environment:** Live Home Assistant instance
- **Development:** Iterative testing in `/config/packages/` with HA config validation

### Deployment Strategy
- **CI/CD Platform:** Home Assistant config checks & reloads (manual)
- **CI/CD Trigger:** Manual (config reloads / restarts)
- **Deployment Solution:** Home Assistant package reload system
- **Code Repository:** Local file system management

## Domain Integrations & System Capabilities

### Smart Home Hardware Integration
- **Lighting Control:** Home Assistant `light.*` entities with adaptive brightness & color temperature control
- **WLED Integration:** Advanced LED strip control for sink/fridge areas with preset management and dynamic effects
- **Motion Sensors:** Multi-room motion detection for kitchen, living room, hallway, bathroom, closet, and laundry
- **Door/Lock Sensors:** Front door and bathroom contact sensors integrated with Aqara smart lock
- **Mobile Integration:** iPhone device trackers (`device_tracker.iphone15`, `device_tracker.work_iphone`) for presence detection

### External Data Sources
- **Weather Integration:** PirateWeather (`weather.pirateweather`) providing cloud coverage, temperature, and seasonal data
- **Astronomical Data:** Sun elevation tracking for circadian rhythm synchronization
- **Calendar Integration:** Work schedule system with morning ramp coordination

### Core System Architecture
- **Home State Management:** Centralized `input_select.home_state` with Early Morning/Day/Evening/Night/Away states
- **Adaptive Learning System (ALS):** Machine learning-based brightness adaptation with SQLite data persistence
- **Intelligent Lighting System (ILS):** Context-aware lighting coordination with weather, schedule, and presence integration
- **Diagnostics Framework:** Real-time status monitoring with per-room diagnostic sensors and error reporting

### User Interface and Monitoring
- **Enhanced Dashboard:** Custom Home Assistant panels with system status and learning progress display
- **Diagnostic Monitoring:** Per-room ALS status sensors showing ready/blocked/away/error states
- **Debug Controls:** Developer-friendly debug toggles and templates for troubleshooting
- **Material Design Icons:** Consistent iconography throughout the interface (`mdi:*`)

### Specialized Features
- **Circadian Rhythm Support:** Evening temperature ramping and morning brightness gradients
- **Weather-Responsive Automation:** Dynamic lighting adjustments based on cloud coverage and seasonal patterns
- **Work Schedule Integration:** Calendar-aware morning routines with sleep-in detection
- **Multi-Source Presence:** Reliable home/away detection combining device trackers, motion sensors, and contextual logic