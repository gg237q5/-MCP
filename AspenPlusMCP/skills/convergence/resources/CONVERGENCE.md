# Convergence Settings Guide

This guide covers the configuration of convergence settings in Aspen Plus.

## Overview

Convergence settings control how Aspen Plus solves recycle loops and design specifications. Proper configuration is essential for simulation stability and performance.

## Key Parameters

### TOL (Tolerance)

**Path:** `TOL`  
**Default:** 0.01  
**Type:** Number

The convergence tolerance determines when the simulation considers a recycle loop converged. Smaller values increase accuracy but may require more iterations.

| Value | Use Case |
|-------|----------|
| 0.001 | High precision (more iterations) |
| 0.01 | Standard simulations (default) |
| 0.1 | Quick estimates |

### WEG_MAXIT (Maximum Wegstein Iterations)

**Path:** `WEG_MAXIT`  
**Default:** 5000  
**Type:** Integer

Maximum number of Wegstein acceleration iterations allowed for convergence. Increase if simulation fails to converge.

| Value | Use Case |
|-------|----------|
| 100 | Simple flowsheets |
| 5000 | Complex recycle loops (default) |
| 9999 | Very difficult convergence (maximum) |

## Usage Examples

### Basic Usage

```python
# Set tolerance
set_input_convergence(tol=0.001)

# Set max iterations
set_input_convergence(weg_maxit=100)

# Set both
set_input_convergence(tol=0.001, weg_maxit=100)
```

### Advanced Usage

```python
# Query all available specs first
get_input_convergence()

# Set using specifications_dict
set_input_convergence(specifications_dict={
    'TOL': 0.001,
    'WEG_MAXIT': 200
})
```

## Workflow

1. **Check current settings:**
   ```python
   get_input_convergence()
   ```

2. **Modify as needed:**
   ```python
   set_input_convergence(tol=0.001, weg_maxit=100)
   ```

3. **Run simulation:**
   ```python
   run_simulation()
   ```

4. **If convergence fails:**
   - Increase `WEG_MAXIT`
   - Loosen `TOL` temporarily
   - Check for tear stream initialization

## Troubleshooting

### Simulation Not Converging

1. Increase maximum iterations:
   ```python
   set_input_convergence(weg_maxit=9999)
   ```

2. Loosen tolerance temporarily:
   ```python
   set_input_convergence(tol=0.1)
   ```

3. After convergence, tighten tolerance:
   ```python
   set_input_convergence(tol=0.01)
   ```

### Too Many Iterations

1. Check for conflicting design specs
2. Review tear stream selection
3. Consider using different convergence methods

## Related Tools

- `get_input_convergence` - Query all convergence specifications
- `set_input_convergence` - Set convergence parameters
- `run_simulation` - Execute simulation after configuration
- `check_model_completion_status` - Verify model readiness
