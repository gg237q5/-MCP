# Stream Output Conditions

## Overview

After running a simulation, use `get_stream_output_conditions` to retrieve calculated stream results.

## Prerequisites

- Simulation must be run successfully first
- Use `run_simulation`, `run_and_report`, or `check_and_run`

## Usage

```python
# Quick view - list all available output conditions
get_stream_output_conditions(stream_name='DISTIL')

# Detailed view - get specific condition values
get_stream_output_conditions(
    stream_name='DISTIL',
    specification_names=['TEMP\\MIXED', 'PRES\\MIXED', 'MASSFLOW\\MIXED']
)
```

## Common Output Conditions

| Condition | Description |
|-----------|-------------|
| TEMP\MIXED | Temperature |
| PRES\MIXED | Pressure |
| MASSFLOW\MIXED | Total mass flow |
| MOLEFLOW\MIXED | Total molar flow |
| VOLFLOW\MIXED | Total volume flow |
| MASSFRAC\MIXED\<COMP> | Component mass fraction |
| MOLEFRAC\MIXED\<COMP> | Component mole fraction |
| ENTHALPY\MIXED | Stream enthalpy |
| ENTROPY\MIXED | Stream entropy |
| DENSITY\MIXED | Stream density |
| PROPMSG | Property Calculation Message |
| BLKMSG | Block Convergence Message |

## Workflow

```
1. run_simulation() or check_and_run()
2. get_stream_output_conditions(stream_name='STREAM')
3. Analyze results
```

## Example

```python
# After simulation, check product stream
get_stream_output_conditions(
    stream_name='PRODUCT',
    specification_names=[
        'TEMP\\MIXED',
        'MOLEFRAC\\MIXED\\ETHANOL',
        'MOLEFRAC\\MIXED\\WATER'
    ]
)
```
