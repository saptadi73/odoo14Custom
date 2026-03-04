# Fix: RuntimeError - OrderedDict mutated during iteration

## Problem

**Error:**
```
RuntimeError: OrderedDict mutated during iteration
  File "C:\odoo14c\server\odoo\service\server.py", line 408, in cron_thread
    for db_name, registry in registries.d.items():
```

## Root Cause

The cron thread was iterating directly over `registries.d.items()` (an OrderedDict). When multiple threads are running:
- Thread A iterates over the registries
- Thread B adds/removes a database registry during the iteration
- Python raises `RuntimeError` because the dictionary was modified during iteration

This is a **race condition** that occurs when:
1. Multiple cron threads are polling for jobs
2. New database connections are being created/destroyed
3. Module upgrades are happening

## Solution

Changed the iteration from:
```python
for db_name, registry in registries.d.items():
```

To:
```python
for db_name, registry in list(registries.d.items()):
```

**Why this works:**
- `list(registries.d.items())` creates a **snapshot** of the dictionary items at that moment
- We iterate over the snapshot, not the live dictionary
- Changes to the original dictionary don't affect our iteration
- This is a standard Python pattern for safe dictionary iteration

## File Changed

- `C:\odoo14c\server\odoo\service\server.py` (line 408)

## Impact

- ✅ Fixes the RuntimeError during cron execution
- ✅ Allows safe concurrent access to registry dictionary
- ✅ No performance impact (the list is created very quickly)
- ✅ Standard Python best practice for this scenario

## Testing

After this fix, the Odoo server should start and run without the RuntimeError. The cron threads will continue to poll for jobs safely even when database registries are being added/removed.

**Restart Odoo to apply the fix:**
```bash
# Stop current Odoo process and restart
python C:\odoo14c\server\odoo-bin -c C:\addon14\odoo.conf
```

## Date
Fixed on: March 4, 2026
