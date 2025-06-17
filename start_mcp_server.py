#!/usr/bin/env python3
"""
MongoDB Vector RAG MCP Server Launcher

This script can run the MCP server in different modes:
- Default (STDIO): For MCP clients and automatic frontend integration
- HTTP mode: For direct HTTP access and testing

The frontend will automatically spawn the server in STDIO mode when needed.
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    # Get the project root directory
    project_root = Path(__file__).parent
    mcp_server_dir = project_root / "mongodb_mcp_server"
    
    # Check if the MCP server directory exists
    if not mcp_server_dir.exists():
        print(f"❌ Error: MCP server directory not found at {mcp_server_dir}")
        print("Make sure you're running this script from the project root.")
        sys.exit(1)
    
    # Check if main.py exists
    main_py = mcp_server_dir / "main.py"
    if not main_py.exists():
        print(f"❌ Error: main.py not found at {main_py}")
        sys.exit(1)
    
    # Check for virtual environment
    venv_python = None
    if os.name == 'nt':  # Windows
        venv_python = mcp_server_dir / "venv" / "Scripts" / "python.exe"
    else:  # Unix/Linux/macOS
        venv_python = mcp_server_dir / "venv" / "bin" / "python"
    
    # Use venv python if available, otherwise system python
    if venv_python.exists():
        python_cmd = str(venv_python)
        print(f"🐍 Using virtual environment: {python_cmd}")
    else:
        python_cmd = "python"
        print(f"🐍 Using system Python: {python_cmd}")
        print("⚠️  Warning: Virtual environment not found. Consider creating one for better isolation.")
    
    # Check if HTTP mode is requested
    http_mode = len(sys.argv) > 1 and sys.argv[1] == "--http"
    
    if http_mode:
        print("\n🌐 Starting MongoDB Vector RAG MCP Server in HTTP mode...")
        print("📍 Server will be available at: http://127.0.0.1:8000/sse")
        print("🔗 You can connect via HTTP clients or test with curl")
        print("\n" + "="*60)
        
        try:
            # Start the MCP server in HTTP mode
            subprocess.run([
                python_cmd, 
                str(main_py),
                "--http"
            ], cwd=str(mcp_server_dir), check=True)
        except KeyboardInterrupt:
            print("\n\n⏹️  Server stopped by user")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Server failed to start: {e}")
            print("\nTroubleshooting:")
            print("1. Check that your .env file is configured correctly")
            print("2. Verify MongoDB Atlas connection")
            print("3. Confirm OpenAI API key is set")
            print("4. Ensure all dependencies are installed")
            sys.exit(1)
    else:
        print("\n📋 MongoDB Vector RAG MCP Server Information")
        print("="*60)
        print("🎯 The MCP server runs automatically when you use the frontend!")
        print("")
        print("💡 To use the system:")
        print("   1. cd contract-analyzer-ui")
        print("   2. npm run dev")
        print("   3. Open http://localhost:3000")
        print("   4. Ask questions - the MCP server will start automatically")
        print("")
        print("🌐 To run the server in HTTP mode for testing:")
        print(f"   python {Path(__file__).name} --http")
        print("")
        print("🔧 To test the server manually:")
        print(f"   cd {mcp_server_dir.name} && python main.py")
        print("")
        print("Your frontend is now using the modern MCP STDIO architecture! 🚀")

if __name__ == "__main__":
    main() 