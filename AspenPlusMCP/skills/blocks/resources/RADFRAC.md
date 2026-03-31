# RADFRAC Distillation Column Setup

## Required Steps

### 1. Connect Streams
| Port | Description |
|------|-------------|
| F(IN) | Feed |
| VD(OUT) | Vapor distillate |
| LD(OUT) | Liquid distillate |
| B(OUT) | Bottoms product |

### 2. Set Number of Stages
```python
{'NSTAGE': 20}
```

### 3. Set Feed Stage
```python
{'FEED_STAGE\\FEED': 10}  # FEED is the feed stream name
```

### 4. Set TWO Design Specs (choose one combination)

**Combination A: Reflux Ratio + Bottoms Rate**
```python
{
    'BASIS_RR': {'value': 2.0, 'basis': 'MOLE'},
    'BASIS_B': {'value': 50, 'unit': 3, 'basis': 'MOLE'}
}
```

**Combination B: Reflux Ratio + D:F Ratio**
```python
{
    'BASIS_RR': 2.0,
    'D:F': {'value': 0.5, 'basis': 'MOLE'}
}
```

## BASIS Configuration ⚠️

### Product Specs (BASIS_D, BASIS_B, D:F, B:F)
- **Must specify basis parameter**
- Valid values: `'MASS'`, `'MOLE'`, `'VOLUME'`
- Example:
```python
{'D:F': {'value': 0.5, 'basis': 'MOLE'}}
{'BASIS_D': {'value': 50, 'unit': 3, 'basis': 'MASS'}}
```

### Reflux Ratio (BASIS_RR, BASIS_BR)
- Specify basis when using mass or volume basis
- Example:
```python
{'BASIS_RR': {'value': 2.0, 'basis': 'MOLE'}}
```

### 5. Set Condenser Type (Required)
```python
{'CONDENSER': 'TOTAL'}  # Options: 'TOTAL', 'PARTIAL-V', 'PARTIAL-VL', 'NONE'
```

### 6. Set Pressure (Required)
```python
{'PRES1': 1.0}  # Top stage pressure (bar)
```

## Optional Parameters

| Parameter | Description |
|-----------|-------------|
| DP_STAGE | Pressure drop per stage |
| MAXOL | Maximum outer loop iterations (default: 25, maximum:200) |

> [!TIP]
> **For better convergence**, set `MAXOL` to maximum value:
> ```python
> {'MAXOL': 200}
> ```
> This allows more iterations for complex columns or difficult separations.

## ⚠️ Common Errors

1. **Forgetting to connect all required ports**
2. **Setting only one design spec** (need two)
3. **Product specs without basis**

## Recommended Workflow

1. `get_block_connections('COL1')` - Check connections
2. `connect_block_stream(...)` - Connect streams
3. `get_block_input_specifications('COL1')` - Query specs
4. `unit_list()` - Query units
5. `set_block_input_specifications(...)` - Set values
