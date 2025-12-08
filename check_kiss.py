#!/usr/bin/env python3
"""
KRWL HOF KISS Compliance Checker

This script checks if the codebase follows KISS (Keep It Simple, Stupid) principles
by measuring various complexity metrics and generating a report.

Usage:
    python3 check_kiss.py [--json] [--fail-on-violation]

Options:
    --json                Output results in JSON format
    --fail-on-violation   Exit with error code if KISS violations found
    --verbose             Show detailed output
"""

import os
import sys
import json
import re
from pathlib import Path
from collections import defaultdict


class KISSChecker:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.repo_root = Path(__file__).parent
        self.thresholds = {
            # File size thresholds (lines)
            'max_file_lines': 500,
            'warn_file_lines': 350,
            
            # Function complexity
            'max_function_lines': 50,
            'warn_function_lines': 30,
            
            # Dependency checks
            'max_imports_per_file': 15,
            'warn_imports_per_file': 10,
            
            # Nesting depth
            'max_nesting_depth': 4,
            'warn_nesting_depth': 3,
            
            # Workflow complexity
            'max_workflow_steps': 20,
            'warn_workflow_steps': 15,
        }
        
        self.results = {
            'overall_score': 'excellent',  # excellent, good, fair, poor
            'total_files_checked': 0,
            'violations': [],
            'warnings': [],
            'metrics': {},
            'summary': {}
        }
    
    def log(self, message, level="INFO"):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def check_file_size(self, file_path):
        """Check if file size is reasonable (KISS: small files)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            line_count = len(lines)
            non_empty_lines = len([l for l in lines if l.strip()])
            
            if line_count > self.thresholds['max_file_lines']:
                self.results['violations'].append({
                    'type': 'file_too_large',
                    'severity': 'error',
                    'file': str(file_path.relative_to(self.repo_root)),
                    'lines': line_count,
                    'threshold': self.thresholds['max_file_lines'],
                    'message': f"File has {line_count} lines (max {self.thresholds['max_file_lines']})"
                })
            elif line_count > self.thresholds['warn_file_lines']:
                self.results['warnings'].append({
                    'type': 'file_size_warning',
                    'severity': 'warning',
                    'file': str(file_path.relative_to(self.repo_root)),
                    'lines': line_count,
                    'threshold': self.thresholds['warn_file_lines'],
                    'message': f"File has {line_count} lines (consider splitting if it grows)"
                })
            
            return line_count, non_empty_lines
        
        except Exception as e:
            self.log(f"Error checking {file_path}: {e}", "ERROR")
            return 0, 0
    
    def check_function_complexity(self, file_path):
        """Check function sizes (KISS: small functions)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find Python functions
            if file_path.suffix == '.py':
                pattern = r'^\s*def\s+(\w+)\s*\('
                functions = re.finditer(pattern, content, re.MULTILINE)
                
                lines = content.split('\n')
                for match in functions:
                    func_name = match.group(1)
                    start_line = content[:match.start()].count('\n')
                    
                    # Find function end (next def or class at same/lower indentation)
                    func_indent = len(match.group(0)) - len(match.group(0).lstrip())
                    end_line = start_line + 1
                    
                    for i in range(start_line + 1, len(lines)):
                        line = lines[i]
                        if line.strip() and not line.strip().startswith('#'):
                            line_indent = len(line) - len(line.lstrip())
                            if line_indent <= func_indent and (line.strip().startswith('def ') or 
                                                               line.strip().startswith('class ') or
                                                               line.strip().startswith('@')):
                                break
                        end_line = i + 1
                    
                    func_lines = end_line - start_line
                    
                    if func_lines > self.thresholds['max_function_lines']:
                        self.results['violations'].append({
                            'type': 'function_too_large',
                            'severity': 'error',
                            'file': str(file_path.relative_to(self.repo_root)),
                            'function': func_name,
                            'lines': func_lines,
                            'threshold': self.thresholds['max_function_lines'],
                            'message': f"Function '{func_name}' has {func_lines} lines (max {self.thresholds['max_function_lines']})"
                        })
                    elif func_lines > self.thresholds['warn_function_lines']:
                        self.results['warnings'].append({
                            'type': 'function_size_warning',
                            'severity': 'warning',
                            'file': str(file_path.relative_to(self.repo_root)),
                            'function': func_name,
                            'lines': func_lines,
                            'threshold': self.thresholds['warn_function_lines'],
                            'message': f"Function '{func_name}' has {func_lines} lines (consider breaking it up)"
                        })
            
            # Find JavaScript functions
            elif file_path.suffix == '.js':
                # Simple pattern for functions
                pattern = r'(?:function\s+(\w+)|(\w+)\s*:\s*function|async\s+(\w+)|(\w+)\s*\([^)]*\)\s*{)'
                functions = re.finditer(pattern, content, re.MULTILINE)
                
                for match in functions:
                    func_name = next((g for g in match.groups() if g), 'anonymous')
                    # Simple heuristic: count lines until matching closing brace
                    # (Not perfect but good enough for KISS check)
                    start_pos = match.end()
                    brace_count = 1
                    pos = start_pos
                    
                    while brace_count > 0 and pos < len(content):
                        if content[pos] == '{':
                            brace_count += 1
                        elif content[pos] == '}':
                            brace_count -= 1
                        pos += 1
                    
                    func_content = content[start_pos:pos]
                    func_lines = func_content.count('\n')
                    
                    if func_lines > self.thresholds['max_function_lines']:
                        self.results['violations'].append({
                            'type': 'function_too_large',
                            'severity': 'error',
                            'file': str(file_path.relative_to(self.repo_root)),
                            'function': func_name,
                            'lines': func_lines,
                            'threshold': self.thresholds['max_function_lines'],
                            'message': f"Function '{func_name}' has {func_lines} lines (max {self.thresholds['max_function_lines']})"
                        })
        
        except Exception as e:
            self.log(f"Error checking functions in {file_path}: {e}", "ERROR")
    
    def check_imports(self, file_path):
        """Check import complexity (KISS: minimal dependencies)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import_count = 0
            
            if file_path.suffix == '.py':
                # Count import statements
                imports = re.findall(r'^\s*(?:import|from)\s+', content, re.MULTILINE)
                import_count = len(imports)
            
            if import_count > self.thresholds['max_imports_per_file']:
                self.results['violations'].append({
                    'type': 'too_many_imports',
                    'severity': 'error',
                    'file': str(file_path.relative_to(self.repo_root)),
                    'imports': import_count,
                    'threshold': self.thresholds['max_imports_per_file'],
                    'message': f"File has {import_count} imports (max {self.thresholds['max_imports_per_file']})"
                })
            elif import_count > self.thresholds['warn_imports_per_file']:
                self.results['warnings'].append({
                    'type': 'import_warning',
                    'severity': 'warning',
                    'file': str(file_path.relative_to(self.repo_root)),
                    'imports': import_count,
                    'threshold': self.thresholds['warn_imports_per_file'],
                    'message': f"File has {import_count} imports (consider reducing dependencies)"
                })
            
            return import_count
        
        except Exception as e:
            self.log(f"Error checking imports in {file_path}: {e}", "ERROR")
            return 0
    
    def check_nesting_depth(self, file_path):
        """Check nesting depth (KISS: flat is better than nested)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            max_depth = 0
            current_depth = 0
            
            for line in lines:
                if not line.strip() or line.strip().startswith('#'):
                    continue
                
                # Simple indentation-based depth check
                indent = len(line) - len(line.lstrip())
                spaces_per_level = 4  # Common convention
                depth = indent // spaces_per_level
                
                if depth > max_depth:
                    max_depth = depth
            
            if max_depth > self.thresholds['max_nesting_depth']:
                self.results['violations'].append({
                    'type': 'deep_nesting',
                    'severity': 'error',
                    'file': str(file_path.relative_to(self.repo_root)),
                    'depth': max_depth,
                    'threshold': self.thresholds['max_nesting_depth'],
                    'message': f"Max nesting depth {max_depth} (max {self.thresholds['max_nesting_depth']})"
                })
            elif max_depth > self.thresholds['warn_nesting_depth']:
                self.results['warnings'].append({
                    'type': 'nesting_warning',
                    'severity': 'warning',
                    'file': str(file_path.relative_to(self.repo_root)),
                    'depth': max_depth,
                    'threshold': self.thresholds['warn_nesting_depth'],
                    'message': f"Max nesting depth {max_depth} (consider flattening)"
                })
            
            return max_depth
        
        except Exception as e:
            self.log(f"Error checking nesting in {file_path}: {e}", "ERROR")
            return 0
    
    def check_workflow_complexity(self, file_path):
        """Check GitHub Actions workflow complexity (KISS: simple workflows)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count steps in workflow
            steps = re.findall(r'^\s*-\s+name:', content, re.MULTILINE)
            step_count = len(steps)
            
            if step_count > self.thresholds['max_workflow_steps']:
                self.results['violations'].append({
                    'type': 'workflow_too_complex',
                    'severity': 'error',
                    'file': str(file_path.relative_to(self.repo_root)),
                    'steps': step_count,
                    'threshold': self.thresholds['max_workflow_steps'],
                    'message': f"Workflow has {step_count} steps (max {self.thresholds['max_workflow_steps']})"
                })
            elif step_count > self.thresholds['warn_workflow_steps']:
                self.results['warnings'].append({
                    'type': 'workflow_complexity_warning',
                    'severity': 'warning',
                    'file': str(file_path.relative_to(self.repo_root)),
                    'steps': step_count,
                    'threshold': self.thresholds['warn_workflow_steps'],
                    'message': f"Workflow has {step_count} steps (consider splitting)"
                })
            
            return step_count
        
        except Exception as e:
            self.log(f"Error checking workflow {file_path}: {e}", "ERROR")
            return 0
    
    def check_all(self):
        """Check all files in the repository"""
        print("=" * 60)
        print("KRWL HOF KISS Compliance Check")
        print("=" * 60)
        print()
        
        # Patterns to check
        patterns = {
            'python': '**/*.py',
            'javascript': '**/*.js',
            'workflows': '.github/workflows/*.yml',
        }
        
        file_metrics = defaultdict(dict)
        
        for file_type, pattern in patterns.items():
            self.log(f"Checking {file_type} files...", "INFO")
            
            for file_path in self.repo_root.glob(pattern):
                # Skip excluded paths
                if any(ex in str(file_path) for ex in ['.git', 'node_modules', '__pycache__', 'venv']):
                    continue
                
                self.results['total_files_checked'] += 1
                rel_path = str(file_path.relative_to(self.repo_root))
                
                self.log(f"  Checking {rel_path}", "DEBUG")
                
                # Check file size
                total_lines, code_lines = self.check_file_size(file_path)
                file_metrics[rel_path]['total_lines'] = total_lines
                file_metrics[rel_path]['code_lines'] = code_lines
                
                # Check function complexity
                if file_type in ['python', 'javascript']:
                    self.check_function_complexity(file_path)
                
                # Check imports
                if file_type == 'python':
                    imports = self.check_imports(file_path)
                    file_metrics[rel_path]['imports'] = imports
                
                # Check nesting depth
                if file_type in ['python', 'javascript']:
                    depth = self.check_nesting_depth(file_path)
                    file_metrics[rel_path]['max_nesting'] = depth
                
                # Check workflow complexity
                if file_type == 'workflows':
                    steps = self.check_workflow_complexity(file_path)
                    file_metrics[rel_path]['workflow_steps'] = steps
        
        self.results['metrics'] = dict(file_metrics)
        
        # Calculate overall score
        violation_count = len(self.results['violations'])
        warning_count = len(self.results['warnings'])
        
        if violation_count > 0:
            self.results['overall_score'] = 'poor'
        elif warning_count > 5:
            self.results['overall_score'] = 'fair'
        elif warning_count > 0:
            self.results['overall_score'] = 'good'
        else:
            self.results['overall_score'] = 'excellent'
        
        # Generate summary
        self.results['summary'] = {
            'total_violations': violation_count,
            'total_warnings': warning_count,
            'score': self.results['overall_score']
        }
        
        return self.results
    
    def print_report(self):
        """Print human-readable report"""
        print("\n" + "=" * 60)
        print("KISS COMPLIANCE REPORT")
        print("=" * 60)
        
        summary = self.results['summary']
        score = summary['score']
        
        # Score emoji
        score_emoji = {
            'excellent': '✅',
            'good': '✓',
            'fair': '⚠️',
            'poor': '❌'
        }
        
        print(f"\nOverall Score: {score_emoji.get(score, '?')} {score.upper()}")
        print(f"Files Checked: {self.results['total_files_checked']}")
        print(f"Violations: {summary['total_violations']}")
        print(f"Warnings: {summary['total_warnings']}")
        
        # Print violations
        if self.results['violations']:
            print("\n" + "=" * 60)
            print("VIOLATIONS (Must Fix)")
            print("=" * 60)
            
            for violation in self.results['violations']:
                print(f"\n❌ {violation['type'].upper()}")
                print(f"   File: {violation['file']}")
                print(f"   {violation['message']}")
        
        # Print warnings
        if self.results['warnings']:
            print("\n" + "=" * 60)
            print("WARNINGS (Consider Fixing)")
            print("=" * 60)
            
            for warning in self.results['warnings']:
                print(f"\n⚠️  {warning['type'].upper()}")
                print(f"   File: {warning['file']}")
                print(f"   {warning['message']}")
        
        # KISS recommendations
        if summary['total_violations'] > 0 or summary['total_warnings'] > 0:
            print("\n" + "=" * 60)
            print("KISS RECOMMENDATIONS")
            print("=" * 60)
            print("""
1. Break large files into smaller modules
2. Split complex functions into smaller ones
3. Reduce dependencies where possible
4. Flatten deeply nested code
5. Simplify complex workflows
6. Keep each component focused on one thing
            """)
        
        print("=" * 60)
        
        if summary['score'] == 'excellent':
            print("\n🎉 Excellent! Your codebase follows KISS principles.")
        elif summary['score'] == 'good':
            print("\n✓ Good job! Minor improvements recommended.")
        elif summary['score'] == 'fair':
            print("\n⚠️  Consider simplifying to improve maintainability.")
        else:
            print("\n❌ Action needed: Simplify complex code for better maintainability.")
        
        return 0 if summary['total_violations'] == 0 else 1


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Check KISS compliance of KRWL HOF codebase"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        "--fail-on-violation",
        action="store_true",
        help="Exit with error code if violations found"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    
    args = parser.parse_args()
    
    checker = KISSChecker(verbose=args.verbose)
    results = checker.check_all()
    
    if args.json:
        print("\n" + json.dumps(results, indent=2))
        exit_code = 1 if results['summary']['total_violations'] > 0 else 0
    else:
        exit_code = checker.print_report()
    
    if args.fail_on_violation and exit_code != 0:
        sys.exit(exit_code)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
