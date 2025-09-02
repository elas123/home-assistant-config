# Database Schema

This is the database schema implementation for the spec detailed in @.agent-os/specs/2025-09-02-kitchen-teaching-system/spec.md

> Created: 2025-09-02
> Version: 3.0.0 (Simplified - No Schema Changes Required)

## Schema Changes

### No Database Changes Required

The timing learning enhancement leverages the existing `adaptive_learning` table infrastructure without any schema modifications. This approach reuses proven data patterns and storage mechanisms.

**Current Schema** (already exists):
```sql
CREATE TABLE IF NOT EXISTS adaptive_learning (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room TEXT NOT NULL,
    condition_key TEXT NOT NULL,
    brightness_percent INTEGER NOT NULL,
    temperature_kelvin INTEGER NULL,
    timestamp TEXT NOT NULL
);
```

**Teaching System Data Format:**
- **room**: `"routine_teaching"` (identifies teaching system entries)
- **condition_key**: `"{day_type}_{season}_{week}"` (e.g., "work_winter_36") 
- **brightness_percent**: Encoded completion time in minutes since midnight (e.g., 445 for 7:25 AM)
- **temperature_kelvin**: Confidence score * 1000 (e.g., 850 for 85% confidence)
- **timestamp**: Standard timestamp of when routine ended

### Add Prediction Tracking

Store prediction accuracy using the same table with a different room identifier:

- **room**: `"routine_predictions"`
- **condition_key**: `"{prediction_date}_{day_type}"` 
- **brightness_percent**: Predicted time in minutes since midnight
- **temperature_kelvin**: Accuracy score * 1000 (actual vs predicted difference)
- **timestamp**: When prediction was made

### Data Migration

No schema migration required - uses existing table structure and `als_memory_manager.py` functions.

## Implementation Strategy

### Reuse Existing Functions

The teaching system will leverage existing `als_memory_manager.py` functions:

- **`_get_db_connection()`**: Use existing SQLite connection handling
- **Data insertion**: Adapt existing insertion patterns for routine data
- **Query functions**: Build on existing database query infrastructure
- **Cleanup routines**: Extend existing data lifecycle management

### Example Data Entries

**Routine Completion Entry:**
```python
# Store routine completion at 7:25 AM on a winter work day with 85% confidence
room = "routine_teaching"
condition_key = "work_winter_36"  # work day, winter, week 36
brightness_percent = 445  # 7:25 AM = 445 minutes since midnight
temperature_kelvin = 850  # 85% confidence = 850
timestamp = "2025-01-15 07:25:00"
```

**Prediction Accuracy Entry:**
```python 
# Store prediction accuracy for a specific day
room = "routine_predictions"
condition_key = "2025-01-15_work"
brightness_percent = 440  # Predicted 7:20 AM = 440 minutes
temperature_kelvin = 5000  # 5 minute difference = 5000 (error in seconds)
timestamp = "2025-01-15 05:00:00"  # When prediction was made
```

## Schema Specifications

### Data Encoding Format
- **Completion Time Encoding**: Minutes since midnight (0-1439)
  - 7:25 AM = (7 * 60) + 25 = 445 minutes
  - Allows integer storage and easy time calculations
- **Confidence Score Encoding**: Percentage * 10 (0-1000)
  - 85.5% confidence = 855 in temperature_kelvin field
- **Condition Key Format**: `{day_type}_{season}_{week_number}`
  - Enables pattern grouping and seasonal analysis

### Retention Policy
- **routine_teaching**: Retain 180 days using existing cleanup mechanisms
- **routine_predictions**: Retain 90 days for accuracy tracking
- Leverage existing `als_memory_manager.py` cleanup routines with room-based filtering

## Schema Rationale

### Reuse Existing Infrastructure
- **No Schema Changes**: Avoids database migrations and compatibility issues
- **Proven Reliability**: Uses battle-tested storage and retrieval functions
- **Consistent Patterns**: Maintains same data handling approaches as adaptive lighting
- **Unified Management**: Single point of database management for all learning systems

### Efficient Storage
- **Compact Format**: Encodes complex data in existing integer fields
- **Query Performance**: Uses existing indexes on room and timestamp fields
- **Data Relationships**: Maintains logical separation via room identifiers