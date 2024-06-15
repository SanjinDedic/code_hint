import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
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

@patch("api.get_code_hints_from_openai")
def test_get_code_hints(mock_get_code_hints_from_openai, test_code_snippet):
    mock_response = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": '{"runtime_error_free": true, "runtime_error_line": null, "small_hint": "test small hint", "big_hint": "test big hint", "content_warning": false, "logical_error": false, "logical_error_hint": ""}'
                }
            }
        ]
    }
    mock_get_code_hints_from_openai.return_value = mock_response

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

@patch("api.is_this_python")
def test_get_code_hints_invalid_code(mock_is_this_python):
    mock_is_this_python.return_value = False
    invalid_code_snippet = {"code": """invalid code here? $$"""}
    response = client.post("/get_code_hints", json=invalid_code_snippet)
    assert response.status_code == 400
    assert response.json() == {"detail": "The code provided is not valid Python code"}

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World I am the code hint api"}