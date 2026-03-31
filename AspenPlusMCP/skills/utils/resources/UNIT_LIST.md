# Unit List Query

## Overview

Use `unit_list` to query Aspen Plus unit system. Essential for setting correct unit indices when configuring streams and blocks.

## Usage

### List All Unit Categories
```python
unit_list()
```
Returns all available unit categories with their indices.

### List Units in a Category
```python
unit_list(item=[7])  # All units in category 7 (Temperature)
```

### Get Specific Unit Name
```python
unit_list(item=[7, 1])  # Unit at index 1 in category 7
```

## Common Unit Categories

| Index | Category | Common Units |
|-------|----------|--------------|
| 2 | Pressure | bar, atm, psi, Pa, kPa |
| 3 | Molar flow | kmol/hr, mol/s |
| 4 | Mass flow | kg/hr, lb/hr |
| 7 | Temperature | C, K, F, R |
| 8 | Heat duty | kW, MW, Btu/hr |

## Workflow

1. **CRITICAL: Call `unit_list()` FIRST to view all available categories and their indices.**
2. Find the expected `Unit Category` (e.g., Temperature, Pressure)
3. Call `unit_list(item=[category_index])` to see available units in that category
4. Use the correct unit index when setting values

## Example

```python
# 1. Query spec to get unit category (e.g., category 7 for temperature)
get_stream_input_conditions_list('FEED', specification_names=['TEMP\\MIXED'])

# 2. List units in that category
unit_list(item=[7])
# Returns: {1: 'C', 2: 'K', 3: 'F', 4: 'R'}

# 3. Set with correct unit index
set_stream_input_conditions(
    stream_name='FEED',
    specifications_dict={'TEMP\\MIXED': {'value': 298.15, 'unit': 2}}  # Kelvin
)
```
