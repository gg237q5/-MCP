---
name: reactions
description: Reaction configuration guides for defining chemical reactions and sets in Aspen Plus.
---

# Reaction Configuration Skills

Guides for setting up and managing chemical reactions in Aspen Plus models.

## Available Resources

| Resource | Description |
|----------|-------------|
| `KINETIC.md` | KINETIC and POWERLAW reaction parameters setup |
| `EQUIL.md` | EQUIL (Equilibrium) reaction parameters setup |
| `ADD_REACTION_WORKFLOW.md` | Complete step-by-step workflow for adding a new reaction or reaction set |
| `REMOVE_REACTION_WORKFLOW.md` | Complete step-by-step workflow for safely removing reactions |

## When to Use

Use this workflow when the process involves **chemical reactions** requiring explicit definitions, such as:

- Kinetic or Powerlaw reactions
- Equilibrium reactions
- Distillation with reactive components (REAC-DIST)
- LHHW or complex kinetics
- Custom defined stoichiometric equations

> [!IMPORTANT]
> **LLM INSTRUCTION - MANDATORY STEP:**
> Whenever you modify, reconstruct, or add a reaction set, you **MUST** read the parameter configuration guide for the specific reaction type (e.g., `KINETIC.md` or `EQUIL.md`) **BEFORE** attempting to configure the reaction parameters using `set_reaction_input_specifications`. Guessing parameter keys frequently results in Aspen Plus COM errors.