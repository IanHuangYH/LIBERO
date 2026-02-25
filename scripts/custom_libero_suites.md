# Creating Custom LIBERO Task Suites

This guide explains how to create and manage custom LIBERO task suites (e.g., variants with different objects, spatial arrangements, or task goals).

## Table of Contents

1. [Quick Start](#quick-start)
2. [Workflow Overview](#workflow-overview)
3. [Tool Reference](#tool-reference)
4. [Manual Process (Advanced)](#manual-process-advanced)
5. [Troubleshooting](#troubleshooting)
6. [Examples](#examples)

---

## Quick Start

### Create a New Suite (Automated)

```bash
# Step 1: Create suite from existing one
bash third_party/LIBERO/scripts/create_new_libero_suite.sh \
    --new_suite libero_unseen_object \
    --copy_from libero_object \
    --description "LIBERO Object tasks with unseen distractor objects"

# Step 2: Edit BDDL files manually
# Edit files in: third_party/LIBERO/libero/libero/bddl_files/libero_unseen_object/

# Step 3: Regenerate init files after editing BDDLs
bash third_party/LIBERO/scripts/create_new_libero_suite.sh \
    --new_suite libero_unseen_object \
    --regenerate_init_only

# Alternatively, use the Python script directly:
python third_party/LIBERO/scripts/regenerate_all_tasks.py \
    --suite libero_unseen_object

# Step 4: Validate setup
bash third_party/LIBERO/scripts/validate_libero_suite.sh libero_unseen_object

# Step 5: Test evaluation
TASK_SUITE=libero_unseen_object ./pi_setting/eval/eval_libero_quick_test.sh
```

---

## Workflow Overview

### Creating a custom suite involves these steps:

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTOMATED WORKFLOW                            │
└─────────────────────────────────────────────────────────────────┘

1. create_new_libero_suite.py
   ├── Creates directories (bddl_files/, init_files/)
   ├── Copies BDDL and init files from source suite
   ├── Registers suite in libero_suite_task_map.py
   └── Registers suite in benchmark/__init__.py

2. MANUAL STEP: Edit BDDL files
   └── Modify objects, regions, initial conditions, etc.

3. regenerate_all_tasks.py OR set_liberoenv_addobject.sh
   ├── Preserves unchanged object positions
   ├── Generates positions for new objects
   └── Creates .pruned_init files

4. validate_libero_suite.py
   ├── Checks all files exist
   ├── Verifies registration
   └── Confirms suite can be imported

5. Test with evaluation
   └── TASK_SUITE=<your_suite> ./eval_libero_quick_test.sh
```

---

## Tool Reference

### 1. `create_new_libero_suite.sh` (Recommended)

**Purpose:** Shell wrapper for automated suite creation and registration

**Usage:**
```bash
# Create new suite
bash third_party/LIBERO/scripts/create_new_libero_suite.sh \
    --new_suite libero_custom \
    --copy_from libero_object \
    --description "My custom LIBERO suite"

# Regenerate init files for existing suite
bash third_party/LIBERO/scripts/create_new_libero_suite.sh \
    --new_suite libero_custom \
    --regenerate_init_only
```

**What it does:**
- ✅ Creates `bddl_files/<suite_name>/` and `init_files/<suite_name>/`
- ✅ Copies all BDDL and init files from source suite
- ✅ Creates `.bddl.old` backup files automatically
- ✅ Adds suite to `libero_suite_task_map.py`
- ✅ Registers suite class in `benchmark/__init__.py`
- ✅ Adds suite to `libero_suites` list

**Python version:** `create_new_libero_suite.py` - Same functionality, called by the shell script

**Arguments:**
- `--new_suite`: Name of the new suite (required)
- `--copy_from`: Source suite to copy from (required for new creation)
- `--description`: Description of the suite (optional)
- `--regenerate_init_only`: Only regenerate init files (skip creation)
- `--skip_registration`: Skip updating registration files (advanced)

---

### 2. `set_liberoenv_addobject.sh`

**Purpose:** Regenerate init file for a single task with preserved positions

**Usage:**
```bash
# Use defaults (defined in script)
./pi_setting/eval/set_liberoenv_addobject.sh

# Override suite and task
./pi_setting/eval/set_liberoenv_addobject.sh \
    libero_unseen_object \
    pick_up_the_alphabet_soup_and_place_it_in_the_basket
```

**What it does:**
- ✅ Compares old BDDL (`.bddl.old`) with new BDDL (`.bddl`)
- ✅ Preserves exact positions of unchanged objects
- ✅ Generates new positions for added objects
- ✅ Creates `.pruned_init` file
- ✅ Auto-creates backup BDDL if missing

**When to use:**
- Iterating on a single task (edit BDDL, test, repeat)
- Fine-tuning object positions for one task
- Quick testing of BDDL changes

---

### 3. `regenerate_all_tasks.py` / `regenerate_all_tasks.sh`

**Purpose:** Batch regenerate init files for all tasks in a suite

**Usage:**
```bash
# Python version
python third_party/LIBERO/scripts/regenerate_all_tasks.py \
    --suite libero_unseen_object

# Bash version
./pi_setting/eval/regenerate_all_tasks.sh libero_unseen_object
```

**What it does:**
- ✅ Finds all BDDL files in the suite
- ✅ Calls `set_liberoenv_addobject.sh` for each task
- ✅ Regenerates all `.pruned_init` files

**When to use:**
- After editing multiple BDDL files
- Initial setup after copying from source suite
- Bulk regeneration after logic changes

---

### 4. `validate_libero_suite.sh` (Recommended)

**Purpose:** Shell wrapper for validating suite configuration

**Usage:**
```bash
bash third_party/LIBERO/scripts/validate_libero_suite.sh libero_unseen_object
```

**What it checks:**
- ✅ Directories exist (`bddl_files/`, `init_files/`)
- ✅ All tasks have BDDL files
- ✅ All tasks have `.init` and `.pruned_init` files
- ✅ All tasks have `.bddl.old` backup files
- ✅ Suite is in `libero_suite_task_map.py`
- ✅ Suite is in `libero_suites` list
- ✅ Benchmark class exists
- ✅ Suite can be imported and instantiated

**Python version:** `validate_libero_suite.py --suite <name>` - Same functionality, called by the shell script

**When to use:**
- Before running evaluation
- After manual changes to registration files
- Debugging setup issues

---

## Manual Process (Advanced)

If you prefer manual control or need to understand what's happening:

### Step 1: Create Folders
```bash
SUITE_NAME="libero_custom"
mkdir -p third_party/LIBERO/libero/libero/bddl_files/$SUITE_NAME
mkdir -p third_party/LIBERO/libero/libero/init_files/$SUITE_NAME
```

### Step 2: Copy Files
```bash
SOURCE="libero_object"
cp third_party/LIBERO/libero/libero/bddl_files/$SOURCE/*.bddl \
   third_party/LIBERO/libero/libero/bddl_files/$SUITE_NAME/

cp third_party/LIBERO/libero/libero/init_files/$SOURCE/*.init \
   third_party/LIBERO/libero/libero/init_files/$SUITE_NAME/
```

### Step 3: Edit BDDL Files
Manually edit BDDL files to add/remove objects, change regions, etc.

### Step 4: Add to `libero_suite_task_map.py`
Edit `third_party/LIBERO/libero/libero/benchmark/libero_suite_task_map.py`:

```python
libero_task_map = {
    # ... existing suites ...
    
    "libero_custom": [
        "task_name_1",
        "task_name_2",
        # ... all your tasks ...
    ],
}
```

### Step 5: Register in `benchmark/__init__.py`
Edit `third_party/LIBERO/libero/libero/benchmark/__init__.py`:

**Add to `libero_suites` list:**
```python
libero_suites = [
    "libero_spatial",
    "libero_object",
    "libero_goal",
    "libero_90",
    "libero_10",
    "libero_unseen_object",  # <-- Add your suite
    "libero_custom",         # <-- Add your suite
]
```

**Add benchmark class at the end:**
```python
@register_benchmark
class LIBERO_CUSTOM(Benchmark):
    def __init__(self, task_order_index=0):
        super().__init__(task_order_index=task_order_index)
        self.name = "libero_custom"
        self._make_benchmark()
```

### Step 6: Regenerate Init Files
```bash
python third_party/LIBERO/scripts/regenerate_all_tasks.py --suite libero_custom
```

### Step 7: Validate
```bash
python third_party/LIBERO/scripts/validate_libero_suite.py --suite libero_custom
```

---

## Troubleshooting

### Error: "Unknown LIBERO suite"

**Cause:** Suite not registered in `benchmark/__init__.py`

**Fix:**
1. Check if suite is in `libero_suites` list
2. Check if benchmark class exists (e.g., `LIBERO_CUSTOM`)
3. Run validation: `python scripts/validate_libero_suite.py --suite <name>`

---

### Error: KeyError in `libero_task_map`

**Cause:** Suite not in `libero_suite_task_map.py`

**Fix:**
1. Add suite entry to `libero_suite_task_map.py`
2. List all task names (match BDDL filenames without `.bddl`)
3. Run validation

---

### Missing `.pruned_init` files

**Cause:** Init files not regenerated after BDDL edits

**Fix:**
```bash
# Regenerate all
python scripts/regenerate_all_tasks.py --suite <name>

# Or regenerate single task
./pi_setting/eval/set_liberoenv_addobject.sh <suite> <task>
```

---

### Validation fails: "Tasks in BDDL but not in task_map"

**Cause:** Task map and BDDL files out of sync

**Fix:**
1. Check BDDL filenames in `bddl_files/<suite>/`
2. Update `libero_suite_task_map.py` to match
3. Task names must match exactly (no `.bddl` extension)

---

## Examples

### Example 1: Create Suite with Distractor Objects

```bash
# 1. Create suite
bash scripts/create_new_libero_suite.sh \
    --new_suite libero_distractor \
    --copy_from libero_object \
    --description "Object tasks with visual distractors"

# 2. Edit BDDL: Add distractor objects
# Edit: bddl_files/libero_distractor/pick_up_the_*.bddl
# Add: plate, bowl, mug (as distractors)

# 3. Regenerate init files
bash scripts/create_new_libero_suite.sh \
    --new_suite libero_distractor \
    --regenerate_init_only

# 4. Validate
bash scripts/validate_libero_suite.sh libero_distractor

# 5. Test
TASK_SUITE=libero_distractor ./pi_setting/eval/eval_libero_quick_test.sh
```

---

### Example 2: Iterate on Single Task

```bash
# Edit BDDL for one task
vim bddl_files/libero_distractor/pick_up_the_milk_and_place_it_in_the_basket.bddl

# Regenerate just that task
./pi_setting/eval/set_liberoenv_addobject.sh \
    libero_distractor \
    pick_up_the_milk_and_place_it_in_the_basket

# Test quickly
# (modify eval script to test single task)
```

---

### Example 3: Copy From Different Suite

```bash
# Create suite based on spatial tasks
bash scripts/create_new_libero_suite.sh \
    --new_suite libero_spatial_variant \
    --copy_from libero_spatial \
    --description "Spatial tasks with different arrangements"

# Edit spatial configurations in BDDL files
# Regenerate and validate as usual
```

---

## File Structure Reference

```
third_party/LIBERO/libero/libero/
├── bddl_files/
│   ├── libero_object/
│   │   ├── pick_up_the_alphabet_soup_and_place_it_in_the_basket.bddl
│   │   └── ...
│   └── libero_unseen_object/          # Your custom suite
│       ├── pick_up_the_*.bddl
│       └── *.bddl.old                 # Auto-created backups
│
├── init_files/
│   ├── libero_object/
│   │   ├── pick_up_the_alphabet_soup_and_place_it_in_the_basket.init
│   │   ├── pick_up_the_alphabet_soup_and_place_it_in_the_basket.pruned_init
│   │   └── ...
│   └── libero_unseen_object/          # Your custom suite
│       ├── *.init                     # Copied from source
│       ├── *.pruned_init              # Generated after BDDL edits
│       └── visualizations/            # Scene previews (optional)
│
└── benchmark/
    ├── __init__.py                    # Suite registration
    └── libero_suite_task_map.py       # Task name mapping
```

---

## Best Practices

1. **Always validate after changes**
   ```bash
   bash scripts/validate_libero_suite.sh <name>
   # Or use Python directly:
   # python scripts/validate_libero_suite.py --suite <name>
   ```

2. **Use version control**
   - Commit after creating suite
   - Track BDDL changes
   - Don't commit `.pruned_init` (can regenerate)

3. **Iterate incrementally**
   - Edit one task at a time
   - Test frequently
   - Use `set_liberoenv_addobject.sh` for single tasks

4. **Document your changes**
   - Add comments to BDDL files
   - Use descriptive suite names
   - Update `--description` in suite metadata

5. **Back up before bulk operations**
   ```bash
   cp -r bddl_files/libero_custom bddl_files/libero_custom.backup
   ```

---

## Additional Resources

- **BDDL Syntax:** See existing BDDL files for examples
- **Object Names:** Run `python scripts/analyze_libero_objects.py --taskset object`
- **Preserve Positions:** See `pi_setting/eval/preserve_exact_positions.py`
- **Visualization:** Check `init_files/<suite>/visualizations/` for scene previews

---

## Summary

Creating a custom LIBERO suite is now streamlined:

1. **One command** to create and register: `create_new_libero_suite.sh`
2. **Manual BDDL editing** (the creative part)
3. **One command** to regenerate all: `create_new_libero_suite.sh --regenerate_init_only`
4. **One command** to validate: `validate_libero_suite.sh`
5. **Ready to evaluate!**

Shell wrappers (`.sh`) provide easier usage. For advanced options, use the Python scripts directly.

For questions or issues, check the validation output first—it provides specific guidance on what's missing or misconfigured.
