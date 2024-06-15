import pytest
from fastapi.testclient import TestClient
from api import app, get_session
from models import CodeSnippet, CodeHint

client = TestClient(app)

@pytest.fixture
def test_code_snippet():
    return {
        "code": """
def factorial(n):
    if n == 1:
        return 1
    else:
        return n * factorial(n-1)
"""
    }

def test_get_code_hints(test_code_snippet):
    response = client.post("/get_code_hints", json=test_code_snippet)
    assert response.status_code == 200
    data = response.json()
    assert "small_hint" in data
    assert "big_hint" in data
    assert "content_warning" in data
    assert "logical_error" in data
    assert "logical_error_hint" in data
    assert "runtime_error_free" in data
    assert "runtime_error_line" in data
    assert "is_python" in data

def test_get_code_hints_invalid_code():
    invalid_code_snippet = {"code": """invalid code here? $$"""}
    response = client.post("/get_code_hints", json=invalid_code_snippet)
    print(response.json())  
    assert response.status_code == 400
    assert response.json() == {"detail": "The code provided is not valid Python code"}


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World I am the code hint api"}