# Electrolyte System Setup

## When to Use

Use this workflow when the process involves **ionic species or electrolyte reactions**, such as:

- Amine-based CO2 capture
- Acid-gas treating
- Acid-base neutralization processes
- Ionic liquid systems
- Any system requiring dissociation reactions in aqueous solution

> ⚠️ **Key Difference from Standard Workflow:**  
> Do NOT manually set thermodynamic method via `add_thermo_method` for electrolyte systems.  
> The `elec_wizard` will automatically configure:
> - Ionic species
> - Henry Components sets (Henry-Comps)
> - Thermodynamic property method
> - Electrolyte reaction chemistry

## Complete Workflow


1. `create_inp_file`        → Add MOLECULAR components only
      ↓
2. `open_aspen_plus`        → Open the .inp file
      ↓
3. `save_aspen_file_as`     → Save as .bkp (required for Wizard)
      ↓
4. `close_aspen` / `open_aspen_plus` / `show_aspen_gui`
      ↓
4.5 Confirm Wizard Options   → MUST notify user with chosen options
                               to get approval BEFORE execution.
      ↓
5. `elec_wizard`               → Run Electrolyte Wizard
                             (If it fails, simply re-run elec_wizard)
      ↓
6. Verify results         → Check components, Henry-Comps, properties


## Step-by-Step Example

### Step 1: Create input file with molecular components

```python
create_inp_file(
    file_path='D:\\path\\to\\model.inp',
    components=['H2O', 'CO2', 'C2H7NO', 'N2', 'O2'],
    cas_numbers=['7732-18-5', '124-38-9', '141-43-5', '7727-37-9', '7782-44-7']
)
```

### Steps 2-4: Open .inp, Save .bkp, Reopen .bkp, Show GUI

```python
# 1. Open .inp and save as .bkp
open_aspen_plus(file_path='D:\\path\\to\\model.inp')
save_aspen_file_as(filename='D:\\path\\to\\model.bkp')

# 2. Reopen .bkp for Wizard
close_aspen()
open_aspen_plus(file_path='D:\\path\\to\\model.bkp')
show_aspen_gui(visible=True)
```

### Step 4.5: Confirm Wizard Options

Before calling `elec_wizard`, you **MUST** explicitly ask the user to confirm the parameters you intend to use (e.g., `ref_state`, `reaction_opts`, etc.).
**DO NOT** execute the `elec_wizard` tool without the user's explicit consent on the configuration.

### Step 5: Run Electrolyte Wizard

```python
elec_wizard(
    filename='model.bkp',
    chem_source='APV140 REACTIONS',
    ref_state='Unsymmetric',
    h_ion='Hydronium ion H3O+',
    reaction_opts=['Include water dissociation reaction'],
    prop_method='ENRTL-RK',
    sim_approach='True component approach'
)
```

## Wizard Option Guide

| Option | Choices | When to Use |
|--------|---------|-------------|
| ref_state | `Unsymmetric` | Most aqueous electrolyte systems (recommended) |
| ref_state | `Symmetric` | Fused salts or ionic liquids |
| prop_method | `ENRTL-RK` | Unsymmetric, general purpose (recommended) |
| prop_method | `ELENRTL` | Unsymmetric, alternative |
| prop_method | `ENRTL-SR` | Symmetric reference state only |
| h_ion | `Hydronium ion H3O+` | Most systems (recommended) |
| h_ion | `Hydrogen ion H+` | Simplified proton representation |
| sim_approach | `True component approach` | Rate-based models, detailed (recommended) |
| sim_approach | `Apparent component approach` | Equilibrium-based, simplified |
| reaction_opts | `Include salt formation` | Expected solid salt precipitation (recommended for most) |
| reaction_opts | `Include ice formation` | Low-temperature systems with potential ice formation |
| reaction_opts | `Include water dissociation reaction` | Explicitly consider H+ and OH- from water dissociation |

> **Note:** `reaction_opts` is a list of strings and can accept multiple options (e.g., `['Include salt formation', 'Include water dissociation reaction']`). If omitted, it defaults to `['Include salt formation']`.

## Verification

After running the Electrolyte Wizard, verify the setup:

```python
# 1. Check all components (should include ionic species)
get_components_list()

# 2. Check Henry-Comps sets
get_henrycomps_set_list()

# 3. Check Henry-Comps in each set
get_henrycomps_list(set_name='GLOBAL')
```
