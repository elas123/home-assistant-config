"""
Mock PyScript environment for testing PyScript files outside Home Assistant.
This provides the necessary decorators and objects used in PyScript.
"""
import logging
from unittest.mock import Mock
from datetime import datetime
import sys
import os

# Mock logger
class MockLogger:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('pyscript')
    
    def info(self, msg):
        self.logger.info(msg)
    
    def error(self, msg):
        self.logger.error(msg)
    
    def warning(self, msg):
        self.logger.warning(msg)

# Mock state object
class MockState:
    def __init__(self):
        self._states = {
            'input_boolean.pyscript_auto_validation': 'off',
            'input_boolean.run_diagnostics_tests': 'off',
            'input_boolean.run_timing_tests': 'off',
            'input_select.home_state': 'Day',  # Add default day mode
            'light.kitchen_main_lights': 'off',
            'light.sink_wled': 'off',
            'light.frig_strip': 'off',
        }
        self._attributes = {}
    
    def get(self, entity_id, default=None):
        return self._states.get(entity_id, default)
    
    def set(self, entity_id, value):
        self._states[entity_id] = value
    
    def getattr(self, entity_id):
        """Get entity attributes."""
        return self._attributes.get(entity_id, {})
    
    def exist(self, entity_id):
        """Check if entity exists."""
        return entity_id in self._states

# Mock service object with proper call method
class MockService:
    def call(self, domain, service_name, **kwargs):
        print(f"Service call: {domain}.{service_name} with {kwargs}")
        return True
    
    def __call__(self, domain_service, **kwargs):
        """Make service object callable for direct service calls."""
        if '.' in domain_service:
            domain, service_name = domain_service.split('.', 1)
            return self.call(domain, service_name, **kwargs)
        return True

# Mock task object
class MockTask:
    def sleep(self, seconds):
        import time
        time.sleep(seconds)

# Create mock objects
log = MockLogger()
state = MockState()
service_obj = MockService()
task = MockTask()

# Mock decorators
def service_decorator(service_name=None):
    def decorator(func):
        func._pyscript_service = service_name
        return func
    return decorator

def state_trigger(*args, **kwargs):
    def decorator(func):
        func._pyscript_state_trigger = args
        return func
    return decorator

def time_trigger(trigger_spec):
    def decorator(func):
        func._pyscript_time_trigger = trigger_spec
        return func
    return decorator

# Make decorators and objects available globally
service = service_decorator
