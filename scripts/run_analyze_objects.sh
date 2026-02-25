#!/bin/bash
# Script to analyze LIBERO objects across task sets
# Usage: ./run_analyze_objects.sh

# Configuration - modify these as needed
TASKSET="object"  # Options: object, spatial, goal, long_10, long_90
# BDDL_PATH=""    # Uncomment and set custom path if needed

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/analyze_libero_objects.py"

# Build command
CMD="python $PYTHON_SCRIPT --taskset $TASKSET"

# Add custom path if specified
if [ -n "$BDDL_PATH" ]; then
    CMD="$CMD --path $BDDL_PATH"
fi

# Run the analysis
echo "Running LIBERO object analysis..."
echo "Command: $CMD"
echo ""
$CMD
