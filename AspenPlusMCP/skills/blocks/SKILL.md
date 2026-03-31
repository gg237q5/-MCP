---
name: blocks
description: Block configuration guides for Aspen Plus unit operations including distillation, flash, heater.
---

# Block Configuration Skills

Setup guides for configuring Aspen Plus unit operation blocks.

## Available Resources

| Resource | Description |
|----------|-------------|
| `RADFRAC.md` | Distillation column (RADFRAC) setup |
| `FLASH2.md` | Flash drum configuration |
| `HEATER.md` | Heater/Cooler settings |
| `OUTPUT.md` | Block output specifications (post-simulation) |

## Usage

```python
skills(category='blocks', name='RADFRAC')
skills(category='blocks', name='FLASH2')
skills(category='blocks', name='HEATER')
```

## Troubleshooting

For block convergence failures (iterations exceeded, tolerance not met), see `skills(category='simulation', name='TROUBLESHOOTING')`.

## Workflow

1. `add_block` - Create block
2. `get_block_ports` - Check available ports
3. `connect_block_stream` - Connect streams
4. `get_block_input_specifications` - Query specs
5. `set_block_input_specifications` - Set values
