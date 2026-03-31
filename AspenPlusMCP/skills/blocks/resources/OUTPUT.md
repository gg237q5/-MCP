# Block Output Specifications

## Overview

After running a simulation, use `get_block_output_specifications` to retrieve calculated results for a block.

## Prerequisites

- Simulation must be run successfully first
- Use `run_simulation`, `run_and_report`, or `check_and_run`

## Usage

```python
# Quick view - list all available output specs
get_block_output_specifications(block_name='COL1')

# Detailed view - get specific spec values
get_block_output_specifications(
    block_name='COL1',
    specification_names=['MOLE_RR', 'MOLE_BR', 'TOP_TEMP', 'BOT_TEMP']
)
```

## Common Output Specs by Block Type

### RADFRAC (Distillation)
| Spec | Description |
|------|-------------|
| MOLE_RR | Actual molar reflux ratio |
| MOLE_BR | Actual molar boilup ratio |
| TOP_TEMP | Top stage temperature |
| BOT_TEMP | Bottom stage temperature |
| COND_DUTY | Condenser duty |
| REB_DUTY | Reboiler duty |

### HEATER
| Spec | Description |
|------|-------------|
| QCALC | Calculated heat duty |
| TOUT | Outlet temperature |
| VFRAC | Vapor fraction |

### FLASH2
| Spec | Description |
|------|-------------|
| QCALC | Calculated heat duty |
| VFRAC | Vapor fraction |
| TEMP | Flash temperature |

## Workflow

```
1. run_simulation() or check_and_run()
2. get_block_output_specifications(block_name='BLOCK')
3. Analyze results
```
