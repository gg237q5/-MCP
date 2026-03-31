# Simulation Execution

## Recommended Workflow

1. **Check model completeness**
```python
check_model_completion_status()
```

> [!IMPORTANT]
> **For processes with recycles** (e.g., azeotrope breaking, extractive distillation), you must set initial conditions for recycle streams before running. See: `skills(category='streams', name='RECYCLE')`

2. **Run simulation** (three methods)

### Method A: Smart Execution (Recommended)
```python
check_and_run()
```
- Auto-checks model
- Evaluates if ready to run
- Auto-executes or reports issues

### Method B: Direct Execution
```python
run_simulation()
```
- Runs directly without pre-check

### Method C: Run with Report
```python
run_and_report()
```
- Runs and generates detailed report

## After Running

1. **View results**
```python
get_stream_output_conditions('STREAM_NAME')
get_block_output_specifications('BLOCK_NAME')
```

2. **Save file**
```python
save_aspen_file()
```
