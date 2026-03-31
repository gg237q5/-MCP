# Thermodynamic Method Setup

## Setup Workflow ⚠️

1. Use `add_thermo_method` to set method
2. **Must** save as .bkp format
3. **Must** close and reopen file

```python
# Step 1: Set method
add_thermo_method(method_name='NRTL')

# Step 2: Save
save_aspen_file_as(filename='model.bkp')

# Step 3: Close
close_aspen()

# Step 4: Reopen
open_aspen_plus(file_path='model.bkp')
```

## Method Selection Guide

| System Type | Recommended Method |
|-------------|-------------------|
| Ideal systems | IDEAL |
| Polar mixtures | NRTL, UNIQUAC |
| Hydrocarbons | PENG-ROB, SRK |
| Electrolytes | ENRTL-RK, ELENRTL, ENRTL-SR (set via `elec_wizard`) |
| Steam/Water | IAPWS-95 |

> ⚠️ **Electrolyte methods** (ENRTL-RK, ELENRTL, ENRTL-SR) should be configured via `elec_wizard`, NOT manually via `add_thermo_method`. The Wizard automatically sets the property method, Henry Components, and ionic species.
> For the full workflow, call: `skills(category='components', name='ELECTROLYTE')`

## Available Methods

- IDEAL, NRTL, UNIQUAC, WILSON
- PENG-ROB, SRK, PR-BM
- UNIFAC, PSRK
- ELECNRTL, PITZER
- IAPWS-95, IF97
