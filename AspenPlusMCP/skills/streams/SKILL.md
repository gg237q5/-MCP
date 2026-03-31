---
name: streams
description: Stream configuration guides for material, heat, and work streams in Aspen Plus.
---

# Stream Configuration Skills

Setup guides for configuring Aspen Plus streams.

## Available Resources

| Resource | Description |
|----------|-------------|
| `MATERIAL.md` | Material stream setup (temperature, pressure, flow) |
| `OUTPUT.md` | Stream output conditions (post-simulation) |
| `RECYCLE.md` | Recycle stream configuration for tear convergence |

## Usage

```python
skills(category='streams', name='MATERIAL')
```

## Workflow

1. `add_stream` - Create stream
2. `connect_block_stream` - Connect to block ports
3. `get_stream_input_conditions_list` - Query available specs
4. `unit_list` - Get unit indices
5. `set_stream_input_conditions` - Set values
