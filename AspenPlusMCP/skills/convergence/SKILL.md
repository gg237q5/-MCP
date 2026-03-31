---
name: convergence
description: Convergence settings guides for simulation loop tolerance and iteration limits.
---

# Convergence Configuration Skills

Setup guides for configuring Aspen Plus convergence settings.

## Available Resources

| Resource | Description |
|----------|-------------|
| `CONVERGENCE.md` | Convergence settings (TOL, WEG_MAXIT, etc.) |

For troubleshooting guides, see `skills(category='simulation', name='TROUBLESHOOTING')`.

## Usage

```python
skills(category='convergence', name='CONVERGENCE')
```

## Workflow

1. `get_input_convergence` - Query available specs
2. `set_input_convergence` - Set convergence parameters
3. `run_simulation` - Execute simulation

## Quick Reference

| Parameter | Default | Description |
|-----------|---------|-------------|
| TOL | 0.01 | Convergence tolerance |
| WEG_MAXIT | 5000 | Maximum Wegstein iterations |
