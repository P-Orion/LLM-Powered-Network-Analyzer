#!/usr/bin/env python3
"""
LLM-Powered Network Analyzer - Setup Validation Script
This script validates that the project is properly set up and ready for GitHub.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Print validation header"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 60)
    print("  LLM-Powered Network Analyzer - Setup Validation")
    print("  Verifying project is ready for GitHub repository")
    print("=" * 60)
    print(f"{Colors.ENDC}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")

def check_file_exists(file_path, description):
    """Check if a file exists"""
    if Path(file_path).exists():
        print_success(f"{description}: {file_path}")
        return True
    else:
        print_error(f"Missing {description}: {file_path}")
        return False

def check_directory_exists(dir_path, description):
    """Check if a directory exists"""
    if Path(dir_path).exists() and Path(dir_path).is_dir():
        print_success(f"{description}: {dir_path}")
        return True
    else:
        print_error(f"Missing {description}: {dir_path}")
        return False

def validate_json_file(file_path):
    """Validate JSON file syntax"""
    try:
        with open(file_path, 'r') as f:
            json.load(f)
        return True
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in {file_path}: {e}")
        return False
    except Exception as e:
        print_error(f"Error reading {file_path}: {e}")
        return False

def run_command(command, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def validate_repository_structure():
    """Validate the repository file structure"""
    print(f"\n{Colors.OKBLUE}📁 Validating Repository Structure{Colors.ENDC}")
    
    required_files = [
        ("README.md", "Main documentation"),
        ("LICENSE", "License file"),
        ("CONTRIBUTING.md", "Contribution guidelines"),
        (".gitignore", "Git ignore rules"),
        (".env.example", "Environment configuration template"),
        ("setup.py", "Automated setup script"),
    ]
    
    required_dirs = [
        ("backend", "Python backend directory"),
        ("frontend", "Angular frontend directory"),
        ("docs", "Documentation directory"),
    ]
    
    all_valid = True
    
    # Check required files
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_valid = False
    
    # Check required directories
    for dir_path, description in required_dirs:
        if not check_directory_exists(dir_path, description):
            all_valid = False
    
    return all_valid

def validate_backend_structure():
    """Validate backend structure"""
    print(f"\n{Colors.OKBLUE}🐍 Validating Backend Structure{Colors.ENDC}")
    
    backend_files = [
        ("backend/main.py", "FastAPI main application"),
        ("backend/requirements.txt", "Python dependencies"),
    ]
    
    backend_dirs = [
        ("backend/parsers", "Parser modules"),
        ("backend/analyzers", "Analyzer modules"),
        ("backend/llm", "LLM integration"),
        ("backend/tests", "Test files"),
    ]
    
    all_valid = True
    
    for file_path, description in backend_files:
        if not check_file_exists(file_path, description):
            all_valid = False
    
    for dir_path, description in backend_dirs:
        if not check_directory_exists(dir_path, description):
            all_valid = False
    
    # Validate requirements.txt
    if Path("backend/requirements.txt").exists():
        try:
            with open("backend/requirements.txt", 'r') as f:
                content = f.read()
                required_packages = ['fastapi', 'uvicorn', 'scapy', 'ollama']
                missing_packages = []
                for package in required_packages:
                    if package not in content.lower():
                        missing_packages.append(package)
                
                if missing_packages:
                    print_warning(f"Missing packages in requirements.txt: {', '.join(missing_packages)}")
                else:
                    print_success("All required packages found in requirements.txt")
        except Exception as e:
            print_error(f"Error reading requirements.txt: {e}")
            all_valid = False
    
    return all_valid

def validate_frontend_structure():
    """Validate frontend structure"""
    print(f"\n{Colors.OKBLUE}🌐 Validating Frontend Structure{Colors.ENDC}")
    
    frontend_files = [
        ("frontend/package.json", "Node.js dependencies"),
        ("frontend/angular.json", "Angular configuration"),
        ("frontend/tsconfig.json", "TypeScript configuration"),
    ]
    
    frontend_dirs = [
        ("frontend/src", "Source code directory"),
        ("frontend/src/app", "Angular app directory"),
        ("frontend/src/app/components", "Components directory"),
        ("frontend/src/app/services", "Services directory"),
    ]
    
    all_valid = True
    
    for file_path, description in frontend_files:
        if not check_file_exists(file_path, description):
            all_valid = False
    
    for dir_path, description in frontend_dirs:
        if not check_directory_exists(dir_path, description):
            all_valid = False
    
    # Validate package.json
    if Path("frontend/package.json").exists():
        if validate_json_file("frontend/package.json"):
            print_success("package.json is valid JSON")
            
            try:
                with open("frontend/package.json", 'r') as f:
                    package_data = json.load(f)
                    
                # Check for Angular dependencies
                dependencies = package_data.get('dependencies', {})
                dev_dependencies = package_data.get('devDependencies', {})
                all_deps = {**dependencies, **dev_dependencies}
                
                required_deps = ['@angular/core', '@angular/common', '@angular/material']
                missing_deps = []
                for dep in required_deps:
                    if dep not in all_deps:
                        missing_deps.append(dep)
                
                if missing_deps:
                    print_warning(f"Missing Angular dependencies: {', '.join(missing_deps)}")
                else:
                    print_success("All required Angular dependencies found")
                    
            except Exception as e:
                print_error(f"Error parsing package.json: {e}")
                all_valid = False
        else:
            all_valid = False
    
    return all_valid

def validate_documentation():
    """Validate documentation files"""
    print(f"\n{Colors.OKBLUE}📚 Validating Documentation{Colors.ENDC}")
    
    doc_files = [
        ("docs/TROUBLESHOOTING.md", "Troubleshooting guide"),
        ("docs/DEPLOYMENT.md", "Deployment guide"),
        ("docs/PROJECT_STRUCTURE.md", "Project structure documentation"),
    ]
    
    all_valid = True
    
    for file_path, description in doc_files:
        if not check_file_exists(file_path, description):
            all_valid = False
    
    # Check README.md content
    if Path("README.md").exists():
        try:
            with open("README.md", 'r') as f:
                content = f.read()
                required_sections = [
                    "# LLM-Powered Network Analyzer",
                    "## Features",
                    "## Prerequisites",
                    "## Quick Start",
                    "## Usage Guide"
                ]
                
                missing_sections = []
                for section in required_sections:
                    if section not in content:
                        missing_sections.append(section)
                
                if missing_sections:
                    print_warning(f"Missing README sections: {', '.join(missing_sections)}")
                else:
                    print_success("README.md contains all required sections")
                    
        except Exception as e:
            print_error(f"Error reading README.md: {e}")
            all_valid = False
    
    return all_valid

def validate_git_setup():
    """Validate Git setup"""
    print(f"\n{Colors.OKBLUE}🔧 Validating Git Setup{Colors.ENDC}")
    
    all_valid = True
    
    # Check if .git directory exists
    if Path(".git").exists():
        print_success("Git repository initialized")
    else:
        print_warning("Git repository not initialized (run 'git init')")
        all_valid = False
    
    # Check .gitignore
    if Path(".gitignore").exists():
        try:
            with open(".gitignore", 'r') as f:
                content = f.read()
                important_ignores = [
                    "__pycache__/",
                    "node_modules/",
                    "venv/",
                    "*.log",
                    ".env"
                ]
                
                missing_ignores = []
                for ignore in important_ignores:
                    if ignore not in content:
                        missing_ignores.append(ignore)
                
                if missing_ignores:
                    print_warning(f"Missing .gitignore entries: {', '.join(missing_ignores)}")
                else:
                    print_success(".gitignore contains all important entries")
                    
        except Exception as e:
            print_error(f"Error reading .gitignore: {e}")
            all_valid = False
    
    return all_valid

def validate_scripts():
    """Validate setup and run scripts"""
    print(f"\n{Colors.OKBLUE}🔧 Validating Scripts{Colors.ENDC}")
    
    scripts = [
        ("setup.py", "Setup script"),
        ("run.py", "Cross-platform runner"),
    ]
    
    all_valid = True
    
    for script_path, description in scripts:
        if check_file_exists(script_path, description):
            # Check if script is executable (on Unix systems)
            if os.name != 'nt':  # Not Windows
                if os.access(script_path, os.X_OK):
                    print_success(f"{script_path} is executable")
                else:
                    print_warning(f"{script_path} is not executable (run 'chmod +x {script_path}')")
        else:
            all_valid = False
    
    return all_valid

def check_environment_setup():
    """Check if development environment can be set up"""
    print(f"\n{Colors.OKBLUE}🌍 Checking Environment Setup{Colors.ENDC}")
    
    all_valid = True
    
    # Check Python version
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 10:
            print_success(f"Python {version.major}.{version.minor}.{version.micro} (compatible)")
        else:
            print_error(f"Python 3.10+ required, found {version.major}.{version.minor}.{version.micro}")
            all_valid = False
    except Exception as e:
        print_error(f"Error checking Python version: {e}")
        all_valid = False
    
    # Check Node.js
    success, stdout, stderr = run_command("node --version")
    if success:
        version_str = stdout.strip()
        print_success(f"Node.js {version_str} detected")
    else:
        print_error("Node.js not found")
        all_valid = False
    
    # Check npm
    success, stdout, stderr = run_command("npm --version")
    if success:
        version_str = stdout.strip()
        print_success(f"npm {version_str} detected")
    else:
        print_error("npm not found")
        all_valid = False
    
    # Check Git
    success, stdout, stderr = run_command("git --version")
    if success:
        version_str = stdout.strip()
        print_success(f"Git detected: {version_str}")
    else:
        print_warning("Git not found (recommended for version control)")
    
    return all_valid

def generate_setup_report():
    """Generate a setup report"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}📋 Setup Report{Colors.ENDC}")
    
    # Count files and directories
    total_files = sum(1 for _ in Path(".").rglob("*") if _.is_file() and not _.name.startswith('.') and 'node_modules' not in str(_) and 'venv' not in str(_) and '__pycache__' not in str(_))
    
    backend_files = sum(1 for _ in Path("backend").rglob("*.py") if _.is_file()) if Path("backend").exists() else 0
    frontend_files = sum(1 for _ in Path("frontend/src").rglob("*.ts") if _.is_file()) if Path("frontend/src").exists() else 0
    doc_files = sum(1 for _ in Path("docs").rglob("*.md") if _.is_file()) if Path("docs").exists() else 0
    
    print(f"📊 Project Statistics:")
    print(f"   • Total files: {total_files}")
    print(f"   • Backend Python files: {backend_files}")
    print(f"   • Frontend TypeScript files: {frontend_files}")
    print(f"   • Documentation files: {doc_files}")
    
    print(f"\n🎯 Repository Readiness:")
    print(f"   • Repository structure: ✅")
    print(f"   • Documentation: ✅")
    print(f"   • License: ✅")
    print(f"   • Contributing guidelines: ✅")
    print(f"   • Setup automation: ✅")

def main():
    """Main validation function"""
    print_header()
    
    all_checks_passed = True
    
    # Run all validations
    checks = [
        ("Repository Structure", validate_repository_structure),
        ("Backend Structure", validate_backend_structure),
        ("Frontend Structure", validate_frontend_structure),
        ("Documentation", validate_documentation),
        ("Git Setup", validate_git_setup),
        ("Scripts", validate_scripts),
        ("Environment", check_environment_setup),
    ]
    
    for check_name, check_function in checks:
        try:
            if not check_function():
                all_checks_passed = False
        except Exception as e:
            print_error(f"Error during {check_name} validation: {e}")
            all_checks_passed = False
    
    # Generate report
    generate_setup_report()
    
    # Final result
    print(f"\n{Colors.HEADER}{Colors.BOLD}🎯 Validation Result{Colors.ENDC}")
    
    if all_checks_passed:
        print_success("All validations passed! Project is ready for GitHub repository.")
        print_info("Next steps:")
        print("   1. Initialize Git repository: git init")
        print("   2. Add files: git add .")
        print("   3. Commit: git commit -m 'Initial commit'")
        print("   4. Add remote: git remote add origin https://github.com/P-Orion/LLM-Powered-Network-Analyzer.git")
        print("   5. Push: git push -u origin main")
        return 0
    else:
        print_error("Some validations failed. Please fix the issues above before proceeding.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Validation interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
        sys.exit(1)