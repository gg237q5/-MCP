# KINETIC and POWERLAW Reaction Setup

Kinetic and Powerlaw reactions require reaction rate constants (Arrhenius equation parameters).

## Required Parameters

- `REACTYPE\n`: Set to `"KINETIC"` or `"POWERLAW"`
- `PRE-EXP\n`: Pre-exponential factor ($k_0$)
- `ACT-ENERGY\n`: Activation energy ($E$)

- `EXPONENT\n\[COMP] [SSID]`: Concentration exponent for **reacting** species (Reactants).
  - **Example Node Path:** `EXPONENT\6\CO2 MIXED` *(Derived from `Application.Tree.Data.Reactions.Reactions.ABSORBER.Input.EXPONENT.6.CO2 MIXED`)*
  
- `EXPONENT1\n\[COMP] [SSID]`: Concentration exponent for **product** species (Products).
  - **Example Node Path:** `EXPONENT1\9\MEA MIXED` *(Derived from `Application.Tree.Data.Reactions.Reactions.ABSORBER.Input.EXPONENT1.9.MEA MIXED`)*
  - **Handling `None` Values:** If `get_reaction_input_specifications` returns `None` for an exponent, Aspen is implicitly using the stoichiometric coefficient. **CRITICAL:** When restoring parameters via `set_reaction_input_specifications`, you **MUST explicitly set** the exponent back to the absolute value of the stoichiometric coefficient. Do not leave it as `None`.

## Optional/Advanced Parameters

- `T-REF\n`: Reference temperature ($T_0$)
- `EXP\n`: Temperature exponent ($n$)

> [!TIP]
> **Always use `get_reaction_input_specifications`**!
> If you are unsure what the exact parameter path string is for a specific field, call `get_reaction_input_specifications(reac_set="YOUR-SET")`. It will dump the complete list of valid paths (e.g., `PRE-EXP\1`) that you can copy and use in `set_reaction_input_specifications`.
