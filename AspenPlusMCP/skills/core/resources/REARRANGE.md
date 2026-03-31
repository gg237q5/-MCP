# Auto-Rearrange Flowsheet Layout

Aspen Plus has an internal algorithm to automatically arranging the flowsheet layout, but it is only triggered when opening a non-graphic input file (.inp).

> [!TIP]
> Use this workflow when your flowsheet becomes messy or after adding many blocks programmatically.

## Workflow

1. **Save Current File**
   - Use `save_aspen_file()` to ensure current work is saved
   - This prevents data loss before restructuring

2. **Export to Input File** (without graphics)
   - Use `export_file(export_type='inp', file_path='...')`
   - This saves the model data *without* the visual layout coordinates.

3. **Close Current Simulation**
   - Use `close_aspen()`
   - This closes the currently open file.

4. **Close Connection**
   - Use `close_aspen_connection()`
   - This closes the COM connection to Aspen Plus.

5. **Reconnect to Aspen Plus**
   - Use `aspen_connect()`
   - Establishes a fresh connection

6. **Open the Input File**
   - Use `open_aspen_plus(file_path='...')` referencing the file you just exported.
   - Aspen Plus will detect missing graphics and automatically generate a new, organized layout.

7. **Save as Backup**
   - Use `save_aspen_file_as(filename='...bkp')`
   - It is safer to work with .bkp files for stability.

## Example Code

```python
# 1. Save current work
save_aspen_file()

# 2. Export
export_file(export_type='inp', file_path='C:\\my_work\\temp_layout.inp')

# 3. Close file
close_aspen()

# 4. Close connection
close_aspen_connection()

# 5. Reconnect
aspen_connect()

# 6. Reopen to trigger auto-arrange
open_aspen_plus(file_path='C:\\my_work\\temp_layout.inp')

# 7. Save back to original format
save_aspen_file_as(filename='C:\\my_work\\my_model_clean.bkp')
```
