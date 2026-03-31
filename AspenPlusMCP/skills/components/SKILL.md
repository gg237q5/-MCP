---
name: components
description: Component configuration guides for defining chemical species in Aspen Plus.
---

# Component Configuration Skills

Guides for setting up chemical components in Aspen Plus models.

## Available Resources

| Resource | Description |
|----------|-------------|
| `COMPONENTS.md` | Component definition and CAS numbers |
| `ELECTROLYTE.md` | Electrolyte system setup (ionic species, Henry-Comps, Wizard) |

## Usage

```python
skills(category='components', name='COMPONENTS')
skills(category='components', name='ELECTROLYTE')
```

## Workflow

1. `create_inp_file` - Create input file with components
2. `open_aspen_plus` - Open the file
3. `get_components_list` - Verify components

> ⚠️ For electrolyte systems (e.g., MEA-CO2), use `elec_wizard` instead of `add_thermo_method`.
> Call `skills(category='components', name='ELECTROLYTE')` for the full guide.

