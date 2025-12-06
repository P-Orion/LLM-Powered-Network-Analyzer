#!/usr/bin/env python3
"""
Single-command launcher for Network Log Analyzer
Starts both backend and frontend with one command
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path

def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("  🔍 Network Log Analyzer - PCAPNG Analysis Tool")
    print("=" * 60)
    print()

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    try:
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 10):
            print("❌ Python 3.10+ required. Current version:", sys.version)
            return False
        print("✅ Python:", sys.version.split()[0])
    except Exception as e:
        print("❌ Python check failed:", e)
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Node.js:", result.stdout.strip())
        else:
            print("❌ Node.js not found. Please install from https://nodejs.org")
            return False
    except Exception:
        print("❌ Node.js not found. Please install from https://nodejs.org")
        return False
    
    # Check Ollama
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # Check for various Gemma model names
            models_output = result.stdout.lower()
            if any(model in models_output for model in ['gemma2:12b', 'gemma:12b', 'gemma2', 'gemma']):
                print("✅ Ollama with Gemma model found")
                # Extract model names without backslash in f-string
                model_lines = [line.strip() for line in result.stdout.split('\n') if line.strip() and not line.startswith('NAME')]
                print(f"   Available models: {model_lines}")
            else:
                print("⚠️  Ollama found but no Gemma model detected")
                print("   Available models:")
                for line in result.stdout.split('\n'):
                    if line.strip() and not line.startswith('NAME'):
                        print(f"     - {line.strip()}")
                print("   If you have a Gemma model installed, the application will still work.")
                print("   Continuing with setup...")
        else:
            print("❌ Ollama not found. Please install from https://ollama.com")
            return False
    except Exception:
        print("❌ Ollama not found. Please install from https://ollama.com")
        return False
    
    print("✅ All prerequisites met!")
    print()
    return True

def setup_backend():
    """Setup backend environment"""
    print("🔧 Setting up backend...")
    
    backend_dir = Path("backend")
    venv_dir = backend_dir / "venv"
    
    # Create virtual environment if it doesn't exist
    if not venv_dir.exists():
        print("   Creating Python virtual environment...")
        result = subprocess.run([sys.executable, '-m', 'venv', str(venv_dir)], 
                              cwd=backend_dir, capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Failed to create virtual environment")
            print(result.stderr)
            return False
    
    # Determine Python executable in venv
    if os.name == 'nt':  # Windows
        python_exe = venv_dir / "Scripts" / "python.exe"
        pip_exe = venv_dir / "Scripts" / "pip.exe"
    else:  # Unix/Linux/macOS
        python_exe = venv_dir / "bin" / "python"
        pip_exe = venv_dir / "bin" / "pip"
    
    # Install dependencies
    print("   Installing Python dependencies...")
    result = subprocess.run([str(pip_exe), 'install', '-r', 'requirements.txt'], 
                          cwd=backend_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Failed to install Python dependencies")
        print(result.stderr)
        return False
    
    print("✅ Backend setup complete")
    return str(python_exe)

def setup_frontend():
    """Setup frontend environment"""
    print("🔧 Setting up frontend...")
    
    frontend_dir = Path("frontend")
    
    # Check if Angular CLI is installed
    try:
        result = subprocess.run(['ng', 'version'], capture_output=True, text=True, timeout=10, shell=True)
        if result.returncode != 0:
            print("   Installing Angular CLI...")
            install_result = subprocess.run(['npm', 'install', '-g', '@angular/cli'],
                                          capture_output=True, text=True, timeout=120, shell=True)
            if install_result.returncode != 0:
                print("⚠️  Angular CLI installation failed, but continuing...")
                print("   You may need to install it manually: npm install -g @angular/cli")
    except Exception as e:
        print("⚠️  Angular CLI check failed, but continuing...")
        print(f"   Error: {e}")
    
    # Install dependencies
    print("   Installing Node.js dependencies...")
    result = subprocess.run(['npm', 'install'], cwd=frontend_dir, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        print("❌ Failed to install Node.js dependencies")
        print(result.stderr)
        return False
    
    print("✅ Frontend setup complete")
    return True

def start_backend(python_exe):
    """Start backend server"""
    print("Starting backend server...")
    
    backend_dir = Path("backend")
    
    try:
        # Start backend process with UTF-8 encoding
        process = subprocess.Popen(
            [python_exe, 'main.py'],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Monitor backend startup
        for line in process.stdout:
            try:
                print(f"   Backend: {line.strip()}")
                if "Uvicorn running on" in line or "Application startup complete" in line:
                    print("Backend server started on http://localhost:8000")
                    break
            except UnicodeError:
                continue  # Skip problematic lines
            if process.poll() is not None:
                print("Backend server failed to start")
                return None
        
        return process
        
    except Exception as e:
        print(f"Failed to start backend: {e}")
        return None

def start_frontend():
    """Start frontend server"""
    print("Starting frontend server...")
    
    frontend_dir = Path("frontend")
    
    try:
        # Start frontend process with UTF-8 encoding
        process = subprocess.Popen(
            ['ng', 'serve', '--port', '4200'],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            shell=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Monitor frontend startup with timeout
        startup_timeout = 60  # 60 seconds timeout
        start_time = time.time()
        
        for line in process.stdout:
            try:
                print(f"   Frontend: {line.strip()}")
                if "Local:" in line and "4200" in line:
                    print("Frontend server started on http://localhost:4200")
                    break
                if "compiled successfully" in line.lower():
                    print("Frontend compiled successfully")
                    break
            except UnicodeError:
                continue  # Skip problematic lines
            if process.poll() is not None:
                print("Frontend server failed to start")
                return None
            if time.time() - start_time > startup_timeout:
                print("Frontend server starting (continuing in background)")
                break
        
        return process
        
    except Exception as e:
        print(f"Failed to start frontend: {e}")
        return None

def open_browser():
    """Open browser after delay"""
    time.sleep(3)
    print("🌐 Opening browser...")
    webbrowser.open('http://localhost:4200')

def main():
    """Main launcher function"""
    print_banner()
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites not met. Please install missing components.")
        input("Press Enter to exit...")
        return 1
    
    # Setup backend
    python_exe = setup_backend()
    if not python_exe:
        print("❌ Backend setup failed")
        input("Press Enter to exit...")
        return 1
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed")
        input("Press Enter to exit...")
        return 1
    
    print()
    print("🚀 Starting servers...")
    print()
    
    # Start backend
    backend_process = start_backend(python_exe)
    if not backend_process:
        input("Press Enter to exit...")
        return 1
    
    # Wait a moment for backend to fully start
    time.sleep(2)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        input("Press Enter to exit...")
        return 1
    
    # Open browser in background thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print()
    print("=" * 60)
    print("  🎉 Network Log Analyzer is running!")
    print("=" * 60)
    print("  Backend:  http://localhost:8000")
    print("  Frontend: http://localhost:4200")
    print()
    print("  📁 Upload .pcapng files to analyze network traffic")
    print("  🧪 Generate test files: cd backend/tests && python generate_test_pcapng.py")
    print()
    print("  Press Ctrl+C to stop both servers")
    print("=" * 60)
    
    try:
        # Wait for processes
        while True:
            if backend_process.poll() is not None:
                print("❌ Backend process stopped")
                break
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped")
                break
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        
        # Terminate processes
        try:
            backend_process.terminate()
            frontend_process.terminate()
            
            # Wait for graceful shutdown
            backend_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
            
        except subprocess.TimeoutExpired:
            # Force kill if needed
            backend_process.kill()
            frontend_process.kill()
        
        print("✅ Servers stopped")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())