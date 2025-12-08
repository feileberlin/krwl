"""
KRWL HOF KISS Compliance Checker Module

This module provides the KISSChecker class for measuring code complexity
and ensuring adherence to KISS (Keep It Simple, Stupid) principles.
"""

import os
import re
from pathlib import Path
from collections import defaultdict


class KISSChecker:
    def __init__(self, repo_root=None, verbose=False):
        self.verbose = verbose
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
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
                lines = content.split('\n')
            
            # Find functions using regex
            # Matches: def function_name(... or async def function_name(...
            function_pattern = re.compile(r'^\s*(async\s+)?def\s+(\w+)\s*\(')
            
            current_function = None
            function_start = 0
            base_indent = 0
            
            for i, line in enumerate(lines):
                match = function_pattern.match(line)
                
                if match:
                    # Save previous function if exists
                    if current_function:
                        function_lines = i - function_start
                        self._check_function_size(file_path, current_function, function_lines)
                    
                    # Start new function
                    current_function = match.group(2)
                    function_start = i
                    base_indent = len(line) - len(line.lstrip())
                
                # Check for function end (dedent to same or less level)
                elif current_function and line.strip():
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent <= base_indent and i > function_start:
                        function_lines = i - function_start
                        self._check_function_size(file_path, current_function, function_lines)
                        current_function = None
            
            # Handle last function
            if current_function:
                function_lines = len(lines) - function_start
                self._check_function_size(file_path, current_function, function_lines)
        
        except Exception as e:
            self.log(f"Error checking functions in {file_path}: {e}", "ERROR")
    
    def _check_function_size(self, file_path, function_name, line_count):
        """Check if a single function is too large"""
        if line_count > self.thresholds['max_function_lines']:
            self.results['violations'].append({
                'type': 'function_too_long',
                'severity': 'error',
                'file': str(file_path.relative_to(self.repo_root)),
                'function': function_name,
                'lines': line_count,
                'threshold': self.thresholds['max_function_lines'],
                'message': f"Function '{function_name}' has {line_count} lines (max {self.thresholds['max_function_lines']})"
            })
        elif line_count > self.thresholds['warn_function_lines']:
            self.results['warnings'].append({
                'type': 'function_length_warning',
                'severity': 'warning',
                'file': str(file_path.relative_to(self.repo_root)),
                'function': function_name,
                'lines': line_count,
                'threshold': self.thresholds['warn_function_lines'],
                'message': f"Function '{function_name}' has {line_count} lines (consider refactoring)"
            })
    
    def check_imports(self, file_path):
        """Check number of imports (KISS: minimal dependencies)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count import statements
            import_pattern = re.compile(r'^\s*(import|from)\s+', re.MULTILINE)
            imports = import_pattern.findall(content)
            import_count = len(imports)
            
            if import_count > self.thresholds['max_imports_per_file']:
                self.results['violations'].append({
                    'type': 'too_many_imports',
                    'severity': 'error',
                    'file': str(file_path.relative_to(self.repo_root)),
                    'count': import_count,
                    'threshold': self.thresholds['max_imports_per_file'],
                    'message': f"File has {import_count} imports (max {self.thresholds['max_imports_per_file']})"
                })
            elif import_count > self.thresholds['warn_imports_per_file']:
                self.results['warnings'].append({
                    'type': 'import_count_warning',
                    'severity': 'warning',
                    'file': str(file_path.relative_to(self.repo_root)),
                    'count': import_count,
                    'threshold': self.thresholds['warn_imports_per_file'],
                    'message': f"File has {import_count} imports (consider reducing dependencies)"
                })
            
            return import_count
        
        except Exception as e:
            self.log(f"Error checking imports in {file_path}: {e}", "ERROR")
            return 0
    
    def check_nesting_depth(self, file_path):
        """Check nesting depth (KISS: avoid deep nesting)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            max_depth = 0
            current_depth = 0
            prev_indent = 0
            
            for line in lines:
                stripped = line.lstrip()
                if not stripped or stripped.startswith('#'):
                    continue
                
                indent = len(line) - len(stripped)
                
                # Estimate depth based on indent (assuming 4 spaces per level)
                current_depth = indent // 4
                max_depth = max(max_depth, current_depth)
            
            if max_depth > self.thresholds['max_nesting_depth']:
                self.results['violations'].append({
                    'type': 'nesting_too_deep',
                    'severity': 'error',
                    'file': str(file_path.relative_to(self.repo_root)),
                    'depth': max_depth,
                    'threshold': self.thresholds['max_nesting_depth'],
                    'message': f"Max nesting depth is {max_depth} (max {self.thresholds['max_nesting_depth']})"
                })
            elif max_depth > self.thresholds['warn_nesting_depth']:
                self.results['warnings'].append({
                    'type': 'nesting_depth_warning',
                    'severity': 'warning',
                    'file': str(file_path.relative_to(self.repo_root)),
                    'depth': max_depth,
                    'threshold': self.thresholds['warn_nesting_depth'],
                    'message': f"Max nesting depth is {max_depth} (consider flattening)"
                })
            
            return max_depth
        
        except Exception as e:
            self.log(f"Error checking nesting in {file_path}: {e}", "ERROR")
            return 0
    
    def check_workflow_files(self):
        """Check GitHub Actions workflow complexity"""
        workflows_dir = self.repo_root / '.github' / 'workflows'
        
        if not workflows_dir.exists():
            return
        
        for workflow_file in workflows_dir.glob('*.yml'):
            try:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Count steps (rough estimate)
                step_pattern = re.compile(r'^\s*-\s+name:', re.MULTILINE)
                steps = step_pattern.findall(content)
                step_count = len(steps)
                
                if step_count > self.thresholds['max_workflow_steps']:
                    self.results['violations'].append({
                        'type': 'workflow_too_complex',
                        'severity': 'error',
                        'file': str(workflow_file.relative_to(self.repo_root)),
                        'steps': step_count,
                        'threshold': self.thresholds['max_workflow_steps'],
                        'message': f"Workflow has {step_count} steps (max {self.thresholds['max_workflow_steps']})"
                    })
                elif step_count > self.thresholds['warn_workflow_steps']:
                    self.results['warnings'].append({
                        'type': 'workflow_complexity_warning',
                        'severity': 'warning',
                        'file': str(workflow_file.relative_to(self.repo_root)),
                        'steps': step_count,
                        'threshold': self.thresholds['warn_workflow_steps'],
                        'message': f"Workflow has {step_count} steps (consider simplifying)"
                    })
            
            except Exception as e:
                self.log(f"Error checking workflow {workflow_file}: {e}", "ERROR")
    
    def check_python_files(self):
        """Check all Python files in the repository"""
        # Check src directory
        src_dir = self.repo_root / 'src'
        if src_dir.exists():
            for py_file in src_dir.rglob('*.py'):
                if '__pycache__' in str(py_file):
                    continue
                
                self.log(f"Checking {py_file.relative_to(self.repo_root)}")
                self.results['total_files_checked'] += 1
                
                self.check_file_size(py_file)
                self.check_function_complexity(py_file)
                self.check_imports(py_file)
                self.check_nesting_depth(py_file)
        
        # Check root Python files
        for py_file in self.repo_root.glob('*.py'):
            self.log(f"Checking {py_file.relative_to(self.repo_root)}")
            self.results['total_files_checked'] += 1
            
            self.check_file_size(py_file)
            self.check_function_complexity(py_file)
            self.check_imports(py_file)
            self.check_nesting_depth(py_file)
    
    def check_all(self):
        """Run all KISS checks"""
        self.log("Starting KISS compliance check...")
        
        # Check Python files
        self.check_python_files()
        
        # Check workflows
        self.check_workflow_files()
        
        # Calculate summary
        self.results['summary'] = self._calculate_summary()
        
        return self.results
    
    def _calculate_summary(self):
        """Calculate summary statistics"""
        total_violations = len(self.results['violations'])
        total_warnings = len(self.results['warnings'])
        
        # Determine overall score
        if total_violations == 0 and total_warnings == 0:
            score = 'excellent'
        elif total_violations == 0 and total_warnings <= 3:
            score = 'good'
        elif total_violations <= 2:
            score = 'fair'
        else:
            score = 'poor'
        
        self.results['overall_score'] = score
        
        return {
            'score': score,
            'total_violations': total_violations,
            'total_warnings': total_warnings,
            'files_checked': self.results['total_files_checked']
        }
    
    def print_report(self):
        """Print human-readable report"""
        summary = self.results['summary']
        
        print("\n" + "=" * 60)
        print("KRWL HOF KISS Compliance Report")
        print("=" * 60)
        
        score = summary['score']
        score_emoji = {
            'excellent': '🎉',
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
