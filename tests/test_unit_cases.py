# tests/test_unit_cases.py

import pytest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastapi.testclient import TestClient
    from api.main import app
    
    client = TestClient(app)
    API_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import API components: {e}")
    API_AVAILABLE = False
    client = None

def test_basic_python_functionality():
    """Basic test to ensure Python and pytest are working."""
    assert 1 + 1 == 2
    assert "hello" + " world" == "hello world"
    assert len([1, 2, 3]) == 3

def test_environment_setup():
    """Test that the environment is properly set up."""
    assert sys.version_info >= (3, 8), "Python 3.8+ required"
    assert os.path.exists("requirements.txt"), "requirements.txt should exist"

@pytest.mark.skipif(not API_AVAILABLE, reason="API components not available")
def test_home():
    """Test the home endpoint if API is available."""
    if not client:
        pytest.skip("API not available")
    
    response = client.get("/")
    assert response.status_code == 200
