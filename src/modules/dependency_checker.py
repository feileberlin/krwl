#!/usr/bin/env python3
"""
Dependency Checker Module

Validates and visualizes module dependencies to help prevent breaking changes.
Ensures dependency tracking in features.json is accurate and up-to-date.

Usage:
    python3 src/modules/dependency_checker.py
    python3 src/modules/dependency_checker.py --check-feature FEATURE_ID
    python3 src/modules/dependency_checker.py --show-tree
    python3 src/modules/dependency_checker.py --validate
    python3 src/modules/dependency_checker.py --analyze-js
    python3 src/modules/dependency_checker.py --analyze-py
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


class DependencyChecker:
    """Analyzes and validates module dependencies"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.getcwd())
        self.features = self._load_features()
        self.dependency_graph = self._build_dependency_graph()
        
    def _load_features(self) -> dict:
        """Load features.json"""
        features_path = self.base_path / 'features.json'
        if not features_path.exists():
            raise FileNotFoundError(f"features.json not found at {features_path}")
        
        with open(features_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build dependency graph from features.json"""
        graph = {}
        
        for feature in self.features.get('features', []):
            feature_id = feature['id']
            depends_on = feature.get('depends_on', [])
            
            if feature_id not in graph:
                graph[feature_id] = set()
            
            for dep in depends_on:
                graph[feature_id].add(dep)
        
        return graph
    
    def analyze_js_dependencies(self) -> Dict[str, Dict]:
        """
        Analyze JavaScript file dependencies.
        
        Note: Uses regex patterns for basic analysis. For complex codebases,
        consider using a proper JavaScript parser like esprima or acorn.
        This is sufficient for our KISS-compliant vanilla JS codebase.
        """
        js_dir = self.base_path / 'assets' / 'js'
        dependencies = {}
        
        for js_file in js_dir.glob('*.js'):
            if js_file.name.startswith('README'):
                continue
            
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find class definitions (KISS: regex is sufficient for our simple classes)
            # Matches: class ClassName { ... }
            classes = re.findall(r'class\s+(\w+)', content)
            
            # Find instantiations (new ClassName())
            # Matches: new ClassName(args)
            instantiations = re.findall(r'new\s+(\w+)\(', content)
            
            # Remove duplicates
            dependencies[js_file.name] = {
                'defines': list(set(classes)),
                'uses': list(set(instantiations))
            }
        
        return dependencies
    
    def analyze_python_dependencies(self) -> Dict[str, Dict]:
        """
        Analyze Python module dependencies.
        
        Detects imports from peer modules using common patterns:
        - Relative imports: from .module_name import
        - From modules: from modules.module_name import
        - Absolute imports: from src.modules.module_name import
        """
        modules_dir = self.base_path / 'src' / 'modules'
        dependencies = {}
        
        for py_file in modules_dir.glob('*.py'):
            if py_file.name == '__init__.py':
                continue
            
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find imports from peer modules (multiple patterns)
            imports = set()
            
            # Pattern 1: Relative imports (from .module_name import)
            imports.update(re.findall(r'from \.(\w+) import', content))
            
            # Pattern 2: From modules directory (from modules.module_name import)
            imports.update(re.findall(r'from modules\.(\w+) import', content))
            
            # Pattern 3: Absolute imports (from src.modules.module_name import)
            imports.update(re.findall(r'from src\.modules\.(\w+) import', content))
            imports.update(re.findall(r'import src\.modules\.(\w+)', content))
            
            dependencies[py_file.name] = {
                'imports': list(imports)
            }
        
        return dependencies
    
    def find_dependents(self, feature_id: str) -> List[str]:
        """Find all features that depend on the given feature"""
        dependents = []
        
        for fid, deps in self.dependency_graph.items():
            if feature_id in deps:
                dependents.append(fid)
        
        return dependents
    
    def calculate_impact(self, feature_id: str) -> Dict[str, Any]:
        """Calculate the impact of changing a feature"""
        direct_dependents = self.find_dependents(feature_id)
        all_dependents = set(direct_dependents)
        
        # Recursively find all indirect dependents
        to_check = list(direct_dependents)
        while to_check:
            current = to_check.pop()
            deps = self.find_dependents(current)
            for dep in deps:
                if dep not in all_dependents:
                    all_dependents.add(dep)
                    to_check.append(dep)
        
        return {
            'feature_id': feature_id,
            'direct_dependents': direct_dependents,
            'all_dependents': list(all_dependents),
            'impact_score': len(all_dependents)
        }
    
    def get_feature_by_id(self, feature_id: str) -> dict:
        """Get feature details by ID"""
        for feature in self.features.get('features', []):
            if feature['id'] == feature_id:
                return feature
        return None
    
    def print_impact_report(self, feature_id: str):
        """Print detailed impact report for a feature"""
        feature = self.get_feature_by_id(feature_id)
        if not feature:
            print(f"❌ Feature '{feature_id}' not found in features.json")
            return
        
        impact = self.calculate_impact(feature_id)
        
        print(f"\n{'='*80}")
        print(f"  IMPACT ANALYSIS: {feature['name']} ({feature_id})")
        print(f"{'='*80}\n")
        
        print(f"📦 Feature Details:")
        print(f"   Category: {feature.get('category', 'N/A')}")
        print(f"   Files: {', '.join(feature.get('files', []))}")
        
        if feature.get('depends_on'):
            print(f"\n📌 This feature depends on:")
            for dep in feature['depends_on']:
                dep_feature = self.get_feature_by_id(dep)
                if dep_feature:
                    print(f"   • {dep_feature['name']} ({dep})")
        else:
            print(f"\n✅ No dependencies (standalone feature)")
        
        if impact['direct_dependents']:
            print(f"\n⚠️  Changing this feature DIRECTLY affects:")
            for dep in impact['direct_dependents']:
                dep_feature = self.get_feature_by_id(dep)
                if dep_feature:
                    print(f"   • {dep_feature['name']} ({dep})")
        
        if len(impact['all_dependents']) > len(impact['direct_dependents']):
            print(f"\n🔴 Changing this feature INDIRECTLY affects:")
            indirect = set(impact['all_dependents']) - set(impact['direct_dependents'])
            for dep in indirect:
                dep_feature = self.get_feature_by_id(dep)
                if dep_feature:
                    print(f"   • {dep_feature['name']} ({dep})")
        
        # Impact score
        print(f"\n📊 Impact Score: {impact['impact_score']}")
        if impact['impact_score'] == 0:
            print(f"   🟢 LOW RISK - No dependent features")
        elif impact['impact_score'] <= 2:
            print(f"   🟡 MEDIUM RISK - Few dependent features")
        else:
            print(f"   🔴 HIGH RISK - Many dependent features")
        
        print(f"\n{'='*80}\n")
    
    def print_full_dependency_tree(self):
        """Print complete dependency tree"""
        print(f"\n{'='*80}")
        print(f"  COMPLETE DEPENDENCY TREE")
        print(f"{'='*80}\n")
        
        for feature in self.features.get('features', []):
            feature_id = feature['id']
            deps = feature.get('depends_on', [])
            
            if deps:
                print(f"📦 {feature['name']} ({feature_id})")
                print(f"   Depends on:")
                for dep in deps:
                    dep_feature = self.get_feature_by_id(dep)
                    if dep_feature:
                        print(f"   └─→ {dep_feature['name']} ({dep})")
                print()
    
    def validate_dependencies(self) -> List[str]:
        """Validate that all dependencies exist and are valid"""
        errors = []
        
        for feature in self.features.get('features', []):
            feature_id = feature['id']
            depends_on = feature.get('depends_on', [])
            
            for dep in depends_on:
                dep_feature = self.get_feature_by_id(dep)
                if not dep_feature:
                    errors.append(
                        f"Feature '{feature_id}' depends on non-existent feature '{dep}'"
                    )
        
        return errors
    
    def check_circular_dependencies(self) -> List[Tuple[str, str]]:
        """Check for circular dependencies"""
        circular = []
        
        def has_path(start: str, end: str, visited: Set[str] = None) -> bool:
            # Avoid mutable default argument
            visited = visited or set()
            
            if start == end and visited:
                return True
            
            if start in visited:
                return False
            
            visited.add(start)
            
            for dep in self.dependency_graph.get(start, set()):
                if has_path(dep, end, visited.copy()):
                    return True
            
            return False
        
        for feature_id in self.dependency_graph:
            for dep in self.dependency_graph.get(feature_id, set()):
                if has_path(dep, feature_id):
                    circular.append((feature_id, dep))
        
        return circular


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Check and visualize module dependencies'
    )
    parser.add_argument(
        '--check-feature',
        metavar='FEATURE_ID',
        help='Show impact analysis for a specific feature'
    )
    parser.add_argument(
        '--show-tree',
        action='store_true',
        help='Show complete dependency tree'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate all dependencies'
    )
    parser.add_argument(
        '--analyze-js',
        action='store_true',
        help='Analyze JavaScript dependencies'
    )
    parser.add_argument(
        '--analyze-py',
        action='store_true',
        help='Analyze Python dependencies'
    )
    
    args = parser.parse_args()
    
    try:
        checker = DependencyChecker()
        
        if args.check_feature:
            checker.print_impact_report(args.check_feature)
        elif args.show_tree:
            checker.print_full_dependency_tree()
        elif args.validate:
            print("\n🔍 Validating dependencies...\n")
            errors = checker.validate_dependencies()
            if errors:
                print("❌ Validation errors found:")
                for error in errors:
                    print(f"   • {error}")
            else:
                print("✅ All dependencies are valid!")
            
            print("\n🔍 Checking for circular dependencies...\n")
            circular = checker.check_circular_dependencies()
            if circular:
                print("❌ Circular dependencies found:")
                for dep1, dep2 in circular:
                    print(f"   • {dep1} ↔ {dep2}")
            else:
                print("✅ No circular dependencies!")
            print()
        elif args.analyze_js:
            print("\n📊 JavaScript Dependencies:\n")
            js_deps = checker.analyze_js_dependencies()
            for file, deps in sorted(js_deps.items()):
                if deps['defines'] or deps['uses']:
                    print(f"{file}:")
                    if deps['defines']:
                        print(f"  Defines: {', '.join(deps['defines'])}")
                    if deps['uses']:
                        print(f"  Uses: {', '.join(deps['uses'])}")
                    print()
        elif args.analyze_py:
            print("\n📊 Python Dependencies:\n")
            py_deps = checker.analyze_python_dependencies()
            for file, deps in sorted(py_deps.items()):
                if deps['imports']:
                    print(f"{file}:")
                    print(f"  Imports: {', '.join(deps['imports'])}")
                    print()
        else:
            # Default: show summary
            print("\n" + "="*80)
            print("  DEPENDENCY CHECKER - Quick Summary")
            print("="*80 + "\n")
            
            print("📚 Use these commands to explore dependencies:\n")
            print("  --check-feature FEATURE_ID    Show impact of changing a feature")
            print("  --show-tree                   Show complete dependency tree")
            print("  --validate                    Validate all dependencies")
            print("  --analyze-js                  Analyze JavaScript dependencies")
            print("  --analyze-py                  Analyze Python dependencies")
            print("\nExamples:")
            print("  python3 src/modules/dependency_checker.py --check-feature interactive-map")
            print("  python3 src/modules/dependency_checker.py --validate")
            print()
    
    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}")
        print("Make sure you're running from the project root directory.\n")
        return 1
    except json.JSONDecodeError as e:
        print(f"\n❌ Invalid JSON in features.json: {e}\n")
        return 1
    except KeyError as e:
        print(f"\n❌ Missing required key in features.json: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
