# Export File

Export Aspen Plus models to various file formats.

## Export Types

| Type | Extension | Description |
|------|-----------|-------------|
| `inp` | .inp | Input file **without graphics** - flowsheet auto-arranges on reopen |
| `inp_graphics` | .inp | Input file with graphics - preserves layout |
| `bkp` | .bkp | Backup file - complete model backup |
| `rep` | .rep | Report file - simulation results |
| `sum` | .sum | Summary file - simulation summary |

## Usage

```python
export_file(export_type='inp', file_path='C:/Temp/model.inp')
```

## Key Use Case: Flowsheet Re-layout

When building a model programmatically, the flowsheet graphics may be cluttered. To get a clean layout:

1. **Export to .inp** (without graphics):
   ```python
   export_file(export_type='inp', file_path='C:/Temp/model.inp')
   ```

2. **Close the current file**:
   ```python
   close_aspen()
   ```

3. **Reopen the .inp file**:
   ```python
   open_aspen_plus(file_path='C:/Temp/model.inp')
   ```

4. Aspen Plus will **auto-arrange** the flowsheet layout

## Export Before/After Simulation

| Export Type | Before Simulation | After Simulation |
|-------------|-------------------|------------------|
| `inp` | ✅ Model definition | ✅ With results |
| `inp_graphics` | ✅ With layout | ✅ With layout + results |
| `bkp` | ✅ Complete backup | ✅ Complete backup |
| `rep` | ❌ No results yet | ✅ Results report |
| `sum` | ❌ No results yet | ✅ Summary |

## Example Workflow

```python
# 1. Build model
add_block('COL1', 'RADFRAC')
add_stream('FEED')
# ... configure model ...

# 2. Export to .inp for clean layout
export_file(export_type='inp', file_path='C:/Temp/model.inp')

# 3. Reopen for auto-arranged flowsheet
close_aspen()
open_aspen_plus(file_path='C:/Temp/model.inp')

# 4. Run simulation
check_and_run()

# 5. Export results
export_file(export_type='rep', file_path='C:/Temp/results.rep')
```
