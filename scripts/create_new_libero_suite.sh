#!/bin/bash
# =============================================================================
# Create New LIBERO Suite - Wrapper Script
# =============================================================================
#
# This script provides a convenient shell wrapper for create_new_libero_suite.py
#
# USAGE:
#   # Create new suite
#   ./create_new_libero_suite.sh --new_suite <name> --copy_from <source>
#
#   # Regenerate init files only
#   ./create_new_libero_suite.sh --new_suite <name> --regenerate_init_only
#
# EXAMPLES:
#   ./create_new_libero_suite.sh \
#       --new_suite libero_unseen_object \
#       --copy_from libero_object \
#       --description "LIBERO Object tasks with unseen distractor objects"
#
#   ./create_new_libero_suite.sh \
#       --new_suite libero_unseen_object \
#       --regenerate_init_only
#
# =============================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run the Python script with all arguments passed through
python "$SCRIPT_DIR/create_new_libero_suite.py" "$@"
