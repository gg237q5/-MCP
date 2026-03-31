# MATERIAL Stream Setup

> [!TIP]
> **Recycle Streams**: If your process contains recycle loops, you **MUST** configure initial estimates for tear streams. See [RECYCLE](RECYCLE.md) for details.

## Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| TEMP\MIXED | Temperature | `temp=25` or `{'TEMP\\MIXED': 25}` |
| PRES\MIXED | Pressure | `pres=1.01325` or `{'PRES\\MIXED': 1.01325}` |
| Flow | Choose one | TOTFLOW or FLOW |

## State Variable Specification (MIXED_SPEC\MIXED)

When specifying stream conditions, you must choose one of the following **specification pairs**:

| Pair | Variables | Description |
|------|-----------|-------------|
| **TP** | Temperature + Pressure | Standard specification for known T and P |
| **PV** | Pressure + Vapor Fraction | Saturation at a given Pressure |
| **TV** | Temperature + Vapor Fraction | Saturation at a given Temperature |

### TP (Temperature & Pressure) - Normal Usage
Use when you know the exact temperature and pressure of the stream.
```python
# Default: MIXED_SPEC\MIXED is automatically set to "TP"
set_stream_input_conditions('FEED', temp=25, pres=1.01325)

# Explicit specification (optional)
set_stream_input_conditions('FEED', temp=25, pres=1.01325, 
    specifications_dict={'MIXED_SPEC\\MIXED': 'TP'})
```

### PV (Pressure & Vapor Fraction) - Saturation at P
Use to define a **saturated liquid** or **saturated vapor** at a specific pressure.
- `VAP-FRAC = 0.01` → Saturated Liquid (Bubble Point)
- `VAP-FRAC = 1` → Saturated Vapor (Dew Point)
```python
# Saturated liquid at 1 atm
set_stream_input_conditions('FEED', pres=1.01325, 
    specifications_dict={
        'MIXED_SPEC\\MIXED': 'PV',
        'VFRAC\\MIXED': 0
    })

# Saturated vapor at 2 bar
set_stream_input_conditions('FEED', pres=2.0, 
    specifications_dict={
        'MIXED_SPEC\\MIXED': 'PV',
        'VFRAC\\MIXED': 1
    })
```

### TV (Temperature & Vapor Fraction) - Saturation at T
Use to define a **saturated liquid** or **saturated vapor** at a specific temperature.
```python
# Saturated liquid at 80°C
set_stream_input_conditions('FEED', temp=80, 
    specifications_dict={
        'MIXED_SPEC\\MIXED': 'TV',
        'VFRAC\\MIXED': 0
    })

# Saturated vapor at 100°C
set_stream_input_conditions('FEED', temp=100, 
    specifications_dict={
        'MIXED_SPEC\\MIXED': 'TV',
        'VFRAC\\MIXED': 1
    })
```

## BASIS Configuration ⚠️

### TOTFLOW\MIXED (Total flow)
- **Must specify basis parameter**
- Valid values: `'MASS'`, `'MOLE'`, `'STDVOL'`
- Example:
```python
{'TOTFLOW\\MIXED': {'value': 100, 'unit': 3, 'basis': 'MASS'}}
```

### FLOW\MIXED\<COMPONENT> (Component flow/fraction)
- **Must specify basis parameter**
- Valid values:
  - Flow: `'MASS-FLOW'`, `'MOLE-FLOW'`, `'STDVOL-FLOW'`
  - Fraction: `'MASS-FRAC'`, `'MOLE-FRAC'`, `'STDVOL-FRAC'`
  - Concentration: `'MASS-CONC'`, `'MOLE-CONC'`
- Example:
```python
{'FLOW\\MIXED\\WATER': {'value': 0.5, 'basis': 'MOLE-FRAC'}}
```

## ⚠️ Common Errors

1. **Do NOT set `BASIS\MIXED` or `FLOWBASE\MIXED` directly**
   - These are display-only nodes, setting them has no effect!
   - Use the `basis` parameter when setting flow values

2. **Spec names must match exactly**
   - Use `get_stream_input_conditions_list` to get correct names

## Configuration Formats

> [!IMPORTANT]
> **Before specifying units**, you **MUST** use `unit_list()` to query the correct category index and unit index!
> - `unit_list()` → View all unit categories
> - `unit_list(item=[n])` → List units in category n
> - `unit_list(item=[n, m])` → Get unit name for index m in category n

```python
# 1. Simple value (uses default unit)
{'TEMP\\MIXED': 25}

# 2. With unit - MUST query unit_list() first!
#    Example: unit_list(item=[7]) → Temperature units
#             unit_list(item=[7, 0]) → 'C' (Celsius)
{'TEMP\\MIXED': {'value': 25, 'unit': 0}}  # unit 0 = 'C'

# 3. With basis
{'TOTFLOW\\MIXED': {'value': 100, 'basis': 'MOLE'}}

# 4. Full configuration with unit and basis
#    Example: unit_list(item=[3]) → Mass flow units
#             unit_list(item=[3, 0]) → 'kg/hr'
{'FLOW\\MIXED\\WATER': {'value': 50, 'unit': 0, 'basis': 'MASS-FLOW'}}  # unit 0 = 'kg/hr'

# 5. Pressure example
#    Example: unit_list(item=[4]) → Pressure units
#             unit_list(item=[4, 0]) → 'bar'
{'PRES\\MIXED': {'value': 1.01325, 'unit': 0}}  # unit 0 = 'bar'
```

## Recommended Workflow

> [!CAUTION]
> **Never guess unit indices!** Every unit specification **MUST** be verified using `unit_list()` before setting values.

### Step-by-Step Example

```python
# Step 1: Query available specifications
get_stream_input_conditions_list('FEED')

# Step 2: Query unit categories
unit_list()  # → Returns all available unit categories with indices

# Step 3: Query specific units for EACH parameter you will set
unit_list(item=[7])      # → Temperature units (category 7)
unit_list(item=[7, 0])   # → 'C' (Celsius, index 0)

unit_list(item=[4])      # → Pressure units (category 4)  
unit_list(item=[4, 0])   # → 'bar' (index 0)

unit_list(item=[3])      # → Mass flow units (category 3)
unit_list(item=[3, 0])   # → 'kg/hr' (index 0)

# Step 4: Set values with verified unit indices
set_stream_input_conditions('FEED', 
    temp=25,      # Default: °C
    pres=1.01325, # Default: bar
    specifications_dict={
        'TOTFLOW\\MIXED': {'value': 100, 'unit': 0, 'basis': 'MASS'},  # kg/hr
        'FLOW\\MIXED\\WATER': {'value': 0.5, 'basis': 'MOLE-FRAC'},
        'FLOW\\MIXED\\ETHANOL': {'value': 0.5, 'basis': 'MOLE-FRAC'}
    })
```

### Summary
| Step | Tool | Purpose |
|------|------|---------|
| 1 | `get_stream_input_conditions_list` | Query available spec names |
| 2 | `unit_list()` | View all unit categories |
| 3 | `unit_list(item=[n])` | **Check units for EACH parameter** |
| 4 | `set_stream_input_conditions` | Set values with verified indices |
