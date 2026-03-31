---
name: properties
description: Thermodynamic property method configuration for Aspen Plus models.
---

# Property Configuration Skills

Guides for setting up thermodynamic methods and properties.

## Available Resources

| Resource | Description |
|----------|-------------|
| `THERMO_METHOD.md` | Thermodynamic method selection and setup |

## Usage

```python
skills(category='properties', name='THERMO_METHOD')
```

## Workflow

1. `add_thermo_method` - Set method
2. `save_aspen_file_as` - Save as .bkp
3. `close_aspen` - Close file
4. `open_aspen_plus` - Reopen file
