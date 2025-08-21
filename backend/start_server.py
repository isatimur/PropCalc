#!/usr/bin/env python3
"""
Startup script for PropCalc FastAPI server
This script sets the correct Python path and starts the server
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Now we can import and run the app
if __name__ == "__main__":
    import uvicorn
    from propcalc.main import app
    
    print("🚀 Starting PropCalc FastAPI server...")
    print(f"📁 Python path includes: {src_path}")
    print("🌐 Server will be available at: http://localhost:8001")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
