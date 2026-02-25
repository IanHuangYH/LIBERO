#!/usr/bin/env python3
"""
Batch regenerate init files for all tasks in a LIBERO suite.

This is an alternative to running set_liberoenv_addobject.sh multiple times.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def get_libero_base_path():
    """Get the base path to LIBERO library."""
    script_dir = Path(__file__).parent
    return script_dir / ".."  / "libero" / "libero"


def regenerate_all_init_files(suite_name, verbose=True):
    """Regenerate all init files for a suite."""
    base_path = get_libero_base_path()
    bddl_dir = base_path / "bddl_files" / suite_name
    
    print("base_path=",base_path)
    print("bddl_dir=",bddl_dir)
    
    if not bddl_dir.exists():
        print(f"❌ Error: Suite directory not found: {bddl_dir}")
        return False
    
    # Find all BDDL files
    bddl_files = sorted([
        f for f in bddl_dir.glob("*.bddl")
        if ".old" not in f.name
    ])
    
    if not bddl_files:
        print(f"❌ No BDDL files found in {bddl_dir}")
        return False
    
    if verbose:
        print("=" * 70)
        print(f"Batch Regenerating Init Files")
        print("=" * 70)
        print(f"Suite: {suite_name}")
        print(f"Found {len(bddl_files)} tasks to process")
        print("=" * 70)
        print()
    
    script_path = Path(__file__).parent / "set_liberoenv_addobject.sh"
    
    succeeded = 0
    failed = 0
    
    for idx, bddl_file in enumerate(bddl_files, 1):
        task_name = bddl_file.stem
        
        if verbose:
            print(f"[{idx}/{len(bddl_files)}] Processing: {task_name}")
            print("-" * 70)
        
        # Run set_liberoenv_addobject.sh for this task
        try:
            result = subprocess.run(
                ["bash", str(script_path), suite_name, task_name],
                capture_output=not verbose,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                succeeded += 1
                if verbose:
                    print(f"✅ Success: {task_name}\n")
            else:
                failed += 1
                if verbose:
                    print(f"❌ Failed: {task_name}")
                    if result.stderr:
                        print(f"Error: {result.stderr}")
                    print()
        except Exception as e:
            failed += 1
            if verbose:
                print(f"❌ Exception for {task_name}: {e}\n")
    
    if verbose:
        print("=" * 70)
        print("Batch Processing Complete")
        print("=" * 70)
        print(f"Total:     {len(bddl_files)}")
        print(f"Succeeded: {succeeded}")
        print(f"Failed:    {failed}")
        print("=" * 70)
    
    return failed == 0


def main():
    parser = argparse.ArgumentParser(
        description="Batch regenerate init files for all tasks in a LIBERO suite"
    )
    
    parser.add_argument(
        "--suite",
        type=str,
        required=True,
        help="Name of the suite (e.g., libero_unseen_object)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress verbose output"
    )
    
    args = parser.parse_args()
    
    success = regenerate_all_init_files(args.suite, verbose=not args.quiet)
    
    if success:
        print("\n🎉 All init files regenerated successfully!\n")
        sys.exit(0)
    else:
        print("\n⚠️  Some tasks failed. Check the logs above.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
