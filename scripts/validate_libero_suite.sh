#!/bin/bash
# =============================================================================
# Validate LIBERO Suite - Wrapper Script
# =============================================================================
#
# This script provides a convenient shell wrapper for validate_libero_suite.py
#
# USAGE:
#   ./validate_libero_suite.sh <suite_name>
#
# EXAMPLES:
#   ./validate_libero_suite.sh libero_unseen_object
#   ./validate_libero_suite.sh libero_custom
#
# =============================================================================

if [ $# -eq 0 ]; then
    echo "❌ Error: Missing suite name"
    echo ""
    echo "Usage: $0 <suite_name>"
    echo ""
    echo "Examples:"
    echo "  $0 libero_unseen_object"
    echo "  $0 libero_custom"
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SUITE_NAME=$1

# Run the Python validation script
python "$SCRIPT_DIR/validate_libero_suite.py" --suite "$SUITE_NAME"
