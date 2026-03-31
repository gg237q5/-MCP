# Aspen Plus MCP Overview

## Model Building Workflow

```
⚠️ First: Is this an electrolyte system (amines, acid gas, ionic)?
   → YES: Go to "Electrolyte System Workflow" below
   → NO: Follow this standard workflow

1. Create input file (create_inp_file)
      ↓
2. Open file (open_aspen_plus)
      ↓
3. Set thermodynamic method (add_thermo_method)
      ↓
4. Save/Close/Reopen
      ↓
5. Add reactions (Optional, see Reaction System Workflow)
      ↓
6. Add blocks and streams (add_block, add_stream)
      ↓
7. Connect streams (connect_block_stream)
      ↓
8. Set stream conditions (set_stream_input_conditions)
      ↓
9. Set block specs (set_block_input_specifications)
      ↓
10. Auto-arrange flowsheet (see REARRANGE skill)
      ↓
11. Check model (check_model_completion_status)
      ↓
12. Run simulation (check_and_run)
```

> [!TIP]
> Step 10 explains how to fix messy process flow diagrams. For detailed instructions, call: `skills(category='core', name='REARRANGE')`

> [!TIP]
> For setting up recycle streams correctly, refer to: `skills(category='streams', name='RECYCLE')`

> [!TIP]
> If your simulation fails to converge (especially with recycle loops), refer to the troubleshooting guide: `skills(category='simulation', name='TROUBLESHOOTING')`


## Electrolyte System Workflow

For systems involving ionic species:

```
1. Create input file (create_inp_file)
   → Add MOLECULAR components ONLY
   → Do NOT add ions
      ↓
2. Open .inp file (open_aspen_plus)
      ↓
3. Save as .bkp (save_aspen_file_as)
      ↓
4. Close / Reopen .bkp / Show GUI
   (close_aspen, open_aspen_plus, show_aspen_gui)
      ↓
5. Run elec_wizard
   → Auto-adds ionic species, Henry-Comps, thermo method, reactions
   → If it fails, simply re-run elec_wizard
      ↓
6. Verify: get_components_list, get_henrycomps_set_list, get_henrycomps_list
      ↓
7. Modify reactions if needed (Optional, see Reaction System Workflow)
      ↓
8. Add blocks and streams (add_block, add_stream)
      ↓
9. Connect, set conditions, set specs (same as standard workflow steps 7-12)
```

> [!TIP]
> For detailed wizard options and examples, call: `skills(category='components', name='ELECTROLYTE')`

## Reaction System Workflow

For processes that require explicit chemical reaction definitions (Kinetic, Equilibrium, REAC-DIST, etc.):

**Prerequisite:** 
1. Ensure that the property method has already been set and the file has been saved, closed, and reopened.
2. Ensure ALL required components (molecular AND ionic) exist in the simulation. If ions are missing, DO NOT add them manually; instead re-run `elec_wizard`.

### Add Reaction Workflow

```
0. get_components_list       → Check if all required molecular AND ionic species exist (CRITICAL)
      ↓
1. get_reaction_set_list     → Check existing reaction sets
      ↓
2. get_reaction_set_type_list→ Check available reaction types
      ↓
3. SKILL(category='reactions', name=<TYPE>) → Read the corresponding parameter documentation early
      ↓
4. add_reaction_set          → (Optional) Create a new reaction set
      ↓
5. export_file               → Export current model to .inp (export_type='inp')
      ↓
6. close_aspen               → Close the .bkp file to release locks
      ↓
7. add_reaction              → Inject exact Aspen reaction syntax into .inp
      ↓
8. open_aspen_plus           → Open the updated .inp file
      ↓
9. get_reaction_input_specifications → Query valid parameters
      ↓
10. set_reaction_input_specifications → Configure reaction parameters
```

### Remove Reaction Workflow

```
0. save_aspen_file           → Save current model state
      ↓
1. get_reaction_set_list     → Get the list of available Reaction Sets
      ↓
2. SKILL(category='reactions', name=<TYPE>) → Read the corresponding parameter documentation early
      ↓
3. get_reaction_input_specifications → Query valid parameters (e.g., REACTYPE\1)
      ↓
4. export_file               → Export current model to .inp (export_type='inp')
      ↓
5. close_aspen               → Close the .bkp file to release locks
      ↓
6. read .inp file            → Review .inp to identify reaction IDs and parameters to KEEP
      ↓
7. remove_reaction           → Pass reactions_data you want to KEEP to reconstruct the set
      ↓
8. open_aspen_plus           → Open the updated .inp file
      ↓
9. get_reaction_input_specifications → Verify remaining reactions and parameters
      ↓
10. set_reaction_input_specifications → Configure reaction parameters
```

> [!TIP]
> For detailed instructions on adding or removing stoichiometric strings via INP, call: 
> `skills(category='reactions', name='ADD_REACTION_WORKFLOW')` or 
> `skills(category='reactions', name='REMOVE_REACTION_WORKFLOW')`

## Opening Existing Files Workflow

When working with an existing Aspen Plus file, follow this workflow to understand the model before making changes:

```
1. Open file (open_aspen_plus)
      ↓
2. Scan model information (list_aspen_info, info_type='all')
      ↓
3. Get components list (get_components_list)
      ↓
4. Get streams list (get_streams_list)
      ↓
5. Get blocks list (get_blocks_list)
      ↓
6. Check connections (get_block_connections for each block)
      ↓
7. Review stream conditions (get_stream_input_conditions_list)
      ↓
8. Review block specifications (get_block_input_specifications)
      ↓
9. Check model status (check_model_completion_status)
```



## Tool Categories

| Category | Key Tools |
|----------|-----------|
| streams | add_stream, connect_block_stream, set/get input/output |
| blocks | add_block, connect_block_stream, set/get input/output |
| components | get_components_list, elec_wizard, get_henrycomps_set_list, get_henrycomps_list |
| properties | add_thermo_method, get_properties_list |
| reactions | add_reaction_set, add_reaction, set_reaction_input_specifications |
| simulation | check_model, run_simulation, check_and_run |
| utils | unit_list, skills |
