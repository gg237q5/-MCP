## Remove Reaction Workflow

When specific reactions need to be removed from an existing Reaction Set, you must reconstruct the block by passing ONLY the reactions you want to keep. Follow this workflow:

0. `save_aspen_file`           → Save current model state
      ↓
1. `get_reaction_set_list`     → Get the list of available Reaction Sets
      ↓
2. `SKILL(category='reactions', name=<TYPE>)` → Read the corresponding parameter documentation early
      ↓
3. `get_reaction_input_specifications` → Query valid parameters (e.g., REACTYPE\1)
      ↓
4. `export_file`               → Export current model to .inp (export_type='inp')
      ↓
5. `close_aspen`               → Close the .bkp file to release locks
      ↓
6. `remove_reaction`           → Pass reactions_data you want to KEEP to reconstruct the set
      ↓
7. `open_aspen_plus`           → Open the updated .inp file
      ↓
8. `get_reaction_input_specifications` → Verify remaining reactions and parameters
      ↓
9. `set_reaction_input_specifications` → Configure reaction parameters


**WORKFLOW**: To preserve parameters for the retained reactions, you MUST first backup the parameters using COM, run the `remove_reaction` tool on the INP to trim the reactions, reopen the file, and then restore the parameters via COM.

## Step-by-Step Example: Remove Reaction

### Steps 0-2: Save State, List Sets, and Read Documentation

Protect the current state and retrieve available reaction sets.

```python
# 0. Save current state
save_aspen_file()

# 1. Get the list of available Reaction Sets to identify the exact name and TYPE
get_reaction_set_list()
# (Agent uses the returned list, e.g., [{"name": "R-1", "type": "POWERLAW"}], to know the type for Step 6)

# 2. Read the corresponding documentation for the identified reaction type (CRITICAL)
# E.g., if the type is POWERLAW or KINETIC:
skills(category='reactions', name='KINETIC')
skills(category='reactions', name='EQUIL')
```

### Step 3: Backup Existing Parameters (CRITICAL)

Before modifying the INP file, you **MUST** backup the parameters for the reactions you intend to KEEP. `remove_reaction` deletes the block and reconstructs only the STOIC lines. If you don't backup parameters now, they will be lost.

> [!CAUTION]
> **Handling `None` Values in Backup:**
> When querying parameters, you may see values as `None` (e.g., `EXPONENT\1\CO2 MIXED: None`). A `None` value means Aspen was implicitly using the absolute value of the stoichiometric coefficient for that parameter.
> **Action:** When restoring parameters in Step 10, you **MUST NOT** skip these. You must dynamically calculate the explicit value from the `stoic` definitions you retained (e.g., if CO2 stoic is -1.0, explicitly set the exponent to 1.0) and include it in your `set_reaction_input_specifications` payload.

```python
# 3. Backup existing parameters for the reactions you want to KEEP!
get_reaction_input_specifications(reac_set="R-1")
# (Agent processes the output and notes down parameters for the retained IDs)
```

### Steps 4-5: Export to INP and Close Aspen

Generate the `.inp` file and release the COM lock so the file can be modified.

```python
# 4. Export to INP
export_file(export_type="inp", file_path="C:/path/to/simulation.inp")

# 5. Close Aspen
close_aspen()
```

### Step 6: Identify Reactions to KEEP

Review the `.inp` file to figure out which reaction IDs represent the reactions you need to retain. Note down their exact chemical stoichiometry.

### Step 7: Remove Reactions via Rebuilding INP block

Reconstruct the reaction set by passing **ONLY** the reactions you want to keep to the `remove_reaction` tool. Specify the `reaction_type` using the type string retrieved in Step 1.

> [!CAUTION]
> **COMMON FORMATTING ERROR:**
> When defining `reactions_data` for the STOIC, **NEVER** combine the component name and substream ID as the dictionary key (e.g., `{"MEA+ MIXED": -1}` is **WRONG**).
> If a substream ID is required, you **MUST** use the nested dictionary format: `{"MEA+": {"coef": -1, "ssid": "MIXED"}}` or use the `default_ssid` key at the reaction level.
>
> **NOTE**: You MUST NOT include parameters like RATE-CON here. Provide only 'id' and 'stoic'!

```python
# 7. Remove unwanted reactions by rebuilding the block with ONLY retained STOIC
# Example: Assume we want to remove all other reactions and only keep reactions 1, 2, and 3.
remove_reaction(inp_path="C:/path/to/simulation.inp",
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

### Steps 8-10: Open Modified INP and Restore Parameters

Re-open the `.inp` file. Aspen Plus will parse the new `.inp`, rendering only the reactions you kept. Finally, restore the operational parameters using COM.
```python
# 8. Open the modified file
open_aspen_plus(file_path="C:/path/to/simulation.inp")

# 9. (Optional but recommended) Verify remaining specs
get_reaction_input_specifications(reac_set="R-1")

# 10. Restore the parameters we backed up in Step 3
set_reaction_input_specifications(
    set_name="R-1",
    specifications_dict={
        "RATE-CON\\1\\PRE-EXP": 1.33e17,
        "RATE-CON\\1\\ACT-ENERGY": 0.023824,
        "POWLAW-EXP\\1\\MIXED\\CO2": 1.0
        # ... additional restored parameters ...
    }
)
```
