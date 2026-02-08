"""
Smart Civic Issue Reporter - Startup Script
AI Innovation Challenge 2026
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("🏙️  Smart Civic Issue Reporter")
print("   AI Innovation Challenge 2026")
print("=" * 60)
print()

# Check if dependencies are installed
try:
    import fastapi
    import uvicorn
    print("✅ Dependencies found!")
except ImportError as e:
    print("❌ Missing dependencies!")
    print(f"   Error: {e}")
    print()
    print("📦 Please run: pip install -r requirements.txt")
    print()
    sys.exit(1)

print()
print("🚀 Starting server...")
print()
print("📍 Application will be available at:")
print("   → http://localhost:8000")
print("   → http://127.0.0.1:8000")
print()
print("👤 Demo Credentials:")
print("   Admin: admin / admin123")
print("   Citizen: citizen1 / pass123")
print()
print("Press Ctrl+C to stop the server")
print("=" * 60)
print()

# Import and run the FastAPI app from api.py
try:
    from api import app
    print("✅ Loaded app from api.py")
except ImportError:
    print("⚠️  Could not import from api.py, trying backend.main...")
    try:
        from backend.main import app
        print("✅ Loaded app from backend.main")
    except ImportError as e:
        print(f"❌ Error: {e}")
        print()
        print("Make sure you have either:")
        print("  - api.py file in this folder, OR")
        print("  - backend/main.py file")
        sys.exit(1)

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )