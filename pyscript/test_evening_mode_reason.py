"""
/config/pyscript/test_evening_mode_reason.py

Purpose: Explain exactly why Evening mode would be selected at a given time
and show the outcome under both the OLD logic (with the hard fallback to
Evening) and the NEW logic we implemented (strict evening gating, no fallback).

Usage (from HA Developer Tools > Services):
- pyscript.test_evening_mode_reason
  args:
    date: "2025-09-06"          # Optional; defaults to today
    time: "06:30:00"            # Optional; defaults to current time
    sun_elevation: -2            # Optional; if omitted, uses sensor if available
    current_state: "Night"       # Optional; your current input_select.home_state
    override_evening: false      # Optional; input_boolean.evening_mode_override

This script prints a detailed explanation to the log.
"""

from datetime import datetime, date, time as dt_time


def _num(val, d):
    try:
        return float(val)
    except Exception:
        return float(d)


def _state(eid, d=None):
    try:
        v = state.get(eid)
        return v if v not in (None, "unknown", "unavailable", "") else d
    except Exception:
        return d


def _parse_datetime(parts_date: str | None, parts_time: str | None) -> datetime:
    if parts_date and parts_time:
        try:
            return datetime.fromisoformat(f"{parts_date} {parts_time}")
        except Exception:
            pass
    # Fallback to now
    return datetime.now()


def _calc_home_mode_old(h: int, m: int, sun: float, day_th: float, workday: bool,
                        cutoff_str: str | None, learned: float, override: bool,
                        current: str) -> tuple[str, str]:
    # OLD TEMPLATE LOGIC (problematic hard fallback to Evening)
    cutoff_ok = False
    try:
        if cutoff_str:
            cutoff_h, cutoff_m, *_ = [int(x) for x in cutoff_str.split(":")]  # HH:MM:SS
            cutoff_ok = (h, m) >= (cutoff_h, cutoff_m)
    except Exception:
        cutoff_ok = False

    if override or cutoff_ok or (sun < learned and h >= 15):
        return "Evening", "override/cutoff/afternoon+sun<threshold"
    elif workday and ((h == 4 and m >= 50) or h == 5):
        return "Early Morning", "workday morning window"
    elif sun >= day_th:
        return "Day", "sun>=day_threshold"
    elif current == "Early Morning":
        return "Early Morning", "stickiness"
    else:
        return "Evening", "HARD_FALLBACK (root cause of AM flips)"


def _calc_home_mode_new(h: int, sun: float, day_th: float, ramp_active: bool,
                        cutoff_str: str | None, learned: float, override: bool,
                        current: str) -> tuple[str, str]:
    # NEW LOGIC (strict evening gating, no hard fallback)
    cutoff_ok = False
    try:
        if cutoff_str:
            hh, mm, *_ = [int(x) for x in cutoff_str.split(":")]  # HH:MM:SS
            cutoff_ok = (h, 0) >= (hh, mm)
    except Exception:
        cutoff_ok = False

    if override or cutoff_ok or (h >= 15 and sun < learned):
        return "Evening", "override/cutoff/afternoon+sun<threshold"
    elif ramp_active:
        return "Early Morning", "ramp_active"
    elif sun >= day_th:
        return "Day", "sun>=day_threshold"
    else:
        return current, "KEEP_CURRENT (no forced flip)"


@service("pyscript.test_evening_mode_reason")
def test_evening_mode_reason(date: str | None = None,
                             time: str | None = None,
                             sun_elevation: float | None = None,
                             current_state: str | None = None,
                             override_evening: bool | None = None):
    """Explain why Evening would (or would not) trigger for the given moment."""
    dt = _parse_datetime(date, time)
    h, m = dt.hour, dt.minute

    # Load inputs from HA if not provided
    current = current_state or _state("input_select.home_state", "Night")
    workday = _state("binary_sensor.working_today", "off") == "on"
    ramp_active = _state("input_boolean.sleep_in_ramp_active", "off") == "on"
    cutoff_str = _state("input_datetime.evening_time_cutoff", "22:00:00")
    learned = _num(_state("input_number.manual_evening_elevation_setting", 4), 4)
    day_th = _num(_state("input_number.current_day_threshold", 10), 10)
    override = bool(override_evening) if override_evening is not None else (_state("input_boolean.evening_mode_override", "off") == "on")
    sun = float(sun_elevation) if sun_elevation is not None else _num(_state("sensor.sun_elevation_frequent", 0), 0)

    # Evaluate both logics
    old_mode, old_reason = _calc_home_mode_old(h, m, sun, day_th, workday, cutoff_str, learned, override, current)
    new_mode, new_reason = _calc_home_mode_new(h, sun, day_th, ramp_active, cutoff_str, learned, override, current)

    log.warning("[EveningModeTest] ------------------------------------------------------------")
    log.warning(f"[EveningModeTest] Scenario: {dt.strftime('%Y-%m-%d %H:%M')} (weekday={dt.weekday()}, 0=Mon)")
    log.warning(f"[EveningModeTest] Inputs: current={current}, workday={workday}, ramp_active={ramp_active}, override={override}")
    log.warning(f"[EveningModeTest]        sun={sun}°, learned_evening={learned}°, day_threshold={day_th}°, cutoff={cutoff_str}")
    log.warning(f"[EveningModeTest] OLD  => {old_mode}   (reason: {old_reason})")
    log.warning(f"[EveningModeTest] NEW  => {new_mode}   (reason: {new_reason})")
    if old_reason.startswith("HARD_FALLBACK") and new_mode != "Evening":
        log.warning("[EveningModeTest] ✅ FIX CONFIRMED: Old logic would force Evening, new logic prevents it")
    return {
        "scenario": dt.isoformat(),
        "inputs": {
            "current": current,
            "workday": workday,
            "ramp_active": ramp_active,
            "override": override,
            "sun": sun,
            "learned": learned,
            "day_threshold": day_th,
            "cutoff": cutoff_str,
        },
        "old": {"mode": old_mode, "reason": old_reason},
        "new": {"mode": new_mode, "reason": new_reason},
    }

