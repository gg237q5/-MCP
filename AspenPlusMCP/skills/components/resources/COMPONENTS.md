# Component Setup

## Setup Method

Create input file with components using `create_inp_file`:

```python
create_inp_file(
    file_path='D:\\path\\to\\model.inp',
    components=['WATER', 'ETHANOL', 'METHANOL'],
    cas_numbers=['7732-18-5', '64-17-5', '67-56-1']
)
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| components | Component name list (max 8 characters) |
| cas_numbers | Corresponding CAS numbers |

## Common Component CAS Numbers

| Component | CAS |
|-----------|-----|
| WATER | 7732-18-5 |
| ETHANOL | 64-17-5 |
| METHANOL | 67-56-1 |
| BENZENE | 71-43-2 |
| TOLUENE | 108-88-3 |

## View Configured Components

```python
get_components_list()
```
