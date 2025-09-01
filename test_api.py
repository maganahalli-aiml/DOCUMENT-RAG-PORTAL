from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import subprocess
import signal
import os
import time
import threading
import requests
import sys

app = FastAPI()

def kill_process_on_port(port):
    """Kill any process running on the specified port."""
    try:
        # Find processes using the specified port
        result = subprocess.run(
            ["lsof", "-t", f"-i:{port}"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"🔄 Found {len(pids)} process(es) on port {port}, terminating...")
            
            for pid in pids:
                try:
                    pid = int(pid.strip())
                    # Skip our own process
                    if pid == os.getpid():
                        continue
                    print(f"   Killing process {pid}")
                    os.kill(pid, signal.SIGTERM)
                except (ValueError, OSError) as e:
                    print(f"   Warning: Could not kill process {pid}: {e}")
            
            # Wait a moment for processes to terminate gracefully
            time.sleep(1)
            
            # Check if any processes are still running and force kill if necessary
            result = subprocess.run(
                ["lsof", "-t", f"-i:{port}"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        pid = int(pid.strip())
                        if pid != os.getpid():
                            os.kill(pid, signal.SIGKILL)
                    except (ValueError, OSError):
                        pass
                        
            print(f"✅ Port {port} is now available")
        else:
            print(f"✅ Port {port} is already available")
            
    except Exception as e:
        print(f"⚠️  Warning: Could not check/clear port {port}: {e}")
        print("   Proceeding with test anyway...")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "document-portal-test",
        "version": "1.0.0"
    }

@app.post("/chat/index")
async def upload_document(files: UploadFile = File(...)):
    return {
        "status": "success",
        "session_id": f"session_{files.filename}",
        "message": "File uploaded successfully"
    }

def run_api_tests():
    """Run basic API tests and return success/failure."""
    base_url = "http://127.0.0.1:8081"
    
    # Wait for server to start
    print("⏳ Waiting for API server to start...")
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API server is responding")
                break
        except requests.RequestException:
            if i == max_retries - 1:
                print("❌ API server failed to start")
                return False
            time.sleep(1)
    
    # Test health endpoint
    try:
        print("🧪 Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "document-portal-test"
        print("✅ Health endpoint test passed")
        
        # Test upload endpoint (basic structure test)
        print("🧪 Testing upload endpoint structure...")
        # We can't easily test file upload without files, but we can test the endpoint exists
        response = requests.post(f"{base_url}/chat/index", timeout=5)
        # Expecting 422 (validation error) since we didn't send a file, but endpoint exists
        assert response.status_code == 422
        print("✅ Upload endpoint structure test passed")
        
        print("🎉 All API tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    # Kill any existing processes on port 8081 before starting
    kill_process_on_port(8081)
    
    print("🚀 Starting test API server on port 8081...")
    
    # Start server in a separate thread
    server_thread = threading.Thread(
        target=lambda: uvicorn.run(app, host="127.0.0.1", port=8081, log_level="warning"),
        daemon=True
    )
    server_thread.start()
    
    # Run tests
    test_success = run_api_tests()
    
    # The server thread will be automatically terminated when main thread exits
    print("🧹 Test completed, cleaning up...")
    
    # Exit with appropriate code
    sys.exit(0 if test_success else 1)
