# HEATER Setup

## Required Steps

### 1. Connect Streams
| Port | Description |
|------|-------------|
| F(IN) | Feed |
| P(OUT) | Product outlet |

### 2. Set Operating Conditions (choose one)

**Option A: Specify Outlet Temperature**
```python
{'TEMP': 100}  # Outlet temperature in °C
```

**Option B: Specify Duty**
```python
{'DUTY': 1000}  # kW (positive=heating, negative=cooling)
```

## Optional Parameters

| Parameter | Description |
|-----------|-------------|
| PRES | Outlet pressure |
| PDROP | Pressure drop |
| VFRAC | Vapor fraction |

## Recommended Workflow

1. `connect_block_stream(...)` - Connect streams
2. `set_block_input_specifications(...)` - Set values
