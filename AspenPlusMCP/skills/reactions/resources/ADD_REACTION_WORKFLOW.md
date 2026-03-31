## Add Reaction Workflow

When a completely new reaction set or specific new reactions need to be formulated, use this workflow.

0. `get_components_list`       → Check if all required molecular AND ionic species exist (CRITICAL)
      ↓
1. `get_reaction_set_list`     → Check existing reaction sets
      ↓
2. `get_reaction_set_type_list`→ Check available reaction types
      ↓
3. `SKILL(category='reactions', name=<TYPE>)` → Read the corresponding parameter documentation early
      ↓
4. `add_reaction_set`          → (Optional) Create a new reaction set
      ↓
5. `export_file`               → Export current model to .inp (export_type='inp')
      ↓
6. `close_aspen`               → Close the .bkp file to release locks
      ↓
7. `add_reaction`              → Inject exact Aspen reaction syntax into .inp
      ↓
8. `open_aspen_plus`           → Open the updated .inp file
      ↓
9. `get_reaction_input_specifications` → Query valid parameters (e.g., REACTYPE\1)
      ↓
10. `set_reaction_input_specifications` → Configure reaction parameters

## Step-by-Step Example: Add Reaction

### Step 0: Validate Components Requirement (CRITICAL)

Before configuring any reactions, you **MUST** ensure all necessary components (both molecular and ionic species) exist in the Aspen Plus simulation.

**Action**: Use `get_components_list` to fetch the current components. Check against your planned reaction equations (e.g., if you plan to use `H3O+`, it MUST appear in this list).

> [!IMPORTANT]
> If required ionic species are **missing**, DO NOT attempt to create them manually. Halt the reaction setup, adjust the `elec_wizard` parameters, and **re-run `elec_wizard`** to let Aspen formulate the complete electrolytic species list.

```python
# Check which components are currently available
components = get_components_list()
# Verify that all required species for reactions exist...
```

### Step 1: Query Existing Sets and Types

```python
# Check existing sets
get_reaction_set_list()

### Steps 2-3: Query Types and Read Documentation

```python
# Check valid types supported by Aspen
get_reaction_set_type_list()
# (Agent uses the returned list, e.g., ["POWERLAW", "EQUIL"], to know the type for Step 4)

# 3. Read the corresponding documentation for the identified reaction type (CRITICAL)
# E.g., if the type is POWERLAW or KINETIC:
skills(category='reactions', name='KINETIC')
```

### Step 4: Create a New Reaction Set

If your target reaction set doesn't exist yet, create it.

> [!WARNING]
> **CRITICAL**: The `set_name` MUST NOT exceed 8 characters, otherwise Aspen Plus will reject it.

```python
add_reaction_set(set_name="R-1", reactions_type="POWERLAW")
```

### Steps 5-6: Convert to INP and Close BKP

```python
# Export the current simulation file to INP format (without graphics)
export_file(export_type="inp", file_path="C:/path/to/simulation.inp")

# Close Aspen Plus to prevent file conflicts
close_aspen()
```

### Step 7: Add Reaction Statements to INP

Insert reaction stoichiometry into the `.inp` file using structured dictionaries. This method strictly handles formatting using user-provided IDs.

> [!NOTE]
> If the `set_name` you specify does not exist in the `.inp` file, Aspen Plus MCP will automatically generate the header (`REACTIONS {set_name} {reaction_type}`) and insert the reactions at the **END OF FILE (EOF)**.

> [!WARNING]
> **DO NOT** attempt to inject reaction parameters (such as Arrhenius pre-exponential factors, activation energy, etc.) using `add_reaction`. Parameters must be configured via `set_reaction_input_specifications` (Steps 9-10) using the IDs you defined here.

> [!IMPORTANT]
> **Substream ID (`ssid`) Usage**:
> The `ssid` (e.g., `MIXED`, `CISOLID`) will ONLY be written to the STOIC string if the `reaction_type` is `"POWERLAW"` or `"LHHW"`. For other types like `"REAC-DIST"`, `"EQUIL"`, any provided `ssid` will be safely ignored to prevent syntax errors in Aspen Plus.

> [!CAUTION]
> **COMMON FORMATTING ERROR:**
> When defining `reactions_data` for the STOIC, **NEVER** combine the component name and substream ID as the dictionary key (e.g., `{"MEA+ MIXED": -1}` is **WRONG**).
> If a substream ID is required, you **MUST** use the nested dictionary format: `{"MEA+": {"coef": -1, "ssid": "MIXED"}}` or use the `default_ssid` key at the reaction level.

```python
assigned_ids = add_reaction(
    inp_path="C:/path/to/simulation.inp",
    set_name="R-1",
    reaction_type="POWERLAW",
    reactions_data=[
        # Method 1: Simple dictionary (no substream ID)
        {"id": 1, "stoic": {"CO2": -1.0, "MEA": -1.0, "H2O": -1.0, "MEACOO-": 1.0, "H3O+": 1.0}},
        
        # Method 2: default_ssid applies the same substream ID to all components
        {"id": 2, "default_ssid": "MIXED", "stoic": {"MEA": -1.0, "H3O+": -1.0, "MEAH+": 1.0, "H2O": 1.0}},
        
        # Method 3: Complex dictionary to specify individual substream IDs (e.g., CISOLID for solid precipitation)
        {"id": 3, "stoic": {
            "HCO3-": {"coef": -1.0, "ssid": "MIXED"}, 
            "H2O": {"coef": -1.0, "ssid": "MIXED"}, 
            "NACL": {"coef": 1.0, "ssid": "CISOLID"}
        }}
    ]
)
# Returns: [1, 2, 3]
```

### Steps 8-9: Open Modified INP and Query Specs

```python
# Reopen the updated INP file (Aspen Plus will auto-arrange flowsheet)
open_aspen_plus(file_path="C:/path/to/simulation.inp")
```

### Step 10: Set Specifications

Once loaded in Aspen Plus, query the available parameters and modify them for the specific STOIC IDs you defined in Step 7.

> [!IMPORTANT]
> **LLM INSTRUCTION - READ BEFORE RESTORING/SETTING PARAMETERS:** 
> Before constructing the `specifications_dict` for Step 10, you **MUST** read the relevant parameter configuration guides completely.
> Always call `skills(category='reactions', name='KINETIC')` (for KINETIC/POWERLAW reactions) or `skills(category='reactions', name='EQUIL')` (for EQUIL reactions) to understand the valid keys and required formatting. Do not guess the parameter keys or structures.

```python
# Query valid specifications for the reaction set
get_reaction_input_specifications(reac_set="R-1")

# Set the specifications for individual reactions using the IDs
set_reaction_input_specifications(
    set_name="R-1",
    specifications_dict={
        "REACTYPE\\1": "KINETIC",
        "RATE-CON\\1\\PRE-EXP": 1.330E+17,
        "RATE-CON\\1\\ACT-ENERGY": 23.84820,
        "REACTYPE\\2": "KINETIC",
        "REACTYPE\\3": "KINETIC"
    }
)
```

> ⚠️ For adding stoichiometric reaction strings, use the INP export workflow with `add_reaction`.
> Call `skills(category='reactions', name='KINETIC')` or `skills(category='reactions', name='EQUIL')` for parameter configuration guides.
