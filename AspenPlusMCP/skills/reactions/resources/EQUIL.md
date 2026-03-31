# EQUIL (Equilibrium) Reaction Setup

Equilibrium reactions rely on chemical equilibrium constants defined by temperature-dependent equations.

## Required Parameters

- `REACTYPE\n`: Set to `"EQUIL"`

> [!TIP]
> **Always use `get_reaction_input_specifications`**!
> If you are unsure what the exact parameter path string is for a specific field, call `get_reaction_input_specifications(reac_set="YOUR-SET")`. It will dump the complete list of valid paths (e.g., `EQ-CON\1\A`) that you can copy and use in `set_reaction_input_specifications`.
