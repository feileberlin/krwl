#!/usr/bin/env python3
"""
GitHub Actions Workflow Launcher Module

This module provides functionality to list and trigger GitHub Actions workflows
from the TUI and CLI using the GitHub CLI (gh).
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class WorkflowLauncher:
    """Manages GitHub Actions workflow triggering via GitHub CLI"""
    
    # Define workflows that support manual triggering (workflow_dispatch)
    # NOTE: These are hardcoded for simplicity following KISS principles.
    # For a more dynamic approach, consider parsing workflow YAML files directly
    # or maintaining a separate configuration file if the workflow list grows significantly.
    AVAILABLE_WORKFLOWS = {
        'deploy-pages': {
            'file': 'deploy-pages.yml',
            'name': '🚀 Deploy to Production',
            'description': 'Deploy the main branch to GitHub Pages (production)',
            'inputs': {
                'reason': {
                    'description': 'Reason for manual deployment',
                    'type': 'string',
                    'default': 'Manual deployment triggered',
                    'required': False
                }
            }
        },
        'deploy-preview': {
            'file': 'deploy-preview.yml',
            'name': '🔍 Deploy Preview Environment',
            'description': 'Deploy the preview branch to /preview/ path',
            'inputs': {
                'reason': {
                    'description': 'Reason for manual preview deployment',
                    'type': 'string',
                    'default': 'Manual preview deployment triggered',
                    'required': False
                }
            }
        },
        'promote-preview': {
            'file': 'promote-preview.yml',
            'name': '📦 Promote Preview to Production',
            'description': 'Create PR from preview to main branch',
            'inputs': {
                'auto_merge': {
                    'description': '✅ Auto-merge the PR (only works without branch protection)',
                    'type': 'choice',
                    'default': 'false',
                    'options': ['false', 'true'],
                    'required': False
                }
            }
        },
        'scrape-events': {
            'file': 'scrape-events.yml',
            'name': '🔄 Scrape Events & Deploy',
            'description': 'Manually trigger event scraping and deployment',
            'inputs': {
                'force_deploy': {
                    'description': '🚀 Force deployment even if no new events found',
                    'type': 'choice',
                    'default': 'false',
                    'options': ['false', 'true'],
                    'required': False
                }
            }
        },
        'kiss-compliance': {
            'file': 'kiss-compliance.yml',
            'name': '💡 Check KISS Compliance',
            'description': 'Run KISS compliance verification',
            'inputs': {
                'fail_on_violations': {
                    'description': '🚫 Block on KISS violations (normally warnings only)',
                    'type': 'choice',
                    'default': 'false',
                    'options': ['false', 'true'],
                    'required': False
                }
            }
        },
        'lint': {
            'file': 'lint.yml',
            'name': '🔍 Lint Code Quality',
            'description': 'Run linting on Python, JavaScript, and JSON files',
            'inputs': {
                'fail_on_python_errors': {
                    'description': '🐍 Block on Python critical errors',
                    'type': 'choice',
                    'default': 'true',
                    'options': ['true', 'false'],
                    'required': False
                },
                'fail_on_js_errors': {
                    'description': '📜 Block on JavaScript errors',
                    'type': 'choice',
                    'default': 'false',
                    'options': ['true', 'false'],
                    'required': False
                },
                'fail_on_json_errors': {
                    'description': '📋 Block on JSON validation errors',
                    'type': 'choice',
                    'default': 'true',
                    'options': ['true', 'false'],
                    'required': False
                },
                'fail_on_style_issues': {
                    'description': '✨ Block on style/warning issues',
                    'type': 'choice',
                    'default': 'false',
                    'options': ['true', 'false'],
                    'required': False
                }
            }
        },
        'verify-features': {
            'file': 'verify-features.yml',
            'name': '✅ Verify Feature Registry',
            'description': 'Run feature registry verification',
            'inputs': {
                'verbose': {
                    'description': '📝 Verbose output (show all details)',
                    'type': 'choice',
                    'default': 'true',
                    'options': ['true', 'false'],
                    'required': False
                }
            }
        },
        'docs': {
            'file': 'docs.yml',
            'name': '📚 Build Documentation',
            'description': 'Build and validate documentation',
            'inputs': {
                'force_rebuild': {
                    'description': '🔄 Force rebuild even if no changes',
                    'type': 'choice',
                    'default': 'false',
                    'options': ['false', 'true'],
                    'required': False
                }
            }
        }
    }
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize workflow launcher"""
        self.base_path = base_path or Path.cwd()
        self.gh_available = self._check_gh_cli()
        
    def _check_gh_cli(self) -> bool:
        """Check if GitHub CLI is installed and authenticated"""
        try:
            result = subprocess.run(
                ['gh', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def check_gh_auth(self) -> Tuple[bool, str]:
        """Check if GitHub CLI is authenticated"""
        if not self.gh_available:
            return False, "GitHub CLI (gh) is not installed"
        
        try:
            result = subprocess.run(
                ['gh', 'auth', 'status'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, "Authenticated"
            else:
                return False, "Not authenticated. Run: gh auth login"
        except subprocess.TimeoutExpired:
            return False, "GitHub CLI authentication check timed out"
    
    def list_workflows(self) -> List[Dict[str, str]]:
        """List all available workflows that support manual triggering"""
        workflows = []
        for key, workflow in self.AVAILABLE_WORKFLOWS.items():
            workflows.append({
                'id': key,
                'name': workflow['name'],
                'description': workflow['description'],
                'file': workflow['file'],
                'has_inputs': len(workflow['inputs']) > 0
            })
        return workflows
    
    def get_workflow_info(self, workflow_id: str) -> Optional[Dict]:
        """Get detailed information about a specific workflow"""
        return self.AVAILABLE_WORKFLOWS.get(workflow_id)
    
    def trigger_workflow(
        self,
        workflow_id: str,
        branch: str = 'preview',
        inputs: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, str]:
        """
        Trigger a GitHub Actions workflow
        
        Args:
            workflow_id: ID of the workflow to trigger
            branch: Branch to trigger the workflow on (default: preview)
            inputs: Dictionary of input parameters for the workflow
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Check authentication first
        auth_ok, auth_msg = self.check_gh_auth()
        if not auth_ok:
            return False, f"Authentication failed: {auth_msg}"
        
        # Get workflow info
        workflow = self.get_workflow_info(workflow_id)
        if not workflow:
            return False, f"Unknown workflow: {workflow_id}"
        
        workflow_file = workflow['file']
        
        # Build command
        cmd = ['gh', 'workflow', 'run', workflow_file, '--ref', branch]
        
        # Add inputs if provided
        if inputs:
            for key, value in inputs.items():
                cmd.extend(['-f', f'{key}={value}'])
        
        # Execute command
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.base_path
            )
            
            if result.returncode == 0:
                return True, f"✓ Workflow '{workflow['name']}' triggered successfully on branch '{branch}'"
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                # Sanitize error message to avoid leaking sensitive information
                if 'token' in error_msg.lower() or 'auth' in error_msg.lower():
                    return False, "Failed to trigger workflow: Authentication error. Check your GitHub CLI credentials."
                return False, f"Failed to trigger workflow: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "Workflow trigger timed out"
        except subprocess.CalledProcessError as e:
            return False, f"GitHub CLI error: Command failed with exit code {e.returncode}"
        except FileNotFoundError:
            return False, "GitHub CLI (gh) not found. Please install it from https://cli.github.com/"
        except Exception as e:
            # Log full exception but return sanitized message
            print(f"DEBUG: Unexpected error: {type(e).__name__}: {str(e)}", file=sys.stderr)
            return False, "Error triggering workflow: An unexpected error occurred"
    
    def get_workflow_runs(self, workflow_id: str, limit: int = 5) -> Tuple[bool, List[Dict]]:
        """
        Get recent runs of a workflow
        
        Args:
            workflow_id: ID of the workflow
            limit: Maximum number of runs to return
            
        Returns:
            Tuple of (success: bool, runs: List[Dict])
        """
        auth_ok, auth_msg = self.check_gh_auth()
        if not auth_ok:
            return False, []
        
        workflow = self.get_workflow_info(workflow_id)
        if not workflow:
            return False, []
        
        workflow_file = workflow['file']
        
        try:
            result = subprocess.run(
                ['gh', 'run', 'list', '--workflow', workflow_file, '--limit', str(limit), '--json', 
                 'databaseId,conclusion,status,createdAt,headBranch'],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.base_path
            )
            
            if result.returncode == 0:
                runs = json.loads(result.stdout)
                return True, runs
            else:
                return False, []
                
        except json.JSONDecodeError as e:
            print(f"DEBUG: Failed to parse workflow runs JSON: {e}", file=sys.stderr)
            return False, []
        except subprocess.TimeoutExpired:
            return False, []
        except subprocess.CalledProcessError:
            return False, []
        except Exception as e:
            print(f"DEBUG: Unexpected error fetching workflow runs: {type(e).__name__}", file=sys.stderr)
            return False, []


def print_workflows(launcher: WorkflowLauncher):
    """Print available workflows in a formatted list"""
    workflows = launcher.list_workflows()
    
    print("\nAvailable GitHub Actions Workflows:")
    print("-" * 80)
    
    for i, workflow in enumerate(workflows, 1):
        print(f"\n{i}. {workflow['name']} ({workflow['id']})")
        print(f"   Description: {workflow['description']}")
        print(f"   File: .github/workflows/{workflow['file']}")
        if workflow['has_inputs']:
            print(f"   Inputs: Available (configure when launching)")
    
    print("-" * 80)


def main():
    """CLI entry point for workflow launcher"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='GitHub Actions Workflow Launcher'
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available workflows')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Trigger a workflow')
    run_parser.add_argument('workflow_id', help='ID of the workflow to trigger')
    run_parser.add_argument('--branch', default='preview', help='Branch to run on (default: preview)')
    run_parser.add_argument('--input', action='append', help='Workflow input in key=value format')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check workflow run status')
    status_parser.add_argument('workflow_id', help='ID of the workflow')
    status_parser.add_argument('--limit', type=int, default=5, help='Number of runs to show')
    
    args = parser.parse_args()
    
    launcher = WorkflowLauncher()
    
    if args.command == 'list':
        print_workflows(launcher)
        return 0
    
    elif args.command == 'run':
        # Parse inputs
        inputs = {}
        if args.input:
            for inp in args.input:
                if '=' in inp:
                    key, value = inp.split('=', 1)
                    inputs[key] = value
        
        print(f"Triggering workflow '{args.workflow_id}' on branch '{args.branch}'...")
        if inputs:
            print(f"Inputs: {inputs}")
        
        success, message = launcher.trigger_workflow(args.workflow_id, args.branch, inputs)
        print(message)
        return 0 if success else 1
    
    elif args.command == 'status':
        print(f"Recent runs of workflow '{args.workflow_id}':")
        success, runs = launcher.get_workflow_runs(args.workflow_id, args.limit)
        
        if success and runs:
            print("-" * 80)
            for run in runs:
                status = run.get('status', 'unknown')
                conclusion = run.get('conclusion', '-')
                branch = run.get('headBranch', '-')
                created = run.get('createdAt', '-')
                print(f"Run #{run.get('databaseId')}: {status} / {conclusion} (branch: {branch}, created: {created})")
            print("-" * 80)
        elif success:
            print("No recent runs found.")
        else:
            print("Failed to fetch workflow runs.")
        
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
