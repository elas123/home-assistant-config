// Room configuration based on your Home Assistant setup
export const ROOMS = [
  {
    id: 'bedroom',
    name: 'Bedroom',
    icon: 'bed',
    color: '#4A90E2',
    entities: {
      brightness_sensor: 'sensor.bedroom_intelligent_brightness',
      temperature_sensor: 'sensor.intelligent_temperature_bedroom',
      learned_brightness: 'sensor.learned_brightness_bedroom',
      lights: ['light.lamp_1', 'light.lamp_2'],
      custom_settings: 'input_boolean.bedroom_use_custom_settings'
    },
    hasLearning: true,
    description: 'Master bedroom with adaptive learning'
  },
  {
    id: 'living_room',
    name: 'Living Room',
    icon: 'sofa',
    color: '#7ED321',
    entities: {
      brightness_sensor: 'sensor.intelligent_brightness_living_room',
      temperature_sensor: 'sensor.intelligent_temperature_living_room',
      lights: ['light.living_room_main'],
      custom_settings: 'input_boolean.living_room_use_custom_settings'
    },
    hasLearning: false,
    description: 'Main living area'
  },
  {
    id: 'kitchen',
    name: 'Kitchen',
    icon: 'chef-hat',
    color: '#F5A623',
    entities: {
      brightness_sensor: 'sensor.intelligent_brightness_kitchen',
      temperature_sensor: 'sensor.intelligent_temperature_master',
      lights: ['light.kitchen_wled', 'light.kitchen_under_cabinet'],
      motion_sensors: ['binary_sensor.aqara_motion_sensor_p1_occupancy', 'binary_sensor.kitchen_iris_frig_occupancy']
    },
    hasLearning: false,
    description: 'Kitchen with motion automation'
  },
  {
    id: 'bathroom',
    name: 'Bathroom',
    icon: 'shower',
    color: '#50E3C2',
    entities: {
      brightness_sensor: 'sensor.bathroom_intelligent_brightness',
      temperature_sensor: 'sensor.intelligent_temperature_master',
      learned_brightness: 'sensor.learned_brightness_bathroom',
      lights: ['light.bathroom_main'],
      hold_mode: 'input_boolean.bathroom_100_percent_hold',
      override_mode: 'input_boolean.bathroom_adaptive_override'
    },
    hasLearning: true,
    description: 'Bathroom with door-closed hold mode'
  },
  {
    id: 'hallway',
    name: 'Hallway',
    icon: 'floor-lamp',
    color: '#9013FE',
    entities: {
      brightness_sensor: 'sensor.intelligent_brightness_hallway',
      temperature_sensor: 'sensor.intelligent_temperature_master',
      lights: ['light.hallway']
    },
    hasLearning: false,
    description: 'Hallway passage lighting'
  },
  {
    id: 'laundry',
    name: 'Laundry',
    icon: 'washing-machine',
    color: '#FF6B6B',
    entities: {
      brightness_sensor: 'sensor.intelligent_brightness_laundry',
      temperature_sensor: 'sensor.intelligent_temperature_master',
      lights: ['light.laundry']
    },
    hasLearning: false,
    description: 'Utility room lighting'
  },
  {
    id: 'closet',
    name: 'Closet',
    icon: 'hanger',
    color: '#FF9500',
    entities: {
      lights: ['light.closet'],
      temperature_sensor: 'sensor.intelligent_temperature_master'
    },
    hasLearning: false,
    description: 'Walk-in closet'
  }
];

// Home Assistant base URL - update this to your actual HA instance
export const HA_CONFIG = {
  baseUrl: 'http://192.168.10.153:8123',
  longLivedToken: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIxZjE1MGVlMjc0ODc0YTVhOWQ2MzBmZjZhMTA3NDA3ZCIsImlhdCI6MTc1NjkzODk2MSwiZXhwIjoyMDcyMjk4OTYxfQ.O5UTmlzju3JaMhbK-Y2VlKoOlgWq4vSwhoj7QYnraNE',
};

// Brightness presets
export const BRIGHTNESS_PRESETS = [
  { label: '5%', value: 5 },
  { label: '10%', value: 10 },
  { label: '20%', value: 20 },
  { label: '30%', value: 30 },
  { label: '50%', value: 50 },
  { label: '75%', value: 75 },
  { label: '100%', value: 100 }
];

// Temperature presets (in Kelvin)
export const TEMPERATURE_PRESETS = [
  { label: 'Warm (2000K)', value: 2000, color: '#FF8C00' },
  { label: 'Cozy (2700K)', value: 2700, color: '#FFA500' },
  { label: 'Neutral (3000K)', value: 3000, color: '#FFD700' },
  { label: 'Cool (4000K)', value: 4000, color: '#F0F8FF' },
  { label: 'Daylight (5000K)', value: 5000, color: '#E0F6FF' },
];