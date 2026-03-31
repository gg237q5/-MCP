# Recycle Stream Configuration

> [!IMPORTANT]
> **For processes with recycle loops, you MUST specify initial operating conditions for the tear stream (S1) - the MIXER output that feeds into the first process block.**

## Which Stream Needs Initial Conditions?

The stream that needs initial conditions is **S1** - the output of the MIXER that combines MAKEUP (fresh feed) and RECYCLE streams. This is the **tear stream** entering the first process block.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           Recycle Loop                                   │
│                                                                          │
│  MAKEUP     ┌───────┐                 ┌─────────┐         ┌─────────┐   │
│    │        │       │      S1         │         │         │         │   │
│    ▼        │       │  (Configure!)   │         │         │         │   │
│  ─────►─────│ MIXER │────────────────►│ Block A │──S2────►│ Block B │──►│
│             │       │                 │         │         │         │   │
│             └───────┘                 └─────────┘         └─────────┘   │
│                 ▲                                               │       │
│                 │                                               │       │
│                 └──────────────────── RECYCLE ◄─────────────────┘       │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

> [!CAUTION]
> **Configure stream S1** (MIXER output → Block A input):
> - This is the **tear stream** where Aspen Plus breaks the recycle loop
> - It is the stream **entering the first process block** after mixing with recycle
> - Initial conditions are required because Aspen cannot calculate S1 before RECYCLE is known

## Why Recycle Streams Need Initial Conditions

Aspen Plus uses a **sequential modular** approach for flowsheet calculation. When a recycle stream exists, the simulator must:
1. **Tear** the recycle loop at **S1** (MIXER output → Block A input)
2. **Assume** initial values for S1 (temperature, pressure, flow, composition)
3. **Iterate** until the assumed S1 values match the calculated values from MIXER

Without proper initial estimates, the simulation may:
- Fail to converge
- Converge to an incorrect solution
- Take excessive iterations

## Best Practices

1. **Always specify** Temperature, Pressure, and approximate Flow for the tear stream (S1)
2. Use **reasonable estimates** based on expected mixed stream conditions
3. For **vapor-liquid systems**, estimate the phase (use MIXED_SPEC: TP, PV, or TV)
4. **Consider both MAKEUP and RECYCLE contributions** when estimating S1 conditions

## Example: Pressure-Swing Distillation

In pressure-swing distillation, the distillate from one column is recycled to another column at different pressure.

- **MAKEUP**: Fresh feed entering MIXER
- **RECYCLE**: Distillate from Column 2 (High P) returning to MIXER
- **S1**: MIXER output → Column 1 (Low P) input ← **Configure this!**

```python
# S1 = MIXER output → Column 1 input (tear stream)
set_stream_input_conditions(
    'S1',
    temp=80,           # Estimated mixed temperature (°C)
    pres=1.01325,      # Low pressure column feed (bar)
    specifications_dict={
        'TOTFLOW\\MIXED': {'value': 150, 'basis': 'MOLE'}  # MAKEUP + RECYCLE (kmol/hr)
    }
)
```

## Example: Extractive Distillation (Solvent Recycle)

In extractive distillation, a solvent is used to break the azeotrope and recycled from recovery column.

- **MAKEUP**: Fresh solvent entering MIXER
- **RECYCLE**: Recovered solvent from Solvent Recovery Column returning to MIXER
- **S1**: MIXER output → Extractive Column input ← **Configure this!**

```python
# S1 = MIXER output → Extractive Column input (tear stream)
set_stream_input_conditions(
    'S1',
    temp=120,          # Estimated mixed solvent temperature (°C)
    pres=1.01325,      # Operating pressure (bar)
    specifications_dict={
        'TOTFLOW\\MIXED': {'value': 250, 'basis': 'MOLE'}  # MAKEUP + RECYCLE (kmol/hr)
    }
)
```

## Convergence Tips

| Issue | Solution |
|-------|----------|
| Slow convergence | Improve S1 initial estimates based on expected mixed stream conditions |
| No convergence | Check if S1 has proper phase specification (MIXED_SPEC) |
| Oscillating | Adjust S1 estimates or try different convergence method |
| Large recycle ratio | Ensure S1 flow estimate accounts for both MAKEUP and RECYCLE |
