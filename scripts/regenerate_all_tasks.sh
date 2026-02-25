#!/bin/bash
# =============================================================================
# Batch Regenerate Init Files for All Tasks in a LIBERO Suite
# =============================================================================
#
# PURPOSE:
#   After editing multiple BDDL files in a suite, regenerate all .pruned_init
#   files at once instead of running set_liberoenv_addobject.sh repeatedly.
#
# USAGE:
#   ./regenerate_all_tasks.sh <suite_name>
#
# EXAMPLE:
#   ./regenerate_all_tasks.sh libero_unseen_object
#
# WHAT IT DOES:
#   1. Finds all BDDL files in the specified suite
#   2. For each task, runs set_liberoenv_addobject.sh
#   3. Generates all .pruned_init files with preserved positions
#
# =============================================================================

if [ $# -eq 0 ]; then
    echo "❌ Error: Missing suite name"
    echo ""
    echo "Usage: $0 <suite_name>"
    echo ""
    echo "Examples:"
    echo "  $0 libero_unseen_object"
    echo "  $0 libero_object"
    echo "  $0 libero_spatial"
    exit 1
fi

SUITE_NAME=$1
BDDL_DIR="/workspace/lerobot/third_party/LIBERO/libero/libero/bddl_files/$SUITE_NAME"

if [ ! -d "$BDDL_DIR" ]; then
    echo "❌ Error: Suite directory not found: $BDDL_DIR"
    exit 1
fi

echo "================================================"
echo "Batch Regenerating Init Files"
echo "================================================"
echo "Suite: $SUITE_NAME"
echo "BDDL Directory: $BDDL_DIR"
echo "================================================"
echo ""

# Count total tasks
TOTAL_TASKS=$(find "$BDDL_DIR" -name "*.bddl" ! -name "*.old" | wc -l)
echo "Found $TOTAL_TASKS tasks to process"
echo ""

# Process each BDDL file
CURRENT=0
FAILED=0
SUCCEEDED=0

for BDDL_FILE in "$BDDL_DIR"/*.bddl; do
    # Skip backup files
    if [[ "$BDDL_FILE" == *.old ]] || [[ "$BDDL_FILE" == *.bddl.old ]]; then
        continue
    fi
    
    CURRENT=$((CURRENT + 1))
    TASK_NAME=$(basename "$BDDL_FILE" .bddl)
    
    echo "[$CURRENT/$TOTAL_TASKS] Processing: $TASK_NAME"
    echo "----------------------------------------"
    
    # Run set_liberoenv_addobject.sh for this task
    if /workspace/lerobot/third_party/LIBERO/scripts/set_liberoenv_addobject.sh "$SUITE_NAME" "$TASK_NAME"; then
        SUCCEEDED=$((SUCCEEDED + 1))
        echo "✅ Success: $TASK_NAME"
    else
        FAILED=$((FAILED + 1))
        echo "❌ Failed: $TASK_NAME"
    fi
    
    echo ""
done

echo "================================================"
echo "Batch Processing Complete"
echo "================================================"
echo "Total:     $TOTAL_TASKS"
echo "Succeeded: $SUCCEEDED"
echo "Failed:    $FAILED"
echo "================================================"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo "🎉 All init files regenerated successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Validate: python scripts/validate_libero_suite.py --suite $SUITE_NAME"
    echo "  2. Test: TASK_SUITE=$SUITE_NAME ./pi_setting/eval/eval_libero_quick_test.sh"
    exit 0
else
    echo ""
    echo "⚠️  Some tasks failed. Check the logs above."
    exit 1
fi
