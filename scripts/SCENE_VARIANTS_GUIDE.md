# Scene Variants Generation Guide

Generate multiple scene variants for LIBERO tasks by randomly swapping object positions while maintaining the same task command.

## Quick Start

### Option 1: Create New Suite (Recommended)

```bash
# Edit configuration in generate_scene_variants.sh:
CREATE_NEW_SUITE=true
NEW_SUITE_NAME="libero_object_variants"
SOURCE_SUITE="libero_object"

# Run script
bash third_party/LIBERO/scripts/generate_scene_variants.sh
```

This will:
1. ✅ Create `libero_object_variants` suite folders
2. ✅ Copy original BDDL and init files from `libero_object`
3. ✅ Generate variants (`task_0.bddl`, `task_1.bddl`, etc.) in the new suite
4. ✅ **Automatically register the suite in LIBERO** (new!)
5. ✅ Validate the suite setup
6. ✅ Keep original `libero_object` suite unchanged

### Option 2: Modify Original Suite (Legacy)

```bash
# Edit configuration in generate_scene_variants.sh:
CREATE_NEW_SUITE=false
GROUP=libero_object

# Run script
bash third_party/LIBERO/scripts/generate_scene_variants.sh
```

This modifies the original suite in-place (not recommended for production).

---

## What Are Scene Variants?

Scene variants maintain the **same task command** but change **WHERE objects are placed**:

**Original Task:** "pick_up_the_alphabet_soup_and_place_it_in_the_basket"

- **Variant 0** (baseline): alphabet_soup at original position, basket at original position
- **Variant 1**: alphabet_soup at butter's position → robot picks from different location
- **Variant 2**: basket at plate's position → robot places at different location  
- **Variant 3**: both swapped → completely different scene layout

All variants share the same task_id and are evaluated in different episodes.

---

## Configuration

Edit `generate_scene_variants.sh`:

```bash
# Suite creation mode
CREATE_NEW_SUITE=true                      # true = new suite, false = modify original
NEW_SUITE_NAME="libero_object_variants"    # Name for new suite
SOURCE_SUITE="libero_object"               # Source to copy from
SKIP_REGISTRATION=false                    # Set true to skip auto-registration (advanced)

# Variant types and counts
N_TARGET_OBJECT=2        # Swap pickup target (e.g., soup ↔ butter)
N_TARGET_LOCATION=2      # Swap place target (e.g., basket ↔ plate)
N_BOTH_OBJECT_TARGET=2   # Swap both targets

# Init states per variant
NUM_INIT_STATES=10       # 10 for testing, 50 for production

# Reproducibility
DETERMINISTIC=true       # true = same scenes every run, false = random

# Task selection
TASK_LIST=(
    pick_up_the_alphabet_soup_and_place_it_in_the_basket
    pick_up_the_bbq_sauce_and_place_it_in_the_basket
    # ... add more tasks
)
```

---

## Python Script Usage

For more control, use the Python script directly:

### Create Suite and Generate All Variants

```bash
python third_party/LIBERO/scripts/generate_scene_variants.py \
    --create_new_suite libero_object_variants \
    --copy_from libero_object \
    --all_tasks \
    --n_target_object 2 \
    --n_target_location 2 \
    --n_both_object_target 2 \
    --num_init_states 10 \
    --deterministic
```

**Note**: Suite is automatically registered in LIBERO. Use `--skip_registration` to disable.

### Create Suite and Generate for Single Task

```bash
python third_party/LIBERO/scripts/generate_scene_variants.py \
    --create_new_suite libero_object_variants \
    --copy_from libero_object \
    --task pick_up_the_alphabet_soup_and_place_it_in_the_basket \
    --n_target_object 2 \
    --n_target_location 2 \
    --n_both_object_target 2 \
    --num_init_states 10 \
    --deterministic
```

### Generate Variants for Specific File (Original Behavior)

```bash
python third_party/LIBERO/scripts/generate_scene_variants.py \
    --bddl /path/to/task.bddl \
    --init /path/to/task.init \
    --n_target_object 2 \
    --n_target_location 2 \
    --n_both_object_target 2 \
    --num_init_states 10 \
    --deterministic
```

---

## Output Structure

### New Suite Mode

```
libero/libero/
├── bddl_files/
│   └── libero_object_variants/
│       ├── pick_up_the_alphabet_soup_and_place_it_in_the_basket.bddl          # Original
│       ├── pick_up_the_alphabet_soup_and_place_it_in_the_basket_0.bddl        # Variant 0 (copy)
│       ├── pick_up_the_alphabet_soup_and_place_it_in_the_basket_1.bddl        # Variant 1
│       ├── pick_up_the_alphabet_soup_and_place_it_in_the_basket_2.bddl        # Variant 2
│       └── ...
│
└── init_files/
    └── libero_object_variants/
        ├── pick_up_the_alphabet_soup_and_place_it_in_the_basket.init          # Original
        ├── pick_up_the_alphabet_soup_and_place_it_in_the_basket_0.init        # Variant 0
        ├── pick_up_the_alphabet_soup_and_place_it_in_the_basket_1.init        # Variant 1
        └── variant_visualizations/
            └── pick_up_the_alphabet_soup_and_place_it_in_the_basket/
                ├── variant_0.png
                ├── variant_1.png
                └── ...
```

---

## Variant Types Explained

Given a task with:
- **Pickup target**: `alphabet_soup_1`
- **Place target**: `basket_1`
- **Non-interest objects**: `butter_1`, `plate_1`, `mug_1`, etc.

### Type 1: Target Object Variants (N_TARGET_OBJECT=2)

Swap **pickup target** with non-interest objects:

- Variant 1: `alphabet_soup_1` ↔ `butter_1` positions
- Variant 2: `alphabet_soup_1` ↔ `plate_1` positions

**Result**: Robot must pick up from different locations (but still picks alphabet_soup)

### Type 2: Target Location Variants (N_TARGET_LOCATION=2)

Swap **place target** with non-interest objects:

- Variant 1: `basket_1` ↔ `plate_1` positions
- Variant 2: `basket_1` ↔ `mug_1` positions

**Result**: Robot must place at different locations (but still places in basket)

### Type 3: Both Targets Variants (N_BOTH_OBJECT_TARGET=2)

Swap **both pickup and place targets**:

- Variant 1: `alphabet_soup_1` ↔ `butter_1` AND `basket_1` ↔ `plate_1`
- Variant 2: `alphabet_soup_1` ↔ `mug_1` AND `basket_1` ↔ `cream_cheese_1`

**Result**: Completely different scene layouts

### Variant 0 (Baseline)

If `--create_variant_0` is enabled (default), a copy of the original scene is created as `task_0.bddl` and `task_0.init`.

**Total variants**: `N_TARGET_OBJECT + N_TARGET_LOCATION + N_BOTH_OBJECT_TARGET + 1`

Example: `2 + 2 + 2 + 1 = 7 variants`

---

## Using Variants in Evaluation

Variants are automatically used when evaluating with `env.init_states=true`:

```bash
# Evaluate on scene variants
TASK_SUITE=libero_object_variants \
    bash uncertainty_quantification/scripts/eval_libero_with_uncertainty.sh
```

Or specify which variants to use:

```bash
lerobot-eval \
    --env.type=libero \
    --env.task=libero_object_variants \
    --env.task_ids='[0,1,2,3,4,5,6]' \
    --eval.n_episodes=7 \
    --policy.path=lerobot/pi05_libero_finetuned \
    --env.init_states=true
```

Each episode uses a different variant (different scene layout, same task).

---

## After Creating Variants

### 1. Validate the Suite (Recommended)

The suite is automatically registered, so you can immediately validate it:

```bash
bash third_party/LIBERO/scripts/validate_libero_suite.sh libero_object_variants
```

### 2. Test Evaluation

```bash
TASK_SUITE=libero_object_variants \
    ./third_party/LIBERO/scripts/eval_libero_quick_test.sh
```

---

## Deterministic vs Random

### Deterministic Mode (`DETERMINISTIC=true`)

- Uses fixed random seeds (base_seed=42)
- Same scene layouts every run
- Reproducible for benchmarking
- Recommended for research

### Random Mode (`DETERMINISTIC=false`)

- No fixed seeds
- Different layouts every run
- More diverse scenes
- Good for data augmentation

---

## Troubleshooting

### Issue: "Randomization failed"

**Cause**: Object placement constraints conflict (object too big for region)

**Fix**: Reduce number of variants or modify BDDL regions

### Issue: Variants look identical

**Cause**: Non-interest objects are in similar positions

**Fix**: Increase object diversity in BDDL or use more init states

### Issue: Missing files in new suite

**Cause**: Source suite has incomplete files

**Fix**: Check source suite has all `.bddl` and `.init` files

---

## Examples

### Example 1: Create 3 Variants for Testing

```bash
# Quick test with 3 variants
python generate_scene_variants.py \
    --create_new_suite libero_object_test \
    --copy_from libero_object \
    --task pick_up_the_alphabet_soup_and_place_it_in_the_basket \
    --n_target_object 1 \
    --n_target_location 1 \
    --n_both_object_target 1 \
    --num_init_states 10 \
    --deterministic
```

### Example 2: Full Suite with 50 Init States

```bash
# Production-ready suite
python generate_scene_variants.py \
    --create_new_suite libero_object_full \
    --copy_from libero_object \
    --all_tasks \
    --n_target_object 3 \
    --n_target_location 3 \
    --n_both_object_target 3 \
    --num_init_states 50 \
    --deterministic
```

### Example 3: Random Variants for Data Augmentation

```bash
# Random scenes (no deterministic)
python generate_scene_variants.py \
    --create_new_suite libero_object_random \
    --copy_from libero_object \
    --all_tasks \
    --n_target_object 5 \
    --n_target_location 5 \
    --n_both_object_target 5 \
    --num_init_states 20
# (no --deterministic flag)
```

---

## Comparison with create_new_libero_suite.sh

| Feature | create_new_libero_suite.sh | generate_scene_variants.sh |
|---------|---------------------------|---------------------------|
| **Purpose** | Create suite with BDDL modifications | Create suite with position swaps |
| **BDDL Changes** | Manual editing (add/remove objects) | Automatic swapping (object→region) |
| **Init Files** | Regenerated from modified BDDL | Regenerated with swapped positions |
| **Use Case** | Adding distractor objects | Varying scene layouts |
| **Variants** | 1 version per task | Multiple variants per task |
| **Registration** | Includes registration helpers | Manual registration needed |

**Recommendation**: Use `create_new_libero_suite.sh` for semantic changes (different objects), use `generate_scene_variants.sh` for spatial changes (different positions).

---

## Summary

✅ **Recommended workflow**:
1. Set `CREATE_NEW_SUITE=true` in `generate_scene_variants.sh`
2. Configure suite name and variant counts
3. Run `bash generate_scene_variants.sh`
4. **Suite is automatically registered!** (no manual steps needed)
5. Validate with `validate_libero_suite.sh`
6. Test with evaluation

✅ **Benefits**:
- Clean separation from original suite
- Multiple scene layouts per task
- Same task command across variants
- **Automatic suite registration** (new!)
- Easy evaluation with `env.init_states=true`

⚠️ **Advanced**: Use `SKIP_REGISTRATION=true` or `--skip_registration` to disable automatic registration.
