#!/usr/bin/env python3
"""
Quick Setup and Run Script for AI Civic Issue Reporter
AI Innovation Challenge 2026 - Gandhinagar
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def print_banner():
    """Print welcome banner"""
    print("\n" + "=" * 70)
    print("  🏙️  AI-POWERED CIVIC ISSUE REPORTER")
    print("  IBM SkillsBuild | CSRBOX | AI Innovation Challenge 2026")
    print("=" * 70 + "\n")


def print_section(title):
    """Print section header"""
    print(f"\n{'─' * 70}")
    print(f"  {title}")
    print(f"{'─' * 70}\n")


def check_python_version():
    """Check if Python version is compatible"""
    print_section("Checking Python Version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ERROR: Python 3.8 or higher is required")
        print("Please upgrade Python and try again")
        sys.exit(1)
    
    print("✓ Python version is compatible")
    return True


def install_dependencies():
    """Install required Python packages"""
    print_section("Installing Dependencies")
    
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ ERROR: requirements.txt not found")
        sys.exit(1)
    
    print("Installing Python packages (this may take a few minutes)...")
    print("Please wait...\n")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"],
            check=True
        )
        print("✓ All dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ ERROR: Failed to install dependencies")
        print("Try running manually: pip install -r requirements.txt")
        sys.exit(1)


def generate_sample_data():
    """Generate synthetic training data"""
    print_section("Generating Sample Data")
    
    db_file = Path("civic_issues.db")
    
    if db_file.exists():
        print("Database already exists. Skipping data generation.")
        print("To regenerate, delete civic_issues.db and run again.")
        return
    
    print("Generating 800 synthetic civic issues for training...")
    print("This will take about 10-15 seconds...\n")
    
    try:
        subprocess.run([sys.executable, "data_generator.py"], check=True)
        print("\n✓ Sample data generated successfully")
    except subprocess.CalledProcessError:
        print("❌ ERROR: Failed to generate sample data")
        print("You can skip this step and the system will work with empty database")
    except FileNotFoundError:
        print("⚠️  data_generator.py not found. Skipping sample data generation.")


def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    
    if env_file.exists():
        return
    
    print_section("Creating Environment Configuration")
    
    env_content = """# AI Civic Issue Reporter Configuration
DATABASE_URL=sqlite:///./civic_issues.db
SECRET_KEY=civic-ai-secret-key-change-in-production-2026
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✓ Environment configuration created")


def display_startup_info():
    """Display startup information"""
    print_section("🚀 Starting API Server")
    
    print("The AI Civic Issue Reporter API is starting...")
    print("\n📍 Access Points:")
    print("   • API Base URL:        http://localhost:8000")
    print("   • Swagger UI Docs:     http://localhost:8000/docs")
    print("   • ReDoc:               http://localhost:8000/redoc")
    print("   • Health Check:        http://localhost:8000/api/health")
    
    print("\n🤖 AI Features Enabled:")
    print("   ✓ Automatic Issue Classification")
    print("   ✓ Priority Prediction")
    print("   ✓ Duplicate Detection")
    print("   ✓ Solution Suggestions")
    print("   ✓ Predictive Analytics")
    print("   ✓ Hotspot Identification")
    
    print("\n💡 Quick Start:")
    print("   1. Open http://localhost:8000/docs in your browser")
    print("   2. Try the /api/health endpoint")
    print("   3. Register a user with /api/auth/register")
    print("   4. Create an issue with /api/issues/create")
    print("   5. View analytics at /api/analytics/dashboard")
    
    print("\n⚠️  Note: Press Ctrl+C to stop the server")
    print("\n" + "=" * 70 + "\n")
    
    time.sleep(2)


def start_server():
    """Start the FastAPI server"""
    try:
        import uvicorn
        uvicorn.run(
            "api:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except ImportError:
        print("❌ ERROR: uvicorn not installed")
        print("Run: pip install uvicorn")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped gracefully")
        print("Thank you for using AI Civic Issue Reporter!")
        sys.exit(0)


def show_menu():
    """Show interactive menu"""
    print_banner()
    
    print("What would you like to do?\n")
    print("1. Quick Start (Setup + Run Server)")
    print("2. Only Setup (Install dependencies + Generate data)")
    print("3. Only Run Server")
    print("4. Generate Sample Data Only")
    print("5. Check System Status")
    print("6. Exit")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    return choice


def check_system_status():
    """Check system status"""
    print_section("System Status Check")
    
    # Check Python
    print("Python:", "✓" if sys.version_info >= (3, 8) else "❌")
    
    # Check files
    files = ["api.py", "ai_engine.py", "requirements.txt", "data_generator.py"]
    for file in files:
        exists = Path(file).exists()
        status = "✓" if exists else "❌"
        print(f"{file:25s}: {status}")
    
    # Check database
    db_exists = Path("civic_issues.db").exists()
    print(f"{'Database (civic_issues.db)':25s}: {'✓' if db_exists else '❌ (will be created)'}")
    
    # Check dependencies
    try:
        import fastapi
        import sqlalchemy
        import sklearn
        print(f"{'Dependencies':25s}: ✓")
    except ImportError:
        print(f"{'Dependencies':25s}: ❌ (need installation)")
    
    print("\nPress Enter to continue...")
    input()


def main():
    """Main function"""
    os.chdir(Path(__file__).parent)
    
    while True:
        choice = show_menu()
        
        if choice == "1":
            # Quick Start
            check_python_version()
            install_dependencies()
            create_env_file()
            generate_sample_data()
            display_startup_info()
            start_server()
            break
            
        elif choice == "2":
            # Only Setup
            check_python_version()
            install_dependencies()
            create_env_file()
            generate_sample_data()
            print("\n✓ Setup complete! Run option 3 to start the server.")
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            # Only Run Server
            display_startup_info()
            start_server()
            break
            
        elif choice == "4":
            # Generate Data Only
            generate_sample_data()
            input("\nPress Enter to continue...")
            
        elif choice == "5":
            # Check Status
            check_system_status()
            
        elif choice == "6":
            # Exit
            print("\n✓ Goodbye! Good luck with the AI Innovation Challenge! 🚀\n")
            sys.exit(0)
            
        else:
            print("\n❌ Invalid choice. Please try again.")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nFor help, check README.md or run manually:")
        print("  1. pip install -r requirements.txt")
        print("  2. python data_generator.py")
        print("  3. python api.py")
        sys.exit(1)