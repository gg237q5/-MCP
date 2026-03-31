# FLASH2 Flash Drum Setup

## Required Steps

### 1. Connect Streams
| Port | Description |
|------|-------------|
| F(IN) | Feed |
| V(OUT) | Vapor outlet |
| L(OUT) | Liquid outlet |

### 2. Set Operating Conditions (choose one combination)

**Combination A: Temperature + Pressure**
```python
{
    'TEMP': 80,
    'PRES': 1.0
}
```

**Combination B: Vapor Fraction + Pressure**
```python
{
    'VFRAC': 0.5,
    'PRES': 1.0
}
```

**Combination C: Duty + Pressure**
```python
{
    'DUTY': 0,
    'PRES': 1.0
}
```

## Recommended Workflow

1. `get_block_ports('FLASH')` - Query ports
2. `connect_block_stream(...)` - Connect streams
3. `set_block_input_specifications(...)` - Set values
