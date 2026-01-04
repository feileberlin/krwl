#!/usr/bin/env python3
"""
KRWL HOF Documentation Runner Module

Centralized documentation management system following KISS principles.
Handles all documentation generation, validation, and synchronization tasks.
"""

import subprocess
import sys
from pathlib import Path


class DocsRunner:
    """Modular documentation runner for KRWL HOF
    
    Organizes documentation tasks:
    - Generation (README, screenshots, demos)
    - Validation (docs testing, content validation)
    - Synchronization (wiki sync, cleanup)
    """
    
    # Documentation tasks organized by category
    DOCS_TASKS = {
        'generate': {
            'readme': {
                'script': 'scripts/generate_readme.py',
                'description': 'Generate README.md from code and config',
                'supports_args': ['--update-github-about'],
            },
            'demos': {
                'script': 'scripts/generate_demo_events.py',
                'description': 'Generate demo events with dynamic timestamps',
            },
            'screenshots': {
                'script': 'scripts/generate_screenshots.py',
                'description': 'Generate project screenshots',
            },
            'html-docs': {
                'script': 'src/modules/docs_generator.py',
                'description': 'Generate styled HTML documentation with Barbie Pink theme',
            },
        },
        'validate': {
            'docs': {
                'script': 'scripts/test_documentation.py',
                'description': 'Test documentation completeness',
            },
            'content': {
                'script': 'scripts/validate_docs.py',
                'description': 'Validate documentation content',
            },
            'lint-markdown': {
                'script': 'scripts/lint_markdown.py',
                'description': 'Lint markdown files for common issues',
                'supports_args': ['--fix', '--all', '--verbose', 'PATH'],
            },
        },
        'maintain': {
            'cleanup-obsolete': {
                'script': 'scripts/cleanup_obsolete.py',
                'description': 'Clean up obsolete files',
            },
            'cleanup-docs': {
                'script': 'scripts/cleanup_old_docs.py',
                'description': 'Clean up old documentation files',
            },
        },
    }
    
    def __init__(self, base_path: Path):
        """Initialize documentation runner
        
        Args:
            base_path: Repository root path
        """
        self.base_path = Path(base_path)
        
    def list_tasks(self):
        """List all available documentation tasks"""
        print("\n" + "=" * 70)
        print("KRWL HOF Documentation Tasks")
        print("=" * 70)
        
        total_tasks = 0
        for category, tasks in self.DOCS_TASKS.items():
            print(f"\n{category.upper()} ({len(tasks)} tasks):")
            print("-" * 70)
            for name, info in tasks.items():
                print(f"  • {name:20s} - {info['description']}")
                total_tasks += 1
        
        print("\n" + "=" * 70)
        print(f"Total: {total_tasks} documentation tasks available")
        print("=" * 70)
        
        print("\nUsage:")
        print("  python3 src/event_manager.py docs TASK_NAME [OPTIONS]")
        print("\nExamples:")
        print("  python3 src/event_manager.py docs readme")
        print("  python3 src/event_manager.py docs readme --update-github-about")
        print("  python3 src/event_manager.py docs demos")
        print("  python3 src/event_manager.py docs validate")
    
    def run_task(self, name: str, args: list = None) -> bool:
        """Run a specific documentation task
        
        Args:
            name: Task name
            args: Additional arguments
            
        Returns:
            True if successful, False otherwise
        """
        args = args or []
        
        # Find task in categories
        task = None
        for category, tasks in self.DOCS_TASKS.items():
            if name in tasks:
                task = tasks[name]
                break
        
        if not task:
            print(f"\n✗ Unknown documentation task: '{name}'")
            print("\nUse 'docs --list' to see available tasks")
            return False
        
        print(f"\nRunning documentation task: {name}")
        print("=" * 70)
        
        try:
            return self._run_script(task, args)
        except Exception as e:
            print(f"\n✗ Error running task: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_category(self, category: str) -> bool:
        """Run all tasks in a category
        
        Args:
            category: Category name (generate, validate, maintain)
            
        Returns:
            True if all successful, False otherwise
        """
        if category not in self.DOCS_TASKS:
            print(f"\n✗ Unknown category: '{category}'")
            print(f"\nAvailable categories: {', '.join(self.DOCS_TASKS.keys())}")
            return False
        
        tasks = self.DOCS_TASKS[category]
        
        print(f"\nRunning {category.upper()} tasks ({len(tasks)} tasks)")
        print("=" * 70)
        
        all_success = True
        for task_name in tasks.keys():
            print(f"\n--- Running: {task_name} ---")
            if not self.run_task(task_name):
                all_success = False
                print(f"✗ Task '{task_name}' failed")
            else:
                print(f"✓ Task '{task_name}' completed")
        
        print("\n" + "=" * 70)
        if all_success:
            print(f"✓ All {category} tasks completed successfully")
        else:
            print(f"✗ Some {category} tasks failed")
        
        return all_success
    
    def _run_script(self, task: dict, args: list) -> bool:
        """Run documentation script
        
        Args:
            task: Task configuration
            args: Additional arguments
            
        Returns:
            True if successful, False otherwise
        """
        script_path = self.base_path / task['script']
        
        if not script_path.exists():
            print(f"✗ Script not found: {script_path}")
            return False
        
        # Run script
        cmd = [sys.executable, str(script_path)] + args
        
        result = subprocess.run(
            cmd,
            cwd=str(self.base_path),
        )
        
        return result.returncode == 0


def main():
    """Main entry point for standalone usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='KRWL HOF Documentation Runner')
    parser.add_argument('task', nargs='?', default=None,
                       help='Documentation task or category to run')
    parser.add_argument('args', nargs='*',
                       help='Additional arguments for the task')
    parser.add_argument('--list', action='store_true',
                       help='List all available documentation tasks')
    
    args = parser.parse_args()
    
    # Get repository root (go up two levels from src/modules/)
    base_path = Path(__file__).parent.parent.parent
    
    runner = DocsRunner(base_path)
    
    # List tasks
    if args.list or args.task is None:
        runner.list_tasks()
        return 0
    
    # Check if it's a category
    if args.task in runner.DOCS_TASKS:
        return 0 if runner.run_category(args.task) else 1
    
    # Run specific task
    return 0 if runner.run_task(args.task, args.args) else 1


if __name__ == "__main__":
    sys.exit(main())
