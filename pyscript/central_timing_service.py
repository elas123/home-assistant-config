"""
ALS Central Timing Service - The Brain (Tier 2)
Calculates optimal daily schedules and timing decisions for the morning ramp system.
Runs at midnight to determine the day's context and publishes morning_day_transition_time.

Author: Frank's ALS System
Version: 3.0 (Complete Rebuild)
Integration: Hypothesis testing ready
"""

import logging
from datetime import datetime, time, timedelta, date
from typing import Dict, Any, Optional, Tuple
import json
import math

_LOGGER = logging.getLogger(__name__)

class CentralTimingService:
    """
    The Brain of the ALS system - makes all timing decisions
    Calculates optimal schedules based on multiple factors
    """
    
    def __init__(self, hass=None):
        self.hass = hass
        self.initialized = False
        self.current_schedule = {}
        self.last_calculation_date = None
        
    def initialize(self):
        """Initialize the timing service"""
        if not self.initialized:
            _LOGGER.info("🧠 Initializing ALS Central Timing Service...")
            self.initialized = True
            
    @pyscript_executor
    def calculate_daily_schedule(self, target_date: date = None) -> Dict[str, Any]:
        """
        Main calculation function - determines the day's optimal schedule
        Called at midnight or on-demand for testing
        
        Logic Priority:
        1. single_day_off override
        2. work_schedule_system.py detection
        3. Default to Workday
        """
        if target_date is None:
            target_date = date.today()
            
        _LOGGER.info(f"🧠 Calculating daily schedule for {target_date}")
        
        try:
            # Get master kill switch status
            if self.hass and not self._is_system_enabled():
                _LOGGER.info("⏹️ Central timing system disabled via kill switch")
                return self._get_fallback_schedule(target_date, "system_disabled")
            
            # Step 1: Check single day off override
            is_single_day_off = self._check_single_day_off()
            
            # Step 2: Determine workday status
            if is_single_day_off:
                is_workday = False
                workday_source = "single_day_off_override"
            else:
                is_workday = self._determine_workday_status(target_date)
                workday_source = "work_schedule_system" if self.hass else "default_logic"
            
            # Step 3: Get seasonal adjustments
            seasonal_data = self._calculate_seasonal_adjustments(target_date)
            
            # Step 4: Calculate sunrise and base timing
            sunrise_time = self._get_sunrise_time(target_date)
            
            # Step 5: Calculate morning day transition time
            morning_transition = self._calculate_morning_transition_time(
                sunrise_time=sunrise_time,
                is_workday=is_workday,
                seasonal_data=seasonal_data,
                target_date=target_date
            )
            
            # Step 6: Calculate ramp parameters
            ramp_params = self._calculate_ramp_parameters(
                is_workday=is_workday,
                seasonal_data=seasonal_data
            )
            
            # Build the complete schedule
            schedule = {
                "calculation_date": target_date.isoformat(),
                "calculation_timestamp": datetime.now().isoformat(),
                "is_workday": is_workday,
                "workday_source": workday_source,
                "sunrise_time": sunrise_time.isoformat(),
                "morning_day_transition_time": morning_transition.isoformat(),
                "seasonal_adjustments": seasonal_data,
                "ramp_parameters": ramp_params,
                "system_status": "active",
                "version": "3.0"
            }
            
            # Cache the result
            self.current_schedule = schedule
            self.last_calculation_date = target_date
            
            # Publish to Home Assistant if available
            if self.hass:
                self._publish_schedule_to_ha(schedule)
            
            _LOGGER.info(f"✅ Daily schedule calculated: {is_workday=}, transition={morning_transition.strftime('%H:%M')}")
            return schedule
            
        except Exception as e:
            _LOGGER.error(f"❌ Error calculating daily schedule: {e}")
            return self._get_fallback_schedule(target_date, f"calculation_error: {str(e)}")
    
    def _is_system_enabled(self) -> bool:
        """Check if the central timing system is enabled via kill switch"""
        if not self.hass:
            return True  # Default enabled for testing
            
        try:
            state = self.hass.states.get("input_boolean.enable_central_timing")
            return state and state.state == "on"
        except Exception:
            return False
    
    def _check_single_day_off(self) -> bool:
        """Check if single day off override is active"""
        if not self.hass:
            return False
            
        try:
            state = self.hass.states.get("input_boolean.single_day_off")
            return state and state.state == "on"
        except Exception:
            return False
    
    def _determine_workday_status(self, target_date: date) -> bool:
        """
        Determine if target_date is a workday
        Logic: work_schedule_system.py > Default to Workday
        """
        try:
            # Try to call work schedule system if available
            if self.hass:
                # Check if work_schedule_system is available
                work_schedule_state = self.hass.states.get("sensor.work_schedule_today")
                if work_schedule_state and work_schedule_state.state not in ['unknown', 'unavailable']:
                    return work_schedule_state.state.lower() == "workday"
            
            # Default logic: Monday-Friday = Workday, Saturday-Sunday = Off Day
            weekday = target_date.weekday()  # 0=Monday, 6=Sunday
            return weekday < 5  # Monday through Friday
            
        except Exception as e:
            _LOGGER.warning(f"Error determining workday status, defaulting to workday: {e}")
            return True  # Default to workday for safety
    
    def _calculate_seasonal_adjustments(self, target_date: date) -> Dict[str, Any]:
        """Calculate seasonal adjustments for timing and brightness"""
        try:
            # Determine season
            month = target_date.month
            day = target_date.day
            
            if (month == 12 and day >= 21) or (month <= 2) or (month == 3 and day < 20):
                season = "winter"
            elif (month == 3 and day >= 20) or (month <= 5) or (month == 6 and day < 21):
                season = "spring"  
            elif (month == 6 and day >= 21) or (month <= 8) or (month == 9 and day < 22):
                season = "summer"
            else:
                season = "fall"
            
            # Get seasonal boost values from Home Assistant
            winter_boost = self._get_helper_value("input_number.als_winter_boost", 10)
            fall_boost = self._get_helper_value("input_number.als_fall_boost", 5)
            
            # Calculate adjustments
            brightness_boost = 0
            timing_adjustment_minutes = 0
            
            if season == "winter":
                brightness_boost = winter_boost
                timing_adjustment_minutes = -15  # Earlier transition in winter
            elif season == "fall":
                brightness_boost = fall_boost
                timing_adjustment_minutes = -10  # Slightly earlier in fall
            elif season == "spring":
                timing_adjustment_minutes = 10   # Later transition in spring
            # Summer uses default values
            
            return {
                "season": season,
                "brightness_boost_percent": brightness_boost,
                "timing_adjustment_minutes": timing_adjustment_minutes,
                "calculation_date": target_date.isoformat()
            }
            
        except Exception as e:
            _LOGGER.warning(f"Error calculating seasonal adjustments: {e}")
            return {
                "season": "unknown",
                "brightness_boost_percent": 0,
                "timing_adjustment_minutes": 0
            }
    
    def _get_sunrise_time(self, target_date: date) -> datetime:
        """Get sunrise time for the target date"""
        try:
            if self.hass:
                # Try to get actual sunrise from Home Assistant
                sun_state = self.hass.states.get("sun.sun")
                if sun_state and "next_rising" in sun_state.attributes:
                    sunrise_str = sun_state.attributes["next_rising"]
                    sunrise_dt = datetime.fromisoformat(sunrise_str.replace('Z', '+00:00'))
                    # Convert to local time if needed
                    return sunrise_dt.replace(tzinfo=None)
            
            # Fallback: estimate sunrise based on date and season
            # Rough approximation for testing
            base_hour = 6
            base_minute = 30
            
            # Adjust for season (very rough)
            month = target_date.month
            if month in [12, 1, 2]:  # Winter
                base_hour = 7
                base_minute = 15
            elif month in [6, 7, 8]:  # Summer
                base_hour = 5
                base_minute = 45
            
            return datetime.combine(target_date, time(base_hour, base_minute))
            
        except Exception as e:
            _LOGGER.warning(f"Error getting sunrise time: {e}")
            return datetime.combine(target_date, time(6, 30))  # Fallback
    
    def _calculate_morning_transition_time(
        self, 
        sunrise_time: datetime, 
        is_workday: bool, 
        seasonal_data: Dict[str, Any],
        target_date: date
    ) -> datetime:
        """
        Calculate the optimal morning day transition time
        This is when the system should finish ramping and switch to Day mode
        """
        try:
            # Base calculation: sunrise + buffer
            base_buffer_minutes = 60 if is_workday else 90
            
            # Apply seasonal adjustment
            seasonal_adjustment = seasonal_data.get("timing_adjustment_minutes", 0)
            total_buffer = base_buffer_minutes + seasonal_adjustment
            
            # Calculate transition time
            transition_time = sunrise_time + timedelta(minutes=total_buffer)
            
            # Apply constraints
            # Workday: no later than 8:30 AM, no earlier than 6:00 AM
            # Off-day: no later than 10:00 AM, no earlier than 7:00 AM
            if is_workday:
                min_time = datetime.combine(target_date, time(6, 0))
                max_time = datetime.combine(target_date, time(8, 30))
            else:
                min_time = datetime.combine(target_date, time(7, 0))
                max_time = datetime.combine(target_date, time(10, 0))
            
            # Clamp to constraints
            transition_time = max(min_time, min(max_time, transition_time))
            
            return transition_time
            
        except Exception as e:
            _LOGGER.error(f"Error calculating morning transition time: {e}")
            # Fallback times
            fallback_hour = 7 if is_workday else 8
            return datetime.combine(target_date, time(fallback_hour, 30))
    
    def _calculate_ramp_parameters(self, is_workday: bool, seasonal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate parameters for the morning ramp execution"""
        try:
            # Base durations from helpers
            workday_base = self._get_helper_value("input_number.workday_ramp_base_duration", 50)
            offday_base = self._get_helper_value("input_number.offday_ramp_base_duration", 75)
            
            base_duration = workday_base if is_workday else offday_base
            
            # Seasonal adjustments to duration
            seasonal_brightness_boost = seasonal_data.get("brightness_boost_percent", 0)
            if seasonal_brightness_boost > 5:
                # Longer ramp in darker seasons
                duration_adjustment = 5 if is_workday else 10
            else:
                duration_adjustment = 0
            
            final_duration = base_duration + duration_adjustment
            
            # Ramp curve parameters
            start_brightness = self._get_helper_value("input_number.ramp_start_brightness", 10)
            end_brightness = self._get_helper_value("input_number.ramp_end_brightness", 100)
            
            # Temperature parameters (for tunable lights)
            start_temp = self._get_helper_value("input_number.gradient_start_temp", 2000)
            end_temp = self._get_helper_value("input_number.gradient_end_temp", 4000)
            
            return {
                "duration_minutes": final_duration,
                "start_brightness_percent": start_brightness,
                "end_brightness_percent": end_brightness + seasonal_brightness_boost,
                "start_temperature_kelvin": start_temp,
                "end_temperature_kelvin": end_temp,
                "curve_type": "smooth_exponential",
                "is_workday": is_workday,
                "seasonal_boost": seasonal_brightness_boost
            }
            
        except Exception as e:
            _LOGGER.error(f"Error calculating ramp parameters: {e}")
            return {
                "duration_minutes": 50 if is_workday else 75,
                "start_brightness_percent": 10,
                "end_brightness_percent": 100,
                "start_temperature_kelvin": 2000,
                "end_temperature_kelvin": 4000,
                "curve_type": "linear",
                "is_workday": is_workday,
                "seasonal_boost": 0
            }
    
    def _get_helper_value(self, entity_id: str, default_value: float) -> float:
        """Get value from Home Assistant helper entity with fallback"""
        try:
            if self.hass:
                state = self.hass.states.get(entity_id)
                if state and state.state not in ['unknown', 'unavailable']:
                    return float(state.state)
        except Exception:
            pass
        return default_value
    
    def _get_fallback_schedule(self, target_date: date, reason: str) -> Dict[str, Any]:
        """Generate a safe fallback schedule when calculation fails"""
        _LOGGER.warning(f"Using fallback schedule: {reason}")
        
        return {
            "calculation_date": target_date.isoformat(),
            "calculation_timestamp": datetime.now().isoformat(),
            "is_workday": True,  # Safe default
            "workday_source": "fallback",
            "sunrise_time": datetime.combine(target_date, time(6, 30)).isoformat(),
            "morning_day_transition_time": datetime.combine(target_date, time(7, 30)).isoformat(),
            "seasonal_adjustments": {
                "season": "unknown",
                "brightness_boost_percent": 0,
                "timing_adjustment_minutes": 0
            },
            "ramp_parameters": {
                "duration_minutes": 50,
                "start_brightness_percent": 10,
                "end_brightness_percent": 100,
                "start_temperature_kelvin": 2000,
                "end_temperature_kelvin": 4000,
                "curve_type": "linear",
                "is_workday": True,
                "seasonal_boost": 0
            },
            "system_status": "fallback",
            "fallback_reason": reason,
            "version": "3.0"
        }
    
    def _publish_schedule_to_ha(self, schedule: Dict[str, Any]):
        """Publish the calculated schedule to Home Assistant entities"""
        try:
            if not self.hass:
                return
            
            # Update the main transition time entity
            transition_time = schedule["morning_day_transition_time"]
            self.hass.states.set(
                "sensor.morning_day_transition_time",
                transition_time,
                {
                    "friendly_name": "Morning Day Transition Time",
                    "icon": "mdi:weather-sunrise",
                    "is_workday": schedule["is_workday"],
                    "sunrise_time": schedule["sunrise_time"],
                    "ramp_duration": schedule["ramp_parameters"]["duration_minutes"],
                    "seasonal_boost": schedule["seasonal_adjustments"]["brightness_boost_percent"],
                    "last_calculation": schedule["calculation_timestamp"],
                    "system_version": schedule["version"]
                }
            )
            
            # Update system status sensor
            self.hass.states.set(
                "sensor.als_central_timing_status",
                schedule["system_status"],
                {
                    "friendly_name": "ALS Central Timing Status",
                    "icon": "mdi:brain",
                    "schedule": json.dumps(schedule),
                    "last_update": datetime.now().isoformat()
                }
            )
            
            _LOGGER.info("📊 Schedule published to Home Assistant")
            
        except Exception as e:
            _LOGGER.error(f"Error publishing schedule to HA: {e}")
    
    def get_current_schedule(self) -> Optional[Dict[str, Any]]:
        """Get the current calculated schedule"""
        if self.last_calculation_date == date.today():
            return self.current_schedule
        else:
            # Schedule is stale, recalculate
            return self.calculate_daily_schedule()
    
    def calculate_ramp_schedule(self, motion_datetime: datetime, is_workday: bool = None) -> Dict[str, Any]:
        """
        Calculate ramp schedule based on motion detection time
        Used by morning ramp executor
        """
        try:
            motion_date = motion_datetime.date()
            motion_time = motion_datetime.time()
            
            # Get or calculate daily schedule
            daily_schedule = self.get_current_schedule()
            if not daily_schedule or daily_schedule["calculation_date"] != motion_date.isoformat():
                daily_schedule = self.calculate_daily_schedule(motion_date)
            
            # Use provided workday status or get from schedule
            if is_workday is None:
                is_workday = daily_schedule["is_workday"]
            
            # Get target transition time
            target_transition_str = daily_schedule["morning_day_transition_time"]
            target_transition = datetime.fromisoformat(target_transition_str)
            
            # Calculate ramp timing
            ramp_params = daily_schedule["ramp_parameters"]
            ramp_duration_minutes = ramp_params["duration_minutes"]
            
            # For workday: fixed 50-minute ramp if motion between 4:50-5:00 AM
            if is_workday and time(4, 50) <= motion_time <= time(5, 0):
                ramp_start = motion_datetime
                ramp_end = ramp_start + timedelta(minutes=50)
            else:
                # Off-day or late motion: ramp to target transition time
                ramp_end = target_transition
                ramp_start = ramp_end - timedelta(minutes=ramp_duration_minutes)
                
                # Ensure ramp doesn't start before motion
                if ramp_start < motion_datetime:
                    ramp_start = motion_datetime
                    # Minimum 30-minute ramp
                    if (ramp_end - ramp_start).seconds < 1800:  # 30 minutes
                        ramp_end = ramp_start + timedelta(minutes=30)
            
            return {
                "start_time": ramp_start.isoformat(),
                "end_time": ramp_end.isoformat(),
                "ramp_duration": int((ramp_end - ramp_start).seconds / 60),
                "target_transition_time": target_transition.isoformat(),
                "is_workday": is_workday,
                "motion_time": motion_datetime.isoformat(),
                "ramp_parameters": ramp_params
            }
            
        except Exception as e:
            _LOGGER.error(f"Error calculating ramp schedule: {e}")
            # Fallback schedule
            fallback_end = motion_datetime + timedelta(minutes=60)
            return {
                "start_time": motion_datetime.isoformat(),
                "end_time": fallback_end.isoformat(),
                "ramp_duration": 60,
                "target_transition_time": fallback_end.isoformat(),
                "is_workday": True,
                "motion_time": motion_datetime.isoformat(),
                "ramp_parameters": daily_schedule.get("ramp_parameters", {}) if 'daily_schedule' in locals() else {}
            }

# Service functions for Home Assistant
@service
def calculate_daily_schedule_service(target_date: str = None):
    """Service to manually trigger daily schedule calculation"""
    timing_service = CentralTimingService(hass)
    timing_service.initialize()
    
    if target_date:
        target = datetime.fromisoformat(target_date).date()
    else:
        target = date.today()
    
    result = timing_service.calculate_daily_schedule(target)
    _LOGGER.info(f"Daily schedule calculated via service call: {result['morning_day_transition_time']}")
    return result

@service  
def get_ramp_schedule_service(motion_time: str, is_workday: bool = None):
    """Service to calculate ramp schedule for given motion time"""
    timing_service = CentralTimingService(hass)
    timing_service.initialize()
    
    motion_datetime = datetime.fromisoformat(motion_time)
    result = timing_service.calculate_ramp_schedule(motion_datetime, is_workday)
    return result

@service
def get_timing_status_service():
    """Service to get current timing system status"""
    timing_service = CentralTimingService(hass)
    timing_service.initialize()
    
    current_schedule = timing_service.get_current_schedule()
    
    return {
        "system_enabled": timing_service._is_system_enabled(),
        "current_schedule": current_schedule,
        "last_calculation": timing_service.last_calculation_date.isoformat() if timing_service.last_calculation_date else None
    }

# Midnight automation trigger
@time_trigger("00:00:00")
def midnight_schedule_calculation():
    """Automatically calculate daily schedule at midnight"""
    _LOGGER.info("🌙 Midnight triggered - calculating daily schedule")
    timing_service = CentralTimingService(hass)
    timing_service.initialize()
    
    schedule = timing_service.calculate_daily_schedule()
    _LOGGER.info(f"🌅 Tomorrow's schedule: transition at {schedule['morning_day_transition_time']}")

if __name__ == "__main__":
    # Testing mode
    print("🧠 ALS Central Timing Service - Testing Mode")
    service = CentralTimingService()
    service.initialize()
    
    schedule = service.calculate_daily_schedule()
    print(f"✅ Test schedule calculated:")
    print(f"   📅 Date: {schedule['calculation_date']}")
    print(f"   💼 Workday: {schedule['is_workday']}")
    print(f"   🌅 Sunrise: {schedule['sunrise_time']}")
    print(f"   ⏰ Transition: {schedule['morning_day_transition_time']}")
    print(f"   🕒 Ramp Duration: {schedule['ramp_parameters']['duration_minutes']} min")
    print(f"   🌟 Seasonal Boost: {schedule['seasonal_adjustments']['brightness_boost_percent']}%")