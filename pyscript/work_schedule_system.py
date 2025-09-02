"""
/config/pyscript/work_schedule_system.py
VERSION 1.0 - INTELLIGENT WORK SCHEDULE CALCULATOR
Automatically calculates every-other-Friday schedule and all holidays
Author: Claude Code Assistant with Frank S Elaschat

FRANK'S SCHEDULE:
- Off every other Friday (last worked: August 29, 2025)
- Holidays: New Year's Day, Memorial Day, 4th of July, Labor Day, 
  Thanksgiving, Day After Thanksgiving, Christmas Eve, Christmas Day
"""

import datetime
from datetime import timedelta

# --- Frank's Schedule Configuration ---
FRANK_SCHEDULE = {
    # Last Friday Frank worked (reference point for every-other-Friday calculation)
    "last_friday_worked": datetime.date(2025, 8, 29),
    
    # Fixed holidays (same date every year)
    "fixed_holidays": [
        {"month": 1, "day": 1, "name": "New Year's Day"},
        {"month": 7, "day": 4, "name": "Fourth of July"},
        {"month": 12, "day": 24, "name": "Christmas Eve"},
        {"month": 12, "day": 25, "name": "Christmas Day"}
    ],
    
    # Floating holidays (calculated each year)
    "floating_holidays": [
        "memorial_day",      # Last Monday in May
        "labor_day",         # First Monday in September  
        "thanksgiving",      # Fourth Thursday in November
        "day_after_thanksgiving"  # Friday after Thanksgiving
    ]
}

# --- Utility Functions (Frank's proven patterns) ---
def _norm(v, d=None): return d if v in (None, "", "unknown", "unavailable") else v
def _to_int(v, d=0):
    try: return int(float(v))
    except: return d
def _state(eid, d=None):
    try: return _norm(state.get(str(eid)), d)
    except: return d

# --- Holiday Calculation Functions ---
def calculate_memorial_day(year):
    """Last Monday in May"""
    # Start with May 31st and work backwards to find the last Monday
    may_31 = datetime.date(year, 5, 31)
    days_back = (may_31.weekday() + 1) % 7  # Monday = 0, so we need to go back to Monday
    return may_31 - timedelta(days=days_back)

def calculate_labor_day(year):
    """First Monday in September"""
    # Start with September 1st and find the first Monday
    sept_1 = datetime.date(year, 9, 1)
    days_forward = (7 - sept_1.weekday()) % 7  # Monday = 0
    return sept_1 + timedelta(days=days_forward)

def calculate_thanksgiving(year):
    """Fourth Thursday in November"""
    # Start with November 1st and find the first Thursday, then add 3 weeks
    nov_1 = datetime.date(year, 11, 1)
    # Thursday = 3
    days_to_first_thursday = (3 - nov_1.weekday()) % 7
    first_thursday = nov_1 + timedelta(days=days_to_first_thursday)
    return first_thursday + timedelta(weeks=3)  # Fourth Thursday

def calculate_day_after_thanksgiving(year):
    """Friday after Thanksgiving"""
    thanksgiving = calculate_thanksgiving(year)
    return thanksgiving + timedelta(days=1)

# --- Every Other Friday Calculator ---
def is_frank_off_friday(check_date):
    """Determine if Frank is off on a given Friday"""
    if check_date.weekday() != 4:  # Not a Friday
        return False
    
    last_worked = FRANK_SCHEDULE["last_friday_worked"]
    
    # Calculate weeks since last Friday worked
    days_diff = (check_date - last_worked).days
    weeks_diff = days_diff // 7
    
    # Frank is off on odd weeks (every other Friday)
    return weeks_diff % 2 == 1

# --- Holiday Checker ---
def is_holiday(check_date):
    """Check if a given date is one of Frank's holidays"""
    year = check_date.year
    month = check_date.month
    day = check_date.day
    
    # Check fixed holidays
    for holiday in FRANK_SCHEDULE["fixed_holidays"]:
        if month == holiday["month"] and day == holiday["day"]:
            return True, holiday["name"]
    
    # Check floating holidays
    floating_dates = {
        "memorial_day": calculate_memorial_day(year),
        "labor_day": calculate_labor_day(year),
        "thanksgiving": calculate_thanksgiving(year),
        "day_after_thanksgiving": calculate_day_after_thanksgiving(year)
    }
    
    for holiday_key, holiday_date in floating_dates.items():
        if check_date == holiday_date:
            holiday_names = {
                "memorial_day": "Memorial Day",
                "labor_day": "Labor Day", 
                "thanksgiving": "Thanksgiving",
                "day_after_thanksgiving": "Day After Thanksgiving"
            }
            return True, holiday_names[holiday_key]
    
    return False, None

# --- Main Work Schedule Calculator ---
class WorkScheduleCalculator:
    def is_working_today(self, check_date=None):
        """Determine if Frank is working on a given date"""
        if check_date is None:
            check_date = datetime.date.today()
        
        # Check if it's a weekend
        if check_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False, "Weekend"
        
        # Check if it's a holiday
        is_hol, holiday_name = is_holiday(check_date)
        if is_hol:
            return False, f"Holiday: {holiday_name}"
        
        # Check if it's an off Friday
        if check_date.weekday() == 4:  # Friday
            if is_frank_off_friday(check_date):
                return False, "Off Friday (Every Other Friday)"
        
        # Check manual overrides
        single_day_off = _state('input_boolean.single_day_off', 'off') == 'on'
        if single_day_off:
            return False, "Manual Single Day Off"
        
        # If we get here, it's a work day
        return True, "Regular Work Day"
    
    def get_next_off_friday(self):
        """Get the next Friday that Frank is off"""
        today = datetime.date.today()
        # Start from next Friday
        days_until_friday = (4 - today.weekday()) % 7
        if days_until_friday == 0:  # Today is Friday
            days_until_friday = 7  # Next Friday
        
        next_friday = today + timedelta(days=days_until_friday)
        
        # Keep checking Fridays until we find one he's off
        for i in range(8):  # Check up to 8 Fridays ahead
            friday = next_friday + timedelta(weeks=i)
            if is_frank_off_friday(friday):
                return friday
        
        return None
    
    def get_upcoming_holidays(self, days_ahead=90):
        """Get upcoming holidays in the next N days"""
        today = datetime.date.today()
        end_date = today + timedelta(days=days_ahead)
        holidays = []
        
        current_date = today
        while current_date <= end_date:
            is_hol, holiday_name = is_holiday(current_date)
            if is_hol:
                holidays.append({
                    "date": current_date,
                    "name": holiday_name,
                    "days_away": (current_date - today).days
                })
            current_date += timedelta(days=1)
        
        return sorted(holidays, key=lambda x: x["date"])

# --- Global Calculator Instance ---
work_calc = WorkScheduleCalculator()

# --- PyScript Services ---
@service("pyscript.calculate_work_schedule")
def calculate_work_schedule(date_str=None):
    """Calculate work schedule for a specific date"""
    try:
        if date_str:
            check_date = datetime.datetime.fromisoformat(date_str).date()
        else:
            check_date = datetime.date.today()
        
        is_working, reason = work_calc.is_working_today(check_date)
        
        return {
            "date": check_date.isoformat(),
            "is_working": is_working,
            "reason": reason,
            "weekday": check_date.strftime("%A")
        }
    
    except Exception as e:
        log.error(f"Error calculating work schedule: {e}")
        return {"error": str(e)}

@service("pyscript.get_work_schedule_info")
def get_work_schedule_info():
    """Get comprehensive work schedule information"""
    try:
        today = datetime.date.today()
        is_working, reason = work_calc.is_working_today(today)
        next_off_friday = work_calc.get_next_off_friday()
        upcoming_holidays = work_calc.get_upcoming_holidays()
        
        # Calculate some stats
        last_worked = FRANK_SCHEDULE["last_friday_worked"]
        weeks_since_reference = ((today - last_worked).days // 7)
        
        return {
            "today": {
                "date": today.isoformat(),
                "is_working": is_working,
                "reason": reason
            },
            "schedule_info": {
                "last_friday_worked": last_worked.isoformat(),
                "weeks_since_reference": weeks_since_reference,
                "next_off_friday": next_off_friday.isoformat() if next_off_friday else None
            },
            "upcoming_holidays": upcoming_holidays
        }
    
    except Exception as e:
        log.error(f"Error getting work schedule info: {e}")
        return {"error": str(e)}

# --- Daily Work Schedule Updates ---
@time_trigger("startup")
@time_trigger("cron(0 0 * * *)")  # Every day at midnight
def update_work_schedule_entities():
    """Update work schedule entities daily"""
    try:
        today = datetime.date.today()
        is_working, reason = work_calc.is_working_today(today)
        
        # Update main working_today sensor
        state.set("binary_sensor.working_today", "on" if is_working else "off", {
            "friendly_name": "Working Today",
            "reason": reason,
            "calculation_source": "pyscript_work_schedule",
            "icon": "mdi:briefcase" if is_working else "mdi:home"
        })
        
        # Update detailed status sensor
        state.set("sensor.work_schedule_status", reason, {
            "friendly_name": "Work Schedule Status",
            "is_working": is_working,
            "date": today.isoformat(),
            "weekday": today.strftime("%A"),
            "icon": "mdi:calendar-check"
        })
        
        # Update next off Friday info
        next_off_friday = work_calc.get_next_off_friday()
        if next_off_friday:
            days_until = (next_off_friday - today).days
            state.set("sensor.next_off_friday", next_off_friday.strftime("%B %d, %Y"), {
                "friendly_name": "Next Off Friday",
                "date": next_off_friday.isoformat(),
                "days_away": days_until,
                "icon": "mdi:calendar-weekend"
            })
        
        # Update upcoming holidays
        upcoming_holidays = work_calc.get_upcoming_holidays(30)  # Next 30 days
        if upcoming_holidays:
            next_holiday = upcoming_holidays[0]
            state.set("sensor.next_holiday", next_holiday["name"], {
                "friendly_name": "Next Holiday",
                "date": next_holiday["date"].isoformat(),
                "days_away": next_holiday["days_away"],
                "full_list": upcoming_holidays,
                "icon": "mdi:calendar-star"
            })
        
        log.info(f"Work schedule updated: {today.strftime('%A, %B %d')} - {'Working' if is_working else 'Off'} ({reason})")
        
    except Exception as e:
        log.error(f"Error updating work schedule entities: {e}")

# --- Holiday Preview Service ---
@service("pyscript.preview_holiday_schedule")
def preview_holiday_schedule(year=None):
    """Preview all holidays for a given year"""
    try:
        if year is None:
            year = datetime.date.today().year
        else:
            year = int(year)
        
        holidays = []
        
        # Add fixed holidays
        for holiday in FRANK_SCHEDULE["fixed_holidays"]:
            date = datetime.date(year, holiday["month"], holiday["day"])
            holidays.append({
                "date": date.isoformat(),
                "name": holiday["name"],
                "type": "fixed",
                "weekday": date.strftime("%A")
            })
        
        # Add floating holidays
        floating_dates = {
            "Memorial Day": calculate_memorial_day(year),
            "Labor Day": calculate_labor_day(year),
            "Thanksgiving": calculate_thanksgiving(year),
            "Day After Thanksgiving": calculate_day_after_thanksgiving(year)
        }
        
        for name, date in floating_dates.items():
            holidays.append({
                "date": date.isoformat(),
                "name": name,
                "type": "floating",
                "weekday": date.strftime("%A")
            })
        
        # Sort by date
        holidays.sort(key=lambda x: x["date"])
        
        # Update sensor with preview
        state.set(f"sensor.holiday_preview_{year}", f"{len(holidays)} holidays", {
            "friendly_name": f"Holiday Preview {year}",
            "year": year,
            "holidays": holidays,
            "total_count": len(holidays),
            "icon": "mdi:calendar-multiple"
        })
        
        return holidays
        
    except Exception as e:
        log.error(f"Error previewing holiday schedule: {e}")
        return {"error": str(e)}

# --- Friday Schedule Preview ---
@service("pyscript.preview_friday_schedule")
def preview_friday_schedule(months_ahead=6):
    """Preview upcoming Friday work/off schedule"""
    try:
        today = datetime.date.today()
        end_date = today + timedelta(days=30 * months_ahead)
        
        fridays = []
        current_date = today
        
        while current_date <= end_date:
            if current_date.weekday() == 4:  # Friday
                is_off = is_frank_off_friday(current_date)
                is_hol, holiday_name = is_holiday(current_date)
                
                status = "Holiday" if is_hol else ("Off" if is_off else "Work")
                reason = holiday_name if is_hol else ("Every Other Friday" if is_off else "Regular Friday")
                
                fridays.append({
                    "date": current_date.isoformat(),
                    "formatted_date": current_date.strftime("%B %d, %Y"),
                    "status": status,
                    "reason": reason,
                    "is_working": not (is_off or is_hol)
                })
            
            current_date += timedelta(days=1)
        
        # Update sensor
        state.set("sensor.friday_schedule_preview", f"{len(fridays)} Fridays", {
            "friendly_name": "Friday Schedule Preview",
            "fridays": fridays,
            "months_ahead": months_ahead,
            "icon": "mdi:calendar-week"
        })
        
        return fridays
        
    except Exception as e:
        log.error(f"Error previewing Friday schedule: {e}")
        return {"error": str(e)}

# --- System Integration ---
@time_trigger("startup")
def initialize_work_schedule_system():
    """Initialize work schedule system on startup"""
    try:
        log.info("Work Schedule PyScript System - Initializing")
        
        # Update all entities immediately
        update_work_schedule_entities()
        
        # Generate preview data
        preview_holiday_schedule()
        preview_friday_schedule()
        
        log.info("Work Schedule System ready")
        
        # Log today's status for verification
        today = datetime.date.today()
        is_working, reason = work_calc.is_working_today(today)
        log.info(f"Today ({today.strftime('%A, %B %d, %Y')}): {'WORKING' if is_working else 'OFF'} - {reason}")
        
    except Exception as e:
        log.error(f"Error initializing work schedule system: {e}")

# --- Debug and Testing ---
@service("pyscript.test_work_schedule_date")
def test_work_schedule_date(date_str):
    """Test work schedule calculation for any date"""
    try:
        test_date = datetime.datetime.fromisoformat(date_str).date()
        is_working, reason = work_calc.is_working_today(test_date)
        
        # Additional info for testing
        is_friday = test_date.weekday() == 4
        if is_friday:
            is_off_friday = is_frank_off_friday(test_date)
            weeks_from_ref = ((test_date - FRANK_SCHEDULE["last_friday_worked"]).days // 7)
        else:
            is_off_friday = False
            weeks_from_ref = None
        
        is_hol, holiday_name = is_holiday(test_date)
        
        result = {
            "date": test_date.isoformat(),
            "formatted_date": test_date.strftime("%A, %B %d, %Y"),
            "is_working": is_working,
            "reason": reason,
            "is_friday": is_friday,
            "is_off_friday": is_off_friday if is_friday else None,
            "weeks_from_reference": weeks_from_ref if is_friday else None,
            "is_holiday": is_hol,
            "holiday_name": holiday_name if is_hol else None,
            "weekday": test_date.strftime("%A")
        }
        
        log.info(f"Test result for {test_date}: {result}")
        return result
        
    except Exception as e:
        log.error(f"Error testing work schedule: {e}")
        return {"error": str(e)}