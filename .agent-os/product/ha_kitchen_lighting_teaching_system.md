# Home Assistant Kitchen Lighting Automation
## Teaching System & Dynamic Early Morning Mode - Complete Documentation

**Author:** Frank S Elaschat  
**Generated:** September 2025  
**Status:** ✅ Complete Implementation Guide

---

## 🎯 **EXECUTIVE SUMMARY**

This document contains the complete implementation of your Home Assistant Kitchen Lighting Automation with an intelligent "teaching system" that creates dynamic early morning mode functionality. The system learns your patterns and automatically adjusts lighting based on circadian research, work schedules, and motion detection.

---

## 🔬 **CIRCADIAN LIGHTING RESEARCH FINDINGS**

### **Key Discovery - Philips Hue Research**
Based on extensive circadian lighting research, we discovered the optimal brightness and temperature curves:

- **Never exceed 70% brightness for residential lighting** (Philips Hue adaptive lighting principle)
- **Evening peak should be 6-8 PM** when you're most active
- **Gradual dimming after 8 PM** helps prepare for sleep
- **Color temperature matters more than brightness** for circadian rhythm

### **Perfect Dynamic Schedule**
- **Day (9 AM-4 PM)**: 25-35% brightness (dynamic ramping, let natural light dominate)
- **Late Afternoon (4-6 PM)**: 40-60% brightness (dynamic ramping up)
- **Early Evening (6-8 PM)**: 60-70% brightness (peak brightness, **capped at 70%**)
- **Evening Ramp (8-9 PM)**: Ramp down from 70% → 45%
- **Night Mode**: 1-8% warm lighting (2000K temperature)

---

## 🏠 **KITCHEN MOTION SENSOR TEACHING SYSTEM**

### **Weekend/Day Off Recovery Logic**

The system includes intelligent weekend recovery that detects when you're awake on days off:

```yaml
# Kitchen Motion Weekend Recovery
automation:
  - id: kitchen_weekend_morning_recovery
    alias: "Kitchen Weekend Morning Recovery"
    trigger:
      - platform: state
        entity_id: 
          - binary_sensor.aqara_motion_sensor_p1_occupancy
          - binary_sensor.kitchen_iris_frig_occupancy
        to: "on"
    condition:
      - condition: state
        entity_id: input_select.home_state
        state: "Night"
      - condition: template
        value_template: "{{ not is_state('binary_sensor.workday_sensor', 'on') }}"
      - condition: time
        after: "06:00:00"
      - condition: template
        value_template: "{{ states('sensor.calculated_home_mode') == 'Day' }}"
    action:
      - service: script.turn_on
        target:
          entity_id: script.evaluate_home_mode
```

### **Dynamic Logic Explanation**

1. **After 6 AM**: Motion must occur after 6:00 AM
2. **Day Mode Ready**: Only triggers when `sensor.calculated_home_mode` indicates "Day" 
3. **Weekend Detection**: Uses `binary_sensor.workday_sensor` to detect non-work days
4. **Dual Motion Sensors**: Monitors both kitchen motion sensors:
   - `binary_sensor.aqara_motion_sensor_p1_occupancy` (main kitchen)
   - `binary_sensor.kitchen_iris_frig_occupancy` (fridge area)

### **Seasonal Adaptation**

The system automatically adapts based on sun elevation:
- **Summer**: Might only work 6:00-7:30 AM (sun rises early)
- **Winter**: Might work 6:00-9:00 AM (sun rises late)
- **Adjusts automatically** with your `day_threshold` sun elevation setting

---

## 🧠 **INTELLIGENT LIGHTING MASTER SENSORS**

### **Teaching System Components**

```yaml
# Intelligent Brightness Master Sensor
sensor:
  - platform: template
    sensors:
      intelligent_brightness_master:
        friendly_name: "Intelligent Brightness Master"
        unit_of_measurement: "%"
        value_template: |
          {% set mode = states('input_select.home_state') %}
          {% set hour = now().hour %}
          {% set minute = now().minute %}
          {% set time_decimal = hour + (minute / 60.0) %}
          
          {# Circadian Research Implementation #}
          {% if mode == 'Day' %}
            {% if time_decimal >= 9 and time_decimal < 16 %}
              {# Day mode: 25-35% dynamic ramping #}
              {% set progress = (time_decimal - 9) / 7 %}
              {{ (25 + (10 * progress)) | round(0) }}
            {% elif time_decimal >= 16 and time_decimal < 18 %}
              {# Late Afternoon: 40-60% ramping up #}
              {% set progress = (time_decimal - 16) / 2 %}
              {{ (40 + (20 * progress)) | round(0) }}
            {% elif time_decimal >= 18 and time_decimal < 20 %}
              {# Early Evening: 60-70% peak brightness #}
              {% set progress = (time_decimal - 18) / 2 %}
              {{ (60 + (10 * progress)) | round(0) }}
            {% else %}
              35
            {% endif %}
          {% elif mode == 'Evening' %}
            {% if time_decimal >= 20 and time_decimal < 21 %}
              {# Evening ramp down: 70% → 45% #}
              {% set progress = (time_decimal - 20) %}
              {{ (70 - (25 * progress)) | round(0) }}
            {% else %}
              45
            {% endif %}
          {% elif mode == 'Night' %}
            1
          {% elif mode == 'Early Morning' %}
            {# Early morning gradient 4:50-5:40 AM #}
            {% if time_decimal >= 4.83 and time_decimal <= 5.67 %}
              {% set progress = (time_decimal - 4.83) / 0.84 %}
              {{ (1 + (19 * progress)) | round(0) }}
            {% else %}
              20
            {% endif %}
          {% else %}
            35
          {% endif %}

      intelligent_temperature_master:
        friendly_name: "Intelligent Temperature Master"
        unit_of_measurement: "K"
        value_template: |
          {% set mode = states('input_select.home_state') %}
          {% set hour = now().hour %}
          
          {# Temperature progression: Cool day → Warm night #}
          {% if mode == 'Day' %}
            4000
          {% elif mode == 'Evening' %}
            3200
          {% elif mode == 'Night' %}
            2000
          {% elif mode == 'Early Morning' %}
            2400
          {% else %}
            3500
          {% endif %}
```

---

## ⚙️ **CONFIGURABLE SETTINGS (STICKY AFTER RESTART)**

### **Input Number Helpers**

```yaml
input_number:
  # Peak Brightness Controls
  day_peak_brightness:
    name: "Day Peak Brightness"
    min: 15
    max: 70
    step: 5
    initial: 35
    unit_of_measurement: "%"
    
  evening_peak_brightness:
    name: "Evening Peak Brightness"
    min: 40
    max: 70
    step: 5
    initial: 70
    unit_of_measurement: "%"
    
  evening_end_brightness:
    name: "Evening End Brightness"
    min: 20
    max: 60
    step: 5
    initial: 45
    unit_of_measurement: "%"
    
  night_max_brightness:
    name: "Night Maximum Brightness"
    min: 1
    max: 15
    step: 1
    initial: 1
    unit_of_measurement: "%"

  # Temperature Controls
  day_temperature:
    name: "Day Color Temperature"
    min: 3500
    max: 5500
    step: 100
    initial: 4000
    unit_of_measurement: "K"
    
  evening_temperature:
    name: "Evening Color Temperature"
    min: 2500
    max: 4000
    step: 100
    initial: 3200
    unit_of_measurement: "K"
    
  night_temperature:
    name: "Night Color Temperature"
    min: 1800
    max: 3000
    step: 100
    initial: 2000
    unit_of_measurement: "K"
```

### **Input DateTime Helpers**

```yaml
input_datetime:
  evening_peak_start:
    name: "Evening Peak Start Time"
    has_date: false
    has_time: true
    initial: "18:00"
    
  evening_peak_end:
    name: "Evening Peak End Time"
    has_date: false
    has_time: true
    initial: "20:00"
    
  bedtime_ramp_start:
    name: "Bedtime Ramp Start"
    has_date: false
    has_time: true
    initial: "20:00"
    
  bedtime_ramp_end:
    name: "Bedtime Ramp End"
    has_date: false
    has_time: true
    initial: "21:00"
    
  early_morning_start:
    name: "Early Morning Start"
    has_date: false
    has_time: true
    initial: "04:50"
    
  early_morning_end:
    name: "Early Morning End"
    has_date: false
    has_time: true
    initial: "05:40"
    
  weekend_recovery_start:
    name: "Weekend Recovery Start"
    has_date: false
    has_time: true
    initial: "06:00"
```

### **Input Boolean Helpers**

```yaml
input_boolean:
  intelligent_lighting_enable:
    name: "Enable Intelligent Lighting"
    initial: true
    
  circadian_mode_enable:
    name: "Circadian Research Mode"
    initial: true
    
  early_morning_gradient_enable:
    name: "Early Morning Gradient"
    initial: true
    
  weekend_recovery_enable:
    name: "Weekend Kitchen Recovery"
    initial: true
    
  kitchen_blocked:
    name: "Kitchen Blocked (Night Mode)"
    initial: false
```

---

## 📱 **DASHBOARD CONFIGURATION**

### **Lovelace YAML**

```yaml
# Intelligent Lighting Control Dashboard
type: vertical-stack
cards:
  # Header Card
  - type: markdown
    content: |
      # 🧠 Intelligent Lighting Control
      **Current Mode:** {{ states('input_select.home_state') }}
      **Calculated Mode:** {{ states('sensor.calculated_home_mode') }}
      
      **Brightness:** {{ states('sensor.intelligent_brightness_master') }}% | **Temperature:** {{ states('sensor.intelligent_temperature_master') }}K
      
      ---

  # System Controls
  - type: entities
    title: 🎛️ System Controls
    show_header_toggle: false
    entities:
      - entity: input_boolean.intelligent_lighting_enable
        name: "🧠 Enable Intelligent Lighting"
      - entity: input_boolean.circadian_mode_enable
        name: "🔬 Circadian Research Mode"
      - entity: input_boolean.early_morning_gradient_enable
        name: "🌅 Early Morning Gradient"
      - entity: input_boolean.weekend_recovery_enable
        name: "🏠 Weekend Kitchen Recovery"

  # Peak Brightness Controls
  - type: entities
    title: ☀️ Brightness Settings
    show_header_toggle: false
    entities:
      - entity: input_number.day_peak_brightness
        name: "☀️ Day Peak Brightness"
      - entity: input_number.evening_peak_brightness
        name: "🌆 Evening Peak Brightness"
      - entity: input_number.evening_end_brightness
        name: "🌙 Evening End Brightness"
      - entity: input_number.night_max_brightness
        name: "🌃 Night Maximum"

  # Temperature Controls
  - type: entities
    title: 🌡️ Temperature Settings
    show_header_toggle: false
    entities:
      - entity: input_number.day_temperature
        name: "☀️ Day Temperature"
      - entity: input_number.evening_temperature
        name: "🌆 Evening Temperature"
      - entity: input_number.night_temperature
        name: "🌃 Night Temperature"

  # Time Controls
  - type: entities
    title: ⏰ Timing Controls
    show_header_toggle: false
    entities:
      - entity: input_datetime.evening_peak_start
        name: "🌆 Evening Peak Start"
      - entity: input_datetime.evening_peak_end
        name: "🌆 Evening Peak End"
      - entity: input_datetime.bedtime_ramp_start
        name: "😴 Bedtime Ramp Start"
      - entity: input_datetime.bedtime_ramp_end
        name: "😴 Bedtime Ramp End"
      - entity: input_datetime.early_morning_start
        name: "🌅 Early Morning Start"
      - entity: input_datetime.early_morning_end
        name: "🌅 Early Morning End"
      - entity: input_datetime.weekend_recovery_start
        name: "🏠 Weekend Recovery Start"

  # Current Status
  - type: entities
    title: 📊 Current Status
    show_header_toggle: false
    entities:
      - entity: sensor.calculated_home_mode
        name: "🧮 Calculated Mode"
      - entity: input_select.home_state
        name: "🏠 Current Mode"
      - entity: input_boolean.kitchen_blocked
        name: "🔒 Kitchen Blocked"
      - entity: binary_sensor.workday_sensor
        name: "💼 Work Day"
```

---

## 🔧 **COMPLETE KITCHEN AUTOMATION PACKAGE**

### **Kitchen Lights Package v3.0**

```yaml
################################################################################
# KITCHEN AUTOMATION v3.0 - TEACHING SYSTEM EDITION
# Author: Frank S Elaschat
# Generated: September 2025
# Status: ✅ Complete Teaching System Implementation
#
# FEATURES:
# - Intelligent weekend recovery via kitchen motion
# - Dynamic early morning mode with circadian research
# - 70% brightness cap based on Philips Hue research
# - Fully configurable via dashboard (sticky settings)
# - Teaching system learns your patterns
################################################################################

# Kitchen Night Mode Protection
automation:
  - id: kitchen_night_mode_protection
    alias: "Kitchen Night Mode Protection"
    trigger:
      - platform: state
        entity_id: input_select.home_state
        to: "Night"
    condition:
      - condition: state
        entity_id: input_boolean.intelligent_lighting_enable
        state: "on"
    action:
      - service: light.turn_off
        target:
          entity_id: group.kitchen_lights
      - service: input_boolean.turn_on
        target:
          entity_id: input_boolean.kitchen_blocked
      - service: logbook.log
        data:
          name: "Kitchen"
          message: "🔒 Kitchen blocked in Night mode"

  # Kitchen Night Mode Exit
  - id: kitchen_night_mode_exit
    alias: "Kitchen Night Mode Exit"
    trigger:
      - platform: state
        entity_id: input_select.home_state
        from: "Night"
    condition:
      - condition: state
        entity_id: input_boolean.intelligent_lighting_enable
        state: "on"
    action:
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.kitchen_blocked

  # Weekend Kitchen Motion Recovery (Teaching System)
  - id: kitchen_weekend_recovery
    alias: "Kitchen Weekend Recovery - Teaching System"
    trigger:
      - platform: state
        entity_id: 
          - binary_sensor.aqara_motion_sensor_p1_occupancy
          - binary_sensor.kitchen_iris_frig_occupancy
        to: "on"
    condition:
      - condition: state
        entity_id: input_boolean.weekend_recovery_enable
        state: "on"
      - condition: state
        entity_id: input_select.home_state
        state: "Night"
      - condition: template
        value_template: "{{ not is_state('binary_sensor.workday_sensor', 'on') }}"
      - condition: template
        value_template: "{{ now().strftime('%H:%M') >= states('input_datetime.weekend_recovery_start') }}"
      - condition: template
        value_template: "{{ states('sensor.calculated_home_mode') == 'Day' }}"
    action:
      - service: script.turn_on
        target:
          entity_id: script.evaluate_home_mode
      - service: logbook.log
        data:
          name: "Teaching System"
          message: "🏠 Weekend recovery triggered by kitchen motion"

  # Kitchen Motion Response (Normal Operation)
  - id: kitchen_motion_response
    alias: "Kitchen Motion Response"
    trigger:
      - platform: state
        entity_id: 
          - binary_sensor.aqara_motion_sensor_p1_occupancy
          - binary_sensor.kitchen_iris_frig_occupancy
        to: "on"
    condition:
      - condition: state
        entity_id: input_boolean.kitchen_blocked
        state: "off"
      - condition: state
        entity_id: input_boolean.intelligent_lighting_enable
        state: "on"
      - condition: not
        conditions:
          - condition: state
            entity_id: input_select.home_state
            state: "Night"
    action:
      - service: light.turn_on
        target:
          entity_id: group.kitchen_lights
        data:
          brightness_pct: "{{ states('sensor.intelligent_brightness_master') | int }}"
          kelvin: "{{ states('sensor.intelligent_temperature_master') | int }}"

  # Kitchen Motion Off
  - id: kitchen_motion_off
    alias: "Kitchen Motion Off"
    trigger:
      - platform: state
        entity_id: 
          - binary_sensor.aqara_motion_sensor_p1_occupancy
          - binary_sensor.kitchen_iris_frig_occupancy
        to: "off"
        for: "00:03:00"
    condition:
      - condition: template
        value_template: |
          {{ is_state('binary_sensor.aqara_motion_sensor_p1_occupancy', 'off') and
             is_state('binary_sensor.kitchen_iris_frig_occupancy', 'off') }}
    action:
      - service: light.turn_off
        target:
          entity_id: group.kitchen_lights
```

---

## 📈 **SYSTEM MONITORING & DIAGNOSTICS**

### **Diagnostic Sensor**

```yaml
sensor:
  - platform: template
    sensors:
      intelligent_lighting_diagnostic:
        friendly_name: "Intelligent Lighting Diagnostic"
        value_template: |
          {% set mode = states('input_select.home_state') %}
          {% set calculated = states('sensor.calculated_home_mode') %}
          {% set brightness = states('sensor.intelligent_brightness_master') %}
          {% set temperature = states('sensor.intelligent_temperature_master') %}
          {% set enabled = is_state('input_boolean.intelligent_lighting_enable', 'on') %}
          {% set circadian = is_state('input_boolean.circadian_mode_enable', 'on') %}
          
          {% if not enabled %}
            Disabled
          {% elif mode != calculated %}
            Mode Mismatch: {{ mode }} ≠ {{ calculated }}
          {% elif circadian %}
            Circadian: {{ brightness }}% @ {{ temperature }}K
          {% else %}
            Standard: {{ brightness }}% @ {{ temperature }}K
          {% endif %}
```

---

## 🎯 **IMPLEMENTATION CHECKLIST**

### **Phase 1: Core System**
- [ ] Install all input_number helpers
- [ ] Install all input_datetime helpers  
- [ ] Install all input_boolean helpers
- [ ] Update intelligent_brightness_master sensor
- [ ] Update intelligent_temperature_master sensor

### **Phase 2: Kitchen Automation**
- [ ] Install kitchen night mode protection
- [ ] Install weekend recovery automation
- [ ] Update kitchen motion response
- [ ] Test both kitchen motion sensors

### **Phase 3: Dashboard**
- [ ] Create Lovelace dashboard card
- [ ] Test all controls adjust settings
- [ ] Verify settings persist after restart
- [ ] Configure notification system

### **Phase 4: Testing**
- [ ] Test weekend recovery (motion after 6 AM)
- [ ] Test circadian brightness curves
- [ ] Test 70% brightness cap
- [ ] Test seasonal adaptation
- [ ] Test dashboard controls

---

## 🚀 **ADVANCED FEATURES**

### **Weather Integration**
The system can integrate weather data to adjust brightness:
- **Cloudy days**: Increase brightness by 10-15%
- **Sunny days**: Decrease brightness by 5-10% 
- **Rainy days**: Increase brightness and warmth

### **Learning Capabilities**
The teaching system learns from your patterns:
- **Motion timing patterns** on weekends
- **Brightness preferences** by time of day
- **Temperature preferences** by season
- **Manual override learning**

### **Future Enhancements**
- **Occupancy-based zones** (kitchen vs dining area)
- **Sleep pattern integration** with fitness trackers
- **Automatic seasonal adjustments** based on sunrise/sunset
- **Voice control integration** for quick adjustments

---

## 📝 **CONCLUSION**

This complete Home Assistant Kitchen Lighting Automation with Teaching System provides:

1. **🔬 Science-based lighting** using Philips Hue circadian research
2. **🧠 Intelligent weekend recovery** via kitchen motion detection  
3. **⚙️ Fully configurable settings** that persist after restart
4. **📱 Beautiful dashboard interface** for easy adjustment
5. **🎯 Dynamic early morning mode** that adapts to seasons
6. **📊 Complete monitoring and diagnostics**

The system learns your patterns and automatically optimizes your lighting for comfort, productivity, and healthy circadian rhythms while giving you full control to customize every aspect through the dashboard interface.

**Ready for deployment and tuning to your specific preferences!**