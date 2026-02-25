#!/usr/bin/env python3
"""
Validate a LIBERO suite setup.

Checks that all required files exist and are properly registered.

Usage:
    python validate_libero_suite.py --suite libero_unseen_object
"""

import argparse
import sys
from pathlib import Path
import re


def get_libero_base_path():
    """Get the base path to LIBERO library."""
    script_dir = Path(__file__).parent
    return script_dir.parent / "libero" / "libero"


class SuiteValidator:
    """Validates LIBERO suite setup."""
    
    def __init__(self, suite_name):
        self.suite_name = suite_name
        self.base_path = get_libero_base_path()
        self.errors = []
        self.warnings = []
        self.info = []
        
    def check_directories(self):
        """Check that required directories exist."""
        print("📁 Checking directories...")
        
        bddl_dir = self.base_path / "bddl_files" / self.suite_name
        init_dir = self.base_path / "init_files" / self.suite_name
        
        if not bddl_dir.exists():
            self.errors.append(f"BDDL directory not found: {bddl_dir}")
            return False
        else:
            self.info.append(f"✓ BDDL directory exists: {bddl_dir}")
        
        if not init_dir.exists():
            self.errors.append(f"Init directory not found: {init_dir}")
            return False
        else:
            self.info.append(f"✓ Init directory exists: {init_dir}")
        
        return True
    
    def check_files(self):
        """Check that required files exist for each task."""
        print("📄 Checking task files...")
        
        bddl_dir = self.base_path / "bddl_files" / self.suite_name
        init_dir = self.base_path / "init_files" / self.suite_name
        
        # Get all BDDL files (excluding backups)
        bddl_files = sorted([
            f for f in bddl_dir.glob("*.bddl")
            if ".old" not in f.name
        ])
        
        if not bddl_files:
            self.errors.append(f"No BDDL files found in {bddl_dir}")
            return False
        
        self.info.append(f"✓ Found {len(bddl_files)} BDDL files")
        
        missing_init = []
        missing_pruned = []
        
        for bddl_file in bddl_files:
            task_name = bddl_file.stem
            
            # Check for .init file
            init_file = init_dir / f"{task_name}.init"
            if not init_file.exists():
                missing_init.append(task_name)
            
            # Check for .pruned_init file
            pruned_file = init_dir / f"{task_name}.pruned_init"
            if not pruned_file.exists():
                missing_pruned.append(task_name)
        
        if missing_init:
            self.errors.append(f"Missing .init files for {len(missing_init)} tasks: {missing_init[:3]}...")
        else:
            self.info.append(f"✓ All tasks have .init files")
        
        if missing_pruned:
            self.warnings.append(f"Missing .pruned_init files for {len(missing_pruned)} tasks")
            self.warnings.append(f"  Run: python scripts/regenerate_all_tasks.py --suite {self.suite_name}")
        else:
            self.info.append(f"✓ All tasks have .pruned_init files")
        
        return len(missing_init) == 0
    
    def check_task_map(self):
        """Check if suite is registered in task_map.py."""
        print("🗺️  Checking task_map registration...")
        
        task_map_file = self.base_path / "benchmark" / "libero_suite_task_map.py"
        
        if not task_map_file.exists():
            self.errors.append(f"Task map file not found: {task_map_file}")
            return False
        
        with open(task_map_file, 'r') as f:
            content = f.read()
        
        # Check if suite exists in task map
        if f'"{self.suite_name}":' not in content:
            self.errors.append(f"Suite '{self.suite_name}' not found in libero_suite_task_map.py")
            self.errors.append(f"  Add an entry for '{self.suite_name}' in {task_map_file}")
            return False
        
        # Extract task list from task map
        pattern = rf'"{self.suite_name}":\s*\[(.*?)\]'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            task_list_str = match.group(1)
            tasks_in_map = re.findall(r'"([^"]+)"', task_list_str)
            
            # Get tasks from BDDL files
            bddl_dir = self.base_path / "bddl_files" / self.suite_name
            bddl_files = sorted([
                f.stem for f in bddl_dir.glob("*.bddl")
                if ".old" not in f.name
            ])
            
            if set(tasks_in_map) == set(bddl_files):
                self.info.append(f"✓ Task map contains all {len(tasks_in_map)} tasks")
            else:
                missing = set(bddl_files) - set(tasks_in_map)
                extra = set(tasks_in_map) - set(bddl_files)
                
                if missing:
                    self.warnings.append(f"Tasks in BDDL but not in task_map: {missing}")
                if extra:
                    self.warnings.append(f"Tasks in task_map but no BDDL: {extra}")
        
        return True
    
    def check_benchmark_registration(self):
        """Check if suite is registered in benchmark __init__.py."""
        print("📝 Checking benchmark registration...")
        
        init_file = self.base_path / "benchmark" / "__init__.py"
        
        if not init_file.exists():
            self.errors.append(f"Benchmark init file not found: {init_file}")
            return False
        
        with open(init_file, 'r') as f:
            content = f.read()
        
        # Check if suite is in libero_suites list
        suites_match = re.search(r'libero_suites\s*=\s*\[(.*?)\]', content, re.DOTALL)
        
        if suites_match:
            suites_str = suites_match.group(1)
            if f'"{self.suite_name}"' in suites_str:
                self.info.append(f"✓ Suite in libero_suites list")
            else:
                self.errors.append(f"Suite '{self.suite_name}' not in libero_suites list")
                self.errors.append(f"  Add '{self.suite_name}' to libero_suites in {init_file}")
                return False
        else:
            self.errors.append("Could not find libero_suites list in __init__.py")
            return False
        
        # Check if benchmark class exists
        class_name = "LIBERO_" + self.suite_name.upper().replace("LIBERO_", "")
        
        if f"class {class_name}(" in content:
            self.info.append(f"✓ Benchmark class {class_name} exists")
        else:
            self.errors.append(f"Benchmark class '{class_name}' not found")
            self.errors.append(f"  Add @register_benchmark class definition in {init_file}")
            return False
        
        return True
    
    def check_can_import(self):
        """Try to import the benchmark."""
        print("🐍 Checking Python import...")
        
        try:
            # Add LIBERO root directory to path (third_party/LIBERO/)
            import sys
            libero_root = self.base_path.parent.parent  # Go up from libero/libero/ to LIBERO/
            sys.path.insert(0, str(libero_root))
            
            from libero.libero import benchmark
            
            # Get benchmark dict
            bench_dict = benchmark.get_benchmark_dict()
            
            # Check if suite is in the dict
            # Benchmark keys are lowercase class names: LIBERO_UNSEEN_OBJECT_2 -> libero_unseen_object_2
            suite_key = self.suite_name.lower()
            
            if suite_key in bench_dict:
                self.info.append(f"✓ Suite '{self.suite_name}' can be imported")
                
                # Try to instantiate
                try:
                    suite_obj = bench_dict[suite_key]()
                    task_count = suite_obj.get_num_tasks()
                    self.info.append(f"✓ Suite has {task_count} tasks")
                except Exception as e:
                    self.errors.append(f"Failed to instantiate suite: {e}")
                    return False
            else:
                self.errors.append(f"Suite '{self.suite_name}' not in benchmark dict")
                self.errors.append(f"  Available: {list(bench_dict.keys())}")
                return False
            
        except Exception as e:
            self.errors.append(f"Failed to import benchmark: {e}")
            return False
        
        return True
    
    def validate(self):
        """Run all validation checks."""
        print("=" * 70)
        print(f"Validating LIBERO Suite: {self.suite_name}")
        print("=" * 70)
        print()
        
        all_passed = True
        
        all_passed &= self.check_directories()
        all_passed &= self.check_files()
        all_passed &= self.check_task_map()
        all_passed &= self.check_benchmark_registration()
        all_passed &= self.check_can_import()
        
        print()
        print("=" * 70)
        print("Validation Results")
        print("=" * 70)
        
        if self.info:
            print("\n✅ Info:")
            for msg in self.info:
                print(f"  {msg}")
        
        if self.warnings:
            print("\n⚠️  Warnings:")
            for msg in self.warnings:
                print(f"  {msg}")
        
        if self.errors:
            print("\n❌ Errors:")
            for msg in self.errors:
                print(f"  {msg}")
        
        print("\n" + "=" * 70)
        
        if all_passed and not self.errors:
            print("✅ VALIDATION PASSED")
            print("=" * 70)
            print()
            print("Your suite is ready to use!")
            print(f"\nTest with: TASK_SUITE={self.suite_name} ./pi_setting/eval/eval_libero_quick_test.sh")
            print()
            return True
        else:
            print("❌ VALIDATION FAILED")
            print("=" * 70)
            print()
            print("Please fix the errors above before using this suite.")
            print()
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Validate LIBERO suite setup",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--suite",
        type=str,
        required=True,
        help="Name of the suite to validate (e.g., libero_unseen_object)"
    )
    
    args = parser.parse_args()
    
    validator = SuiteValidator(args.suite)
    success = validator.validate()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
