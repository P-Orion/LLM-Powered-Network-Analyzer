#!/usr/bin/env python3
"""
LLM-Powered Network Analyzer - Automated Setup Script
This script handles the complete setup process for the application.
"""

import os
import sys
import subprocess
import platform
import shutil
import time
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
    UNDERLINE = '\033[4m'

def print_header():
    """Print application header"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 60)
    print("  LLM-Powered Network Analyzer - Setup Script")
    print("  Privacy-focused network packet analysis tool")
    print("=" * 60)
    print(f"{Colors.ENDC}")

def print_step(step_num, total_steps, message):
    """Print step progress"""
    print(f"{Colors.OKBLUE}[{step_num}/{total_steps}] {message}...{Colors.ENDC}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

def run_command(command, cwd=None, shell=True):
    """Run a command and return success status"""
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_python_version():
    """Check if Python version is 3.10 or higher"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print_error(f"Python 3.10+ required. Current version: {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_node_version():
    """Check if Node.js version is 20 or higher"""
    success, stdout, stderr = run_command("node --version")
    if not success:
        print_error("Node.js not found. Please install Node.js 20+ from https://nodejs.org/")
        return False
    
    try:
        version_str = stdout.strip().replace('v', '')
        major_version = int(version_str.split('.')[0])
        if major_version < 20:
            print_error(f"Node.js 20+ required. Current version: {version_str}")
            return False
        print_success(f"Node.js {version_str} detected")
        return True
    except:
        print_error("Could not parse Node.js version")
        return False

def check_git():
    """Check if Git is installed"""
    success, stdout, stderr = run_command("git --version")
    if not success:
        print_warning("Git not found. You may need to install Git for version control.")
        return False
    print_success("Git detected")
    return True

def install_ollama():
    """Install Ollama if not present"""
    success, stdout, stderr = run_command("ollama --version")
    if success:
        print_success("Ollama already installed")
        return True
    
    print("Installing Ollama...")
    system = platform.system().lower()
    
    if system == "windows":
        print_warning("Please install Ollama manually from https://ollama.com/")
        print("After installation, run this script again.")
        return False
    else:
        # macOS and Linux
        success, stdout, stderr = run_command("curl -fsSL https://ollama.com/install.sh | sh")
        if success:
            print_success("Ollama installed successfully")
            return True
        else:
            print_error(f"Failed to install Ollama: {stderr}")
            return False

def pull_gemma_model():
    """Pull Gemma 2 12B model"""
    print("Checking for Gemma 2 12B model...")
    success, stdout, stderr = run_command("ollama list")
    
    if "gemma2:12b" in stdout:
        print_success("Gemma 2 12B model already available")
        return True
    
    print("Pulling Gemma 2 12B model (this may take several minutes)...")
    success, stdout, stderr = run_command("ollama pull gemma2:12b")
    
    if success:
        print_success("Gemma 2 12B model downloaded successfully")
        return True
    else:
        print_error(f"Failed to pull Gemma model: {stderr}")
        return False

def setup_backend():
    """Set up Python backend"""
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print_error("Backend directory not found")
        return False
    
    # Create virtual environment
    venv_dir = backend_dir / "venv"
    if not venv_dir.exists():
        print("Creating Python virtual environment...")
        success, stdout, stderr = run_command(f"{sys.executable} -m venv venv", cwd=backend_dir)
        if not success:
            print_error(f"Failed to create virtual environment: {stderr}")
            return False
        print_success("Virtual environment created")
    else:
        print_success("Virtual environment already exists")
    
    # Determine activation script path
    system = platform.system().lower()
    if system == "windows":
        activate_script = venv_dir / "Scripts" / "activate.bat"
        pip_path = venv_dir / "Scripts" / "pip.exe"
    else:
        activate_script = venv_dir / "bin" / "activate"
        pip_path = venv_dir / "bin" / "pip"
    
    # Install Python dependencies
    print("Installing Python dependencies...")
    requirements_file = backend_dir / "requirements.txt"
    if requirements_file.exists():
        success, stdout, stderr = run_command(f'"{pip_path}" install -r requirements.txt', cwd=backend_dir)
        if success:
            print_success("Python dependencies installed")
            return True
        else:
            print_error(f"Failed to install Python dependencies: {stderr}")
            return False
    else:
        print_error("requirements.txt not found in backend directory")
        return False

def setup_frontend():
    """Set up Angular frontend"""
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print_error("Frontend directory not found")
        return False
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        print_success("Frontend dependencies already installed")
        return True
    
    # Install Angular CLI globally if not present
    print("Checking Angular CLI...")
    success, stdout, stderr = run_command("ng version")
    if not success:
        print("Installing Angular CLI globally...")
        success, stdout, stderr = run_command("npm install -g @angular/cli@18")
        if not success:
            print_warning("Failed to install Angular CLI globally. Continuing with local installation...")
    
    # Install frontend dependencies
    print("Installing frontend dependencies...")
    success, stdout, stderr = run_command("npm install", cwd=frontend_dir)
    if success:
        print_success("Frontend dependencies installed")
        return True
    else:
        print_error(f"Failed to install frontend dependencies: {stderr}")
        return False

def generate_test_data():
    """Generate test PCAPNG files"""
    test_script = Path("backend/tests/generate_test_pcapng.py")
    if not test_script.exists():
        print_warning("Test data generator not found, skipping...")
        return True
    
    print("Generating test PCAPNG files...")
    backend_dir = Path("backend")
    system = platform.system().lower()
    
    if system == "windows":
        python_path = backend_dir / "venv" / "Scripts" / "python.exe"
    else:
        python_path = backend_dir / "venv" / "bin" / "python"
    
    success, stdout, stderr = run_command(f'"{python_path}" tests/generate_test_pcapng.py', cwd=backend_dir)
    if success:
        print_success("Test PCAPNG files generated")
        return True
    else:
        print_warning(f"Could not generate test files: {stderr}")
        return True  # Non-critical failure

def create_startup_scripts():
    """Create convenient startup scripts"""
    system = platform.system().lower()
    
    if system == "windows":
        # Create Windows batch file
        batch_content = '''@echo off
echo Starting LLM-Powered Network Analyzer...
echo.

echo Starting backend server...
cd backend
call venv\\Scripts\\activate.bat
start "Backend Server" cmd /k "python main.py"
cd ..

echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo Starting frontend server...
cd frontend
start "Frontend Server" cmd /k "ng serve"
cd ..

echo.
echo ✅ Both servers are starting...
echo ✅ Backend will be available at: http://localhost:8000
echo ✅ Frontend will be available at: http://localhost:4200
echo.
echo Press any key to open the application in your browser...
pause > nul
start http://localhost:4200
'''
        with open("start.bat", "w") as f:
            f.write(batch_content)
        print_success("Created start.bat for Windows")
    
    else:
        # Create shell script for macOS/Linux
        shell_content = '''#!/bin/bash
echo "Starting LLM-Powered Network Analyzer..."
echo

echo "Starting backend server..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

echo "Waiting for backend to start..."
sleep 3

echo "Starting frontend server..."
cd frontend
ng serve &
FRONTEND_PID=$!
cd ..

echo
echo "✅ Both servers are starting..."
echo "✅ Backend will be available at: http://localhost:8000"
echo "✅ Frontend will be available at: http://localhost:4200"
echo
echo "Opening application in browser..."
sleep 5

# Try to open browser
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:4200
elif command -v open > /dev/null; then
    open http://localhost:4200
fi

echo "Press Ctrl+C to stop both servers"
wait
'''
        with open("start.sh", "w") as f:
            f.write(shell_content)
        os.chmod("start.sh", 0o755)
        print_success("Created start.sh for macOS/Linux")

def main():
    """Main setup function"""
    print_header()
    
    total_steps = 9
    current_step = 0
    
    # Step 1: Check prerequisites
    current_step += 1
    print_step(current_step, total_steps, "Checking prerequisites")
    
    if not check_python_version():
        sys.exit(1)
    
    if not check_node_version():
        sys.exit(1)
    
    check_git()  # Non-critical
    
    # Step 2: Install Ollama
    current_step += 1
    print_step(current_step, total_steps, "Installing Ollama")
    
    if not install_ollama():
        print_error("Ollama installation failed. Please install manually and run setup again.")
        sys.exit(1)
    
    # Step 3: Pull Gemma model
    current_step += 1
    print_step(current_step, total_steps, "Downloading Gemma 2 12B model")
    
    if not pull_gemma_model():
        print_error("Failed to download Gemma model. Please check your internet connection.")
        sys.exit(1)
    
    # Step 4: Setup backend
    current_step += 1
    print_step(current_step, total_steps, "Setting up Python backend")
    
    if not setup_backend():
        print_error("Backend setup failed")
        sys.exit(1)
    
    # Step 5: Setup frontend
    current_step += 1
    print_step(current_step, total_steps, "Setting up Angular frontend")
    
    if not setup_frontend():
        print_error("Frontend setup failed")
        sys.exit(1)
    
    # Step 6: Generate test data
    current_step += 1
    print_step(current_step, total_steps, "Generating test data")
    
    generate_test_data()  # Non-critical
    
    # Step 7: Create startup scripts
    current_step += 1
    print_step(current_step, total_steps, "Creating startup scripts")
    
    create_startup_scripts()
    
    # Step 8: Final verification
    current_step += 1
    print_step(current_step, total_steps, "Running final verification")
    
    # Verify Ollama is working
    success, stdout, stderr = run_command("ollama list")
    if not success or "gemma2:12b" not in stdout:
        print_warning("Ollama verification failed. You may need to restart Ollama service.")
    else:
        print_success("Ollama verification passed")
    
    # Step 9: Complete
    current_step += 1
    print_step(current_step, total_steps, "Setup complete")
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}")
    print("🎉 Setup completed successfully!")
    print(f"{Colors.ENDC}")
    
    print(f"{Colors.OKCYAN}")
    print("Next steps:")
    print("1. Run the application:")
    
    system = platform.system().lower()
    if system == "windows":
        print("   • Double-click start.bat")
        print("   • Or run: python run.py")
    else:
        print("   • Run: ./start.sh")
        print("   • Or run: python3 run.py")
    
    print("\n2. Open your browser to: http://localhost:4200")
    print("\n3. Upload a PCAPNG file to test the analysis")
    print("\n4. Use test files in backend/tests/ for testing")
    print(f"{Colors.ENDC}")
    
    # Ask if user wants to start now
    try:
        response = input(f"\n{Colors.BOLD}Would you like to start the application now? (y/N): {Colors.ENDC}")
        if response.lower() in ['y', 'yes']:
            print("\nStarting application...")
            if system == "windows":
                subprocess.Popen(["start.bat"], shell=True)
            else:
                subprocess.Popen(["./start.sh"], shell=True)
    except KeyboardInterrupt:
        print(f"\n{Colors.OKGREEN}Setup completed. Run the application when ready!{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Setup interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
        sys.exit(1)