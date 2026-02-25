#!/usr/bin/env python3
"""
Create a new LIBERO task suite by copying and registering a new benchmark.

This script automates the process of creating a custom LIBERO suite:
1. Creates folder structure (bddl_files/ and init_files/)
2. Copies BDDL and init files from source suite
3. Auto-updates registration files (libero_suite_task_map.py and __init__.py)
4. Provides instructions for manual BDDL editing
5. Optionally regenerates init files after BDDL modifications

Usage:
    # Create new suite
    python create_new_libero_suite.py \\
        --new_suite libero_unseen_object \\
        --copy_from libero_object \\
        --description "LIBERO Object tasks with unseen distractor objects"
    
    # After editing BDDL files, regenerate init files
    python create_new_libero_suite.py \\
        --new_suite libero_unseen_object \\
        --regenerate_init_only
"""

import argparse
import os
import shutil
import glob
import re
from pathlib import Path


def get_libero_base_path():
    """Get the base path to LIBERO library."""
    script_dir = Path(__file__).parent
    return script_dir.parent / "libero" / "libero"


def get_task_name_from_bddl(bddl_path):
    """Extract task name from BDDL filename."""
    return Path(bddl_path).stem


def get_all_tasks_in_suite(suite_name):
    """Get all task names for a given suite by scanning BDDL files."""
    base_path = get_libero_base_path()
    bddl_dir = base_path / "bddl_files" / suite_name
    
    if not bddl_dir.exists():
        return []
    
    tasks = []
    for bddl_file in sorted(bddl_dir.glob("*.bddl")):
        # Skip backup files
        if bddl_file.suffix == ".old" or ".bddl.old" in bddl_file.name:
            continue
        tasks.append(get_task_name_from_bddl(bddl_file))
    
    return tasks


def create_suite_folders(suite_name):
    """Create folder structure for new suite."""
    base_path = get_libero_base_path()
    
    bddl_dir = base_path / "bddl_files" / suite_name
    init_dir = base_path / "init_files" / suite_name
    
    bddl_dir.mkdir(parents=True, exist_ok=True)
    init_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Created directories:")
    print(f"   - {bddl_dir}")
    print(f"   - {init_dir}")
    
    return bddl_dir, init_dir


def copy_suite_files(source_suite, target_suite):
    """Copy all BDDL and init files from source suite to target suite."""
    base_path = get_libero_base_path()
    
    source_bddl = base_path / "bddl_files" / source_suite
    target_bddl = base_path / "bddl_files" / target_suite
    
    source_init = base_path / "init_files" / source_suite
    target_init = base_path / "init_files" / target_suite
    
    # Copy BDDL files and create .bddl.old backups
    copied_count = 0
    for bddl_file in source_bddl.glob("*.bddl"):
        if ".old" not in bddl_file.name:
            # Copy the BDDL file
            target_file = target_bddl / bddl_file.name
            shutil.copy2(bddl_file, target_file)
            
            # Also create .bddl.old backup (for set_liberoenv_addobject.sh)
            backup_file = target_bddl / f"{bddl_file.name}.old"
            shutil.copy2(bddl_file, backup_file)
            
            copied_count += 1
    
    print(f"✅ Copied {copied_count} BDDL files from {source_suite}")
    print(f"✅ Created {copied_count} .bddl.old backup files")
    
    # Copy init files
    init_count = 0
    for init_file in source_init.glob("*.init"):
        shutil.copy2(init_file, target_init / init_file.name)
        init_count += 1
    
    print(f"✅ Copied {init_count} init files from {source_suite}")
    
    return copied_count


def update_task_map(suite_name):
    """Add new suite to libero_suite_task_map.py."""
    base_path = get_libero_base_path()
    task_map_file = base_path / "benchmark" / "libero_suite_task_map.py"
    
    # Get all tasks in the suite
    tasks = get_all_tasks_in_suite(suite_name)
    
    if not tasks:
        print(f"⚠️  No tasks found for {suite_name}")
        return False
    
    # Read current file
    with open(task_map_file, 'r') as f:
        content = f.read()
    
    # Check if suite already exists
    if f'"{suite_name}":' in content:
        print(f"⚠️  Suite {suite_name} already exists in task_map.py")
        return True
    
    # Create task list string
    task_list_str = '    "' + suite_name + '": [\n'
    for task in tasks:
        task_list_str += f'        "{task}",\n'
    task_list_str += '    ],\n}'
    
    # Replace the closing brace
    new_content = content.rstrip()[:-1] + task_list_str
    
    # Write back
    with open(task_map_file, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Added {suite_name} to libero_suite_task_map.py ({len(tasks)} tasks)")
    return True


def update_benchmark_init(suite_name):
    """Add new suite to benchmark __init__.py."""
    base_path = get_libero_base_path()
    init_file = base_path / "benchmark" / "__init__.py"
    
    # Read current file
    with open(init_file, 'r') as f:
        content = f.read()
    
    # Check if already in libero_suites list
    if f'"{suite_name}"' in content and 'libero_suites' in content:
        # Verify it's actually in the list
        suites_match = re.search(r'libero_suites\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if suites_match and f'"{suite_name}"' in suites_match.group(1):
            print(f"⚠️  Suite {suite_name} already in libero_suites list")
        else:
            # Add to libero_suites list
            content = add_to_suites_list(content, suite_name)
    else:
        # Add to libero_suites list
        content = add_to_suites_list(content, suite_name)
    
    # Check if benchmark class exists
    class_name = "LIBERO_" + suite_name.upper().replace("LIBERO_", "")
    if f"class {class_name}" in content:
        print(f"⚠️  Benchmark class {class_name} already exists")
    else:
        # Add benchmark class at the end
        content = add_benchmark_class(content, suite_name)
    
    # Write back
    with open(init_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Registered {suite_name} in benchmark __init__.py")
    return True


def add_to_suites_list(content, suite_name):
    """Add suite to libero_suites list."""
    # Find the libero_suites list
    pattern = r'(libero_suites\s*=\s*\[)(.*?)(\])'
    
    def replacer(match):
        prefix = match.group(1)
        suites = match.group(2)
        suffix = match.group(3)
        
        # Add new suite to the end
        if suites.strip().endswith(','):
            new_suites = suites + f'\n    "{suite_name}",'
        else:
            new_suites = suites.rstrip() + f',\n    "{suite_name}",'
        
        return prefix + new_suites + '\n' + suffix
    
    return re.sub(pattern, replacer, content, flags=re.DOTALL)


def add_benchmark_class(content, suite_name):
    """Add benchmark class definition at the end of file."""
    class_name = "LIBERO_" + suite_name.upper().replace("LIBERO_", "")
    
    class_def = f'''

@register_benchmark
class {class_name}(Benchmark):
    def __init__(self, task_order_index=0):
        super().__init__(task_order_index=task_order_index)
        self.name = "{suite_name}"
        self._make_benchmark()
'''
    
    return content.rstrip() + class_def + '\n'


def validate_suite(suite_name):
    """Validate that the suite is properly set up."""
    base_path = get_libero_base_path()
    
    # Check folders exist
    bddl_dir = base_path / "bddl_files" / suite_name
    init_dir = base_path / "init_files" / suite_name
    
    if not bddl_dir.exists() or not init_dir.exists():
        print(f"❌ Directories missing for {suite_name}")
        return False
    
    # Check task map
    task_map_file = base_path / "benchmark" / "libero_suite_task_map.py"
    with open(task_map_file, 'r') as f:
        if f'"{suite_name}":' not in f.read():
            print(f"❌ Suite {suite_name} not found in task_map.py")
            return False
    
    # Check benchmark registration
    init_file = base_path / "benchmark" / "__init__.py"
    with open(init_file, 'r') as f:
        content = f.read()
        if f'"{suite_name}"' not in content:
            print(f"❌ Suite {suite_name} not registered in __init__.py")
            return False
    
    print(f"✅ Suite {suite_name} is properly configured")
    return True


def print_next_steps(suite_name, new_creation=True):
    """Print instructions for next steps."""
    base_path = get_libero_base_path()
    bddl_dir = base_path / "bddl_files" / suite_name
    
    print("\n" + "="*70)
    if new_creation:
        print("🎉 Suite creation complete!")
    else:
        print("✅ Init files regenerated!")
    print("="*70)
    
    if new_creation:
        print(f"\n📝 NEXT STEPS:")
        print(f"\n1. Edit BDDL files in:")
        print(f"   {bddl_dir}")
        print(f"\n2. After editing, regenerate init files:")
        print(f"   bash third_party/LIBERO/scripts/create_new_libero_suite.sh --new_suite {suite_name} --regenerate_init_only")
        print(f"\n3. Or regenerate individual tasks:")
        print(f"   bash third_party/LIBERO/scripts/set_liberoenv_addobject.sh {suite_name} <task_name>")
    
    print(f"\n4. Validate your suite:")
    print(f"   bash third_party/LIBERO/scripts/validate_libero_suite.sh {suite_name}")
    
    print(f"\n5. Test with evaluation:")
    print(f"   TASK_SUITE={suite_name} ./third_party/LIBERO/scripts/eval_libero_quick_test.sh")
    print("\n" + "="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Create and manage custom LIBERO task suites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--new_suite",
        type=str,
        required=True,
        help="Name of the new suite (e.g., libero_unseen_object)"
    )
    
    parser.add_argument(
        "--copy_from",
        type=str,
        help="Source suite to copy files from (e.g., libero_object)"
    )
    
    parser.add_argument(
        "--description",
        type=str,
        default="",
        help="Description of the new suite"
    )
    
    parser.add_argument(
        "--regenerate_init_only",
        action="store_true",
        help="Only regenerate init files (skip folder creation and file copying)"
    )
    
    parser.add_argument(
        "--skip_registration",
        action="store_true",
        help="Skip updating task_map.py and __init__.py (advanced)"
    )
    
    args = parser.parse_args()
    
    suite_name = args.new_suite
    
    print(f"\n{'='*70}")
    print(f"Creating LIBERO Suite: {suite_name}")
    if args.description:
        print(f"Description: {args.description}")
    print(f"{'='*70}\n")
    
    if args.regenerate_init_only:
        # Just regenerate init files
        print("🔄 Regenerating init files for existing suite...")
        from regenerate_all_tasks import regenerate_all_init_files
        success = regenerate_all_init_files(suite_name)
        if success:
            print_next_steps(suite_name, new_creation=False)
        return
    
    # Full suite creation
    if not args.copy_from:
        print("❌ Error: --copy_from is required for new suite creation")
        return
    
    # Step 1-2: Create folders and copy files
    print("\n📁 Step 1-2: Creating directories and copying files...")
    create_suite_folders(suite_name)
    copy_suite_files(args.copy_from, suite_name)
    
    # Step 5-6: Update registration files
    if not args.skip_registration:
        print("\n📝 Step 5-6: Updating registration files...")
        update_task_map(suite_name)
        update_benchmark_init(suite_name)
    
    # Validation
    print("\n🔍 Validating suite setup...")
    validate_suite(suite_name)
    
    # Print next steps
    print_next_steps(suite_name, new_creation=True)


if __name__ == "__main__":
    main()
