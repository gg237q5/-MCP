# Convergence Troubleshooting Guide

Strategies for resolving Tear and Block convergence issues in Aspen Plus.

## Tear Convergence Issues

Use this strategy when the simulation fails to converge on a recycle loop (Tear Stream).

### Strategy

1. Confirm that the Recycle configuration is complete. Refer to `skills(category='streams', name='RECYCLE')` for guidance.
2. Adjust `WEG_MAXIT` to increase iteration limit.
3. Adjust `TOL` to relax tolerance if the issue persists.

### Recommended Settings

| Parameter | Value | Reason |
|-----------|-------|--------|
| `TOL` | 0.01 | Standard tolerance for recycle loops, can be relaxed to 0.1 if needed |
| `WEG_MAXIT` | 1000 | Increased iterations for complex loops; maximum: 9999 |

### Quick Fix Command

```python
set_input_convergence(tol=0.01, weg_maxit=1000)
```

## Block Convergence Issues

Use this strategy when a specific unit operation block fails to converge.

> [!IMPORTANT]
> Apply these adjustments **ONLY** to the specific blocks that are failing to converge. Do not apply them globally or to blocks that are already converging correctly.

### 1. Increase Iterations

First, try increasing the maximum iterations for the block.

- **Action**: Set Block Max Iterations to **200**.

### 2. Progressive Tolerance Tightening

If simply increasing iterations doesn't work, use this progressive tightening workflow. **Reinitialize** first, then **do not reinitialize** between steps.

**Workflow:**

1.  **Reset Simulation**:
    - Reinitialize the simulation to clear previous state.

2.  **Initial Loose Run**:
    - Set `TOLOL` to **0.01**
    - Run simulation
    - *Note: Ensure Reinitialization is OFF for subsequent steps*

3.  **Step-wise Tightening**:
    - Reduce `TOLOL` to **0.001** -> Run
    - Reduce `TOLOL` to **0.0001** -> Run
    - Reduce `TOLOL` to **1e-5** -> Run (Final Goal)

**Python Implementation Example:**

```python
# Step 1: Reinitialize (Reset)
reinitialization()

# Step 2: Loose tolerance
# Note: Replace 'BLOCK_NAME' with your specific block name
set_block_input_specifications(block_name='BLOCK_NAME', specifications={'TOLOL': 0.01})
run_simulation()

# Step 3: Tighten progressively (without re-init)
tols = [0.001, 0.0001, 1e-5]
for tol in tols:
    set_block_input_specifications(block_name='BLOCK_NAME', specifications={'TOLOL': tol})
    run_simulation()
```
