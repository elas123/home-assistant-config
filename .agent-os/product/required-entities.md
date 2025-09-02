# Required Entities

> Bare-necessities manifest of external entities that must exist in Home Assistant
> for this project to function. Does not include helpers (`input_*`, template
> sensors, or groups). If any of these are missing, automations may break.

---

## Phones / Presence
- device_tracker.iphone15
- device_tracker.work_iphone

---

## Weather
- weather.pirateweather

---

## Lights & Switches
- light.closet
- light.hallway
- light.laundry_room
- light.kitchen_main_lights
- light.lamp_1
- light.lamp_2
- light.bathroom_2_main_lights
- light.living_room_lamps
- light.sink_wled
- light.frig_strip
- light.smart_switch_1
- light.smart_switch_2
- switch.porch

---

## Motion Sensors
- binary_sensor.aqara_motion_sensor_p1_occupancy
- binary_sensor.kitchen_iris_frig_occupancy
- binary_sensor.hallway_iris_occupancy
- binary_sensor.laundry_iris_occupancy
- binary_sensor.bathroom_iris_occupancy
- binary_sensor.bathroom_x_occupancy
- binary_sensor.bathroom_motion_combined
- binary_sensor.bedroom_x_occupancy

---

## Door / Contact
- binary_sensor.bathroom_contact_contact
- binary_sensor.front_door_contact_contact

---

## Lock
- lock.aqara_smart_lock_u100_lock

---

## Media
- media_player.bedroom

---

## WLED Presets / Selects
- select.sink_wled_preset
- select.frig_strip_preset
