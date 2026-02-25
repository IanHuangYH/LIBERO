#!/bin/bash
# =============================================================================
# LIBERO Scene Variant Generation Script
# =============================================================================
#
# PURPOSE:
#   Generate multiple scene variants for LIBERO tasks by swapping object positions.
#   Each variant maintains the same task definition but changes WHERE objects are placed.
#
# NEW: Can create a new suite folder first (like create_new_libero_suite.sh)
#
# MODES:
#   1. ORIGINAL: Generate variants in existing suite folder (modify in-place)
#   2. NEW: Create new suite and generate variants there (cleaner separation)
#
# WHAT IT DOES:
#   1. [NEW MODE ONLY] Creates new suite by copying from source suite
#   2. For each task in TASK_LIST:
#      - Creates variant BDDL files with swapped object→region assignments
#      - Regenerates init states (object positions/velocities) for each variant
#      - Visualizes each variant scene
#
#   3. Three types of variants are generated:
#      a) N_TARGET_OBJECT variants: Swap the PICKUP target with non-interest objects
#         (e.g., alphabet_soup ↔ butter, so robot must pick up butter instead)
#      
#      b) N_TARGET_LOCATION variants: Swap the PLACE target with non-interest objects
#         (e.g., basket ↔ plate, so robot must place in plate instead)
#      
#      c) N_BOTH_OBJECT_TARGET variants: Swap BOTH pickup and place targets
#         (e.g., alphabet_soup ↔ butter AND basket ↔ plate)
#
#   4. Creates variant_0 as copy of original scene (no changes)
#
# OUTPUT FILES (NEW MODE):
#   - Suite folders: /path/to/{NEW_SUITE}/bddl_files/ and init_files/
#   - BDDL files: {task_name}_0.bddl, {task_name}_1.bddl, ...
#   - Init files: {task_name}_0.init, {task_name}_1.init, ...
#   - Visualizations: init_files/variant_visualizations/{task}/variant_XXX.png
#
# OUTPUT FILES (ORIGINAL MODE):
#   - BDDL files: /path/to/bddl_files/{task_name}_0.bddl, {task_name}_1.bddl, ...
#   - Init files: /path/to/init_files/{task_name}_0.init, {task_name}_1.init, ...
#   - Visualizations: /path/to/init_files/variant_visualizations/{task}/variant_XXX.png
#
# DETERMINISTIC MODE:
#   - Set DETERMINISTIC=true for reproducible init states (same scenes every run)
#   - Set DETERMINISTIC=false for random variations (different placements each run)
#
# EXAMPLE:
#   Original task: "pick_up_the_alphabet_soup_and_place_it_in_the_basket"
#   Variant 1: alphabet_soup at butter's location → robot picks up from different spot
#   Variant 2: basket at plate's location → robot places at different spot
#   Variant 3: both swapped → completely different scene layout
#
# =============================================================================

# =============================================================================
# CONFIGURATION
# =============================================================================

# NEW MODE: Set to create a new suite (recommended for cleaner separation)
CREATE_NEW_SUITE=true              # true = create new suite, false = modify original
NEW_SUITE_NAME="libero_object_variants"   # Name for the new suite (only used if CREATE_NEW_SUITE=true)
SOURCE_SUITE="libero_object"       # Source suite to copy from (only used if CREATE_NEW_SUITE=true)
SKIP_REGISTRATION=false            # Set to true to skip automatic registration (advanced)

# ORIGINAL MODE: Set group (only used if CREATE_NEW_SUITE=false)
GROUP=libero_object

DETERMINISTIC=true    # Set to true for reproducible init states (same scenes every run)
# Variant generation parameters
N_TARGET_OBJECT=2      # Number of variants swapping pickup target
N_TARGET_LOCATION=2    # Number of variants swapping place target  
N_BOTH_OBJECT_TARGET=2 # Number of variants swapping both targets
NUM_INIT_STATES=10     # Number of init states per variant (10 for speed, 50 for production)

# Task list - can be modified to process specific tasks
TASK_LIST=(
    pick_up_the_alphabet_soup_and_place_it_in_the_basket
    pick_up_the_bbq_sauce_and_place_it_in_the_basket
    pick_up_the_butter_and_place_it_in_the_basket
    pick_up_the_chocolate_pudding_and_place_it_in_the_basket
    pick_up_the_cream_cheese_and_place_it_in_the_basket
    pick_up_the_ketchup_and_place_it_in_the_basket
    pick_up_the_milk_and_place_it_in_the_basket
    pick_up_the_orange_juice_and_place_it_in_the_basket
    pick_up_the_salad_dressing_and_place_it_in_the_basket
    pick_up_the_tomato_sauce_and_place_it_in_the_basket
)

# =============================================================================
# MAIN EXECUTION
# =============================================================================

# Build deterministic flag
DETERMINISTIC_FLAG=""
if [ "$DETERMINISTIC" = "true" ]; then
    DETERMINISTIC_FLAG="--deterministic"
fi

# Build registration flag
REGISTRATION_FLAG=""
if [ "$SKIP_REGISTRATION" = "true" ]; then
    REGISTRATION_FLAG="--skip_registration"
fi

# MODE 1: Create new suite and generate variants there
if [ "$CREATE_NEW_SUITE" = "true" ]; then
    echo "================================================================================"
    echo "MODE: Creating new suite and generating variants"
    echo "================================================================================"
    echo "  Source suite: $SOURCE_SUITE"
    echo "  New suite: $NEW_SUITE_NAME"
    echo "  Processing ${#TASK_LIST[@]} tasks"
    echo "================================================================================"
    echo ""
    
    cd /workspace/lerobot/third_party/LIBERO/scripts
    
    python3 generate_scene_variants.py \
        --create_new_suite $NEW_SUITE_NAME \
        --copy_from $SOURCE_SUITE \
        --all_tasks \
        --n_target_object $N_TARGET_OBJECT \
        --n_target_location $N_TARGET_LOCATION \
        --n_both_object_target $N_BOTH_OBJECT_TARGET \
        --num_init_states $NUM_INIT_STATES \
        --create_variant_0 \
        $DETERMINISTIC_FLAG \
        $REGISTRATION_FLAG
    
    echo ""
    echo "================================================================================"
    echo "✅ COMPLETED"
    echo "================================================================================"
    echo "Suite created at:"
    echo "  /workspace/lerobot/third_party/LIBERO/libero/libero/bddl_files/$NEW_SUITE_NAME"
    echo "  /workspace/lerobot/third_party/LIBERO/libero/libero/init_files/$NEW_SUITE_NAME"
    echo ""
    if [ "$SKIP_REGISTRATION" = "true" ]; then
        echo "⚠️  Suite was NOT registered (--skip_registration)"
        echo "Next steps:"
        echo "  1. Register manually in libero_suite_task_map.py and __init__.py"
        echo "  2. Validate: bash scripts/validate_libero_suite.sh $NEW_SUITE_NAME"
    else
        echo "✅ Suite registered and ready to use!"
        echo "Next steps:"
        echo "  1. Validate: bash scripts/validate_libero_suite.sh $NEW_SUITE_NAME"
        echo "  2. Test: TASK_SUITE=$NEW_SUITE_NAME ./eval_libero_quick_test.sh"
    fi
    echo "================================================================================"

# MODE 2: Generate variants in original suite folder (legacy behavior)
else
    echo "================================================================================"
    echo "MODE: Generating variants in original suite folder"
    echo "================================================================================"
    echo "  Suite: $GROUP"
    echo "  Processing ${#TASK_LIST[@]} tasks"
    echo "================================================================================"
    echo ""
    
    # Paths
    BDDL_DIR=/workspace/lerobot/third_party/LIBERO/libero/libero/bddl_files/$GROUP
    INIT_DIR=/workspace/lerobot/third_party/LIBERO/libero/libero/init_files/$GROUP

    for TASK in "${TASK_LIST[@]}"; do
        echo "Generating variants for task: $TASK"

        BDDL_FILE=$BDDL_DIR/$TASK.bddl
        INIT_FILE=$INIT_DIR/$TASK.init
        OUTPUT_VIS_DIR=$INIT_DIR/variant_visualizations/$TASK

        # Run the scene variant generation (will create variant_0 and visualize all variants)
        cd /workspace/lerobot/third_party/LIBERO/scripts && python3 generate_scene_variants.py \
            --bddl $BDDL_FILE \
            --init $INIT_FILE \
            --n_target_object $N_TARGET_OBJECT \
            --n_target_location $N_TARGET_LOCATION \
            --n_both_object_target $N_BOTH_OBJECT_TARGET \
            --num_init_states $NUM_INIT_STATES \
            --output_dir $OUTPUT_VIS_DIR \
            --create_variant_0 \
            $DETERMINISTIC_FLAG
    done
    
    echo ""
    echo "================================================================================"
    echo "✅ COMPLETED"
    echo "================================================================================"
fi



