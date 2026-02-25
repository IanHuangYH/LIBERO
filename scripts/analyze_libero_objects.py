#!/usr/bin/env python3
"""
Analyze objects used across different LIBERO task sets to identify unseen objects.
"""
import re
import argparse
from pathlib import Path
from collections import defaultdict

def parse_bddl_objects(bddl_path):
    """
    Parse BDDL file to extract object names from :objects section.
    
    Returns:
        set: Object names (e.g., 'alphabet_soup', 'plate', 'basket')
    """
    objects = set()
    
    with open(bddl_path, 'r') as f:
        content = f.read()
    
    # Find :objects section
    objects_match = re.search(r'\(:objects\s+(.*?)\s+\)', content, re.DOTALL)
    if not objects_match:
        return objects
    
    objects_section = objects_match.group(1)
    
    # Parse object declarations
    # Format: object_name_1 - object_type
    # Example: alphabet_soup_1 - alphabet_soup
    object_lines = re.findall(r'(\w+)_\d+\s+-\s+(\w+)', objects_section)
    
    for instance_name, object_type in object_lines:
        objects.add(object_type)
    
    return objects


def analyze_libero_objects(libero_bddl_dir, target_taskset='libero_object'):
    """
    Analyze objects across all LIBERO task sets.
    
    Args:
        libero_bddl_dir: Path to LIBERO bddl_files directory
        target_taskset: Task set to analyze (compare against others)
    """
    bddl_dir = Path(libero_bddl_dir)
    
    # Task sets to analyze
    task_sets = ['libero_object', 'libero_spatial', 'libero_goal', 'libero_10', 'libero_90']
    
    # Collect objects per task set
    objects_by_taskset = {}
    all_objects = set()
    
    print("=" * 80)
    print("ANALYZING LIBERO OBJECTS ACROSS TASK SETS")
    print("=" * 80)
    
    for task_set in task_sets:
        task_dir = bddl_dir / task_set
        if not task_dir.exists():
            print(f"\n⚠️  {task_set} not found, skipping...")
            continue
        
        print(f"\n📁 {task_set}")
        print("-" * 80)
        
        objects = set()
        bddl_files = list(task_dir.glob("*.bddl"))
        
        for bddl_file in bddl_files:
            file_objects = parse_bddl_objects(bddl_file)
            objects.update(file_objects)
        
        objects_by_taskset[task_set] = objects
        all_objects.update(objects)
        
        print(f"  Tasks: {len(bddl_files)}")
        print(f"  Objects: {sorted(objects)}")
        print(f"  Count: {len(objects)}")
    
    # Analysis
    print("\n" + "=" * 80)
    print("OBJECT ANALYSIS")
    print("=" * 80)
    
    if target_taskset not in objects_by_taskset:
        print(f"\n❌ ERROR: Target task set '{target_taskset}' not found!")
        print(f"   Available task sets: {list(objects_by_taskset.keys())}")
        return
    
    target_objects = objects_by_taskset[target_taskset]
    
    # Objects in other tasks but NOT in target task
    other_task_objects = set()
    for task_set, objects in objects_by_taskset.items():
        if task_set != target_taskset:
            other_task_objects.update(objects)
    
    unseen_objects = other_task_objects - target_objects
    common_objects = other_task_objects & target_objects
    
    print(f"\n✅ Objects in {target_taskset} tasks ({len(target_objects)}):")
    for obj in sorted(target_objects):
        print(f"   - {obj}")
    
    print(f"\n🔍 Objects in OTHER tasks but NOT in {target_taskset} ({len(unseen_objects)}):")
    if unseen_objects:
        # Show which task sets use each unseen object
        for obj in sorted(unseen_objects):
            task_sets_using = [ts for ts, objs in objects_by_taskset.items() 
                             if ts != target_taskset and obj in objs]
            print(f"   - {obj:30s} (used in: {', '.join(task_sets_using)})")
    else:
        print(f"   (None - all objects from other tasks appear in {target_taskset})")
    
    print(f"\n🤝 Objects SHARED between {target_taskset} and other tasks ({len(common_objects)}):")
    if common_objects:
        for obj in sorted(common_objects):
            task_sets_using = [ts for ts, objs in objects_by_taskset.items() 
                             if ts != target_taskset and obj in objs]
            print(f"   - {obj:30s} (also in: {', '.join(task_sets_using)})")
    else:
        print(f"   (None - {target_taskset} has completely unique objects)")
    
    print(f"\n📊 Summary:")
    print(f"   Total unique objects across ALL tasks: {len(all_objects)}")
    print(f"   Objects in {target_taskset}: {len(target_objects)}")
    print(f"   Objects ONLY in {target_taskset}: {len(target_objects - other_task_objects)}")
    print(f"   Objects shared with other tasks: {len(common_objects)}")
    print(f"   Objects NOT in {target_taskset}: {len(unseen_objects)}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS FOR libero_unseen_{target_taskset.replace('libero_', '')}:")
    print("-" * 80)
    print(f"These objects can be added to {target_taskset} tasks as 'unseen' distractors:")
    print()
    
    # Group by category
    food_items = [obj for obj in unseen_objects if any(x in obj for x in 
                 ['soup', 'sauce', 'cheese', 'butter', 'juice', 'milk', 'dressing', 'pudding', 'ketchup'])]
    kitchenware = [obj for obj in unseen_objects if any(x in obj for x in 
                  ['bowl', 'plate', 'mug', 'cup', 'pan', 'pot', 'bottle', 'rack', 'tray'])]
    books = [obj for obj in unseen_objects if 'book' in obj]
    other = sorted(unseen_objects - set(food_items) - set(kitchenware) - set(books))
    
    if food_items:
        print(f"🥫 Food Items ({len(food_items)}):")
        for obj in sorted(food_items):
            print(f"   - {obj}")
    
    if kitchenware:
        print(f"\n🍽️  Kitchenware ({len(kitchenware)}):")
        for obj in sorted(kitchenware):
            print(f"   - {obj}")
    
    if books:
        print(f"\n📚 Books ({len(books)}):")
        for obj in sorted(books):
            print(f"   - {obj}")
    
    if other:
        print(f"\n📦 Other ({len(other)}):")
        for obj in other:
            print(f"   - {obj}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze objects across LIBERO task sets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze libero_object (default)
  python analyze_libero_objects.py
  
  # Analyze libero_spatial
  python analyze_libero_objects.py --taskset spatial
  
  # Analyze libero_goal with custom path
  python analyze_libero_objects.py --taskset goal --path /path/to/bddl_files
  
Available task sets:
  object, spatial, goal, long_10, long_90
        """
    )
    
    parser.add_argument(
        '--taskset', '-t',
        type=str,
        default='object',
        choices=['object', 'spatial', 'goal', 'long_10', 'long_90'],
        help='Task set to analyze (default: object)'
    )
    
    parser.add_argument(
        '--path', '-p',
        type=str,
        default=None,
        help='Path to LIBERO bddl_files directory (default: auto-detect)'
    )
    
    args = parser.parse_args()
    
    # Map short names to full task set names
    taskset_mapping = {
        'object': 'libero_object',
        'spatial': 'libero_spatial',
        'goal': 'libero_goal',
        'long_10': 'libero_10',
        'long_90': 'libero_90'
    }
    
    target_taskset = taskset_mapping[args.taskset]
    
    # Determine bddl_files path
    if args.path:
        libero_bddl_dir = args.path
    else:
        # Default path - use Path to resolve relative to script location
        # Script is in: third_party/LIBERO/scripts/
        # BDDL files are in: third_party/LIBERO/libero/libero/bddl_files/
        script_dir = Path(__file__).parent
        libero_bddl_dir = script_dir.parent / "libero" / "libero" / "bddl_files"
    
    print(f"Using BDDL path: {libero_bddl_dir}")
    print(f"Target task set: {target_taskset}\n")
    
    analyze_libero_objects(libero_bddl_dir, target_taskset)
