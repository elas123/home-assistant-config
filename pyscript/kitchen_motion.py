################################################################################
# KITCHEN MOTION LIGHTING SYSTEM v1.1
# Author: Claude
# Updated: 2025-09-02 15:10
# Status: ✅ Runtime Error Fixed
# Purpose: Kitchen motion detection with WLED strips and main light control
################################################################################

# Kitchen motion → WLED + Main lights (per-mode brightness), debounced clear
# Entities confirmed by you (sink & fridge have preset selects)
# FIXED: Main lights blocked in Night mode
# FIXED: Undefined MAIN_BRIGHTNESS variable

from datetime import datetime, time as dt_time
import time
import asyncio

# ===== Entities =====
SINK_PRESET   = "select.sink_wled_preset"
FRIDGE_PRESET = "select.frig_strip_preset"
SINK_LIGHT    = "light.sink_wled"          # used to turn sink strip off on clear
FRIDGE_LIGHT  = "light.frig_strip"         # not strictly needed with presets but kept for safety

KITCHEN_MAIN  = "light.kitchen_main_lights"  # <-- now actively controlled

MOTION_1      = "binary_sensor.aqara_motion_sensor_p1_occupancy"
MOTION_2      = "binary_sensor.kitchen_iris_frig_occupancy"
HOME_STATE    = "input_select.home_state"
ALLOWED_MODES = {"Day", "Evening", "Night", "Early Morning"}  # mains are NOT blocked in Evening

# ===== Behavior knobs =====
CLEAR_DEBOUNCE_SEC = 5
TEST_BYPASS_MODE   = False       # set True to ignore mode gating while testing

# Kitchen target brightness entity (uses learned values + fallbacks)
KITCHEN_TARGET_BRIGHTNESS = "sensor.kitchen_target_brightness"
# Turn mains off when motion clears?
TURN_MAIN_OFF_ON_CLEAR = True

# Kitchen main light brightness fallbacks by mode
MAIN_BRIGHTNESS = {
    "Early Morning": 30,
    "Day": 80,
    "Evening": 60,
    "Night": 20,
}
# ===========================

# --- helpers ---
def _state(eid, d=None):
    try:
        v = state.get(eid)
        return v if v not in (None, "unknown", "unavailable") else d
    except Exception:
        return d

def _info(msg):  log.info(f"[KitchenALS] {msg}")
def _warn(msg):  log.warning(f"[KitchenALS] {msg}")
def _error(msg): log.error(f"[KitchenALS] {msg}")

def _set_preset(entity_id: str, option: str):
    try:
        service.call("select", "select_option", entity_id=entity_id, option=option)
        _info(f"Preset -> {entity_id} = {option}")
    except Exception as e:
        _error(f"Preset error on {entity_id}: {e}")

def _light_on(entity_id: str, **kwargs):
    try:
        service.call("light", "turn_on", entity_id=entity_id, **kwargs)
        _info(f"Light ON  -> {entity_id} {kwargs if kwargs else ''}")
    except Exception as e:
        _error(f"Light on error on {entity_id}: {e}")

def _light_off(entity_id: str):
    try:
        service.call("light", "turn_off", entity_id=entity_id)
        _info(f"Light OFF -> {entity_id}")
    except Exception as e:
        _error(f"Light off error on {entity_id}: {e}")

def _any_motion_active() -> bool:
    return (_state(MOTION_1) == "on") or (_state(MOTION_2) == "on")

# --- core behavior ---
def _apply_for_motion(active: bool, reason: str):
    hs = _state(HOME_STATE, "unknown")
    if not TEST_BYPASS_MODE and hs not in ALLOWED_MODES:
        _info(f"SKIP (mode={hs}) reason={reason}")
        return

    _info(f"APPLY motion_active={active} mode={hs} reason={reason}")

    if active:
        # WLEDs on preset night-100 (but NOT in Day mode)
        if hs != "Day":
            _set_preset(SINK_PRESET, "night-100")
            _set_preset(FRIDGE_PRESET, "night-100")
        else:
            _info(f"SKIPPING WLEDs - Day mode (no WLEDs during daylight)")

        # Main lights ON - blocked in Night mode EXCEPT after 4:45 AM
        night_block_lifted = False
        if hs == "Night":
            now_time = datetime.now().time()
            morning_threshold = dt_time(4, 45, 0)  # 4:45 AM
            night_block_lifted = now_time >= morning_threshold
        
        if hs != "Night" or night_block_lifted:
            # Use learned brightness + fallbacks (same priority as rest of system)
            target_brightness = _state(KITCHEN_TARGET_BRIGHTNESS, 30)
            br = max(1, min(100, int(target_brightness)))  # Clamp to valid range
            _light_on(KITCHEN_MAIN, brightness_pct=br)
            if night_block_lifted:
                _info(f"Night mode block LIFTED (after 4:45 AM) - main lights ON at {br}% (learned/fallback)")
            else:
                _info(f"Main lights ON at {br}% (learned/fallback)")
        else:
            _info(f"SKIPPING main lights - Night mode before 4:45 AM (WLED only)")

    else:
        # WLED behavior: sink OFF, fridge to night (but NOT in Day mode)
        if hs != "Day":
            _light_off(SINK_LIGHT)
            _set_preset(FRIDGE_PRESET, "night")

        # Main lights OFF if configured AND they were turned on (respect Night mode + time)
        night_block_active = False
        if hs == "Night":
            now_time = datetime.now().time()
            morning_threshold = dt_time(4, 45, 0)  # 4:45 AM
            night_block_active = now_time < morning_threshold
            
        if TURN_MAIN_OFF_ON_CLEAR and not night_block_active:
            _light_off(KITCHEN_MAIN)

# --- listeners (no YAML automation needed) ---
@state_trigger(MOTION_1)
@state_trigger(MOTION_2)
async def kitchen_motion_listener(**kwargs):
    eid = kwargs.get("var_name")
    new = _state(eid)
    _info(f"Listener: {eid} -> {new} @ {datetime.now().strftime('%H:%M:%S')}")

    if _any_motion_active():
        _apply_for_motion(True, reason=f"{eid} active")
    else:
        await asyncio.sleep(CLEAR_DEBOUNCE_SEC)
        if _any_motion_active():
            _info("Clear aborted (motion returned during debounce)")
            return
        _apply_for_motion(False, reason="debounced clear")

# --- manual tests ---
@service("pyscript.kitchen_wled_smoke_test")
def kitchen_wled_smoke_test():
    """Sets both strips to 'night-100', mains on (Evening level), then sink OFF + fridge 'night'."""
    _info("SMOKE: WLEDs -> night-100; mains on; then sink OFF, fridge -> night")
    _set_preset(SINK_PRESET, "night-100")
    _set_preset(FRIDGE_PRESET, "night-100")
    _light_on(KITCHEN_MAIN, brightness_pct=MAIN_BRIGHTNESS.get("Evening", 60))
    time.sleep(2)
    _light_off(SINK_LIGHT)
    _set_preset(FRIDGE_PRESET, "night")
    if TURN_MAIN_OFF_ON_CLEAR:
        _light_off(KITCHEN_MAIN)

@service("pyscript.kitchen_wled_force")
def kitchen_wled_force(mode: str = "active"):
    """Force 'active' or 'clear' immediately (ignores mode gating)."""
    if mode not in ("active", "clear"):
        _warn(f"force: unknown mode '{mode}'")
        return
    _apply_for_motion(mode == "active", reason=f"forced {mode}")

@service("pyscript.kitchen_debug_status")
def kitchen_debug_status():
    """Debug current state of all kitchen components"""
    _info("=== KITCHEN DEBUG STATUS ===")
    _info(f"Home State: {_state(HOME_STATE)}")
    _info(f"Motion 1: {_state(MOTION_1)}")
    _info(f"Motion 2: {_state(MOTION_2)}")
    _info(f"Any Motion Active: {_any_motion_active()}")
    _info(f"Sink Preset: {_state(SINK_PRESET)}")
    _info(f"Fridge Preset: {_state(FRIDGE_PRESET)}")
    _info(f"Sink Light: {_state(SINK_LIGHT)}")
    _info(f"Kitchen Main: {_state(KITCHEN_MAIN)}")
    _info(f"Test Bypass: {TEST_BYPASS_MODE}")
    _info("=== END DEBUG ===")