from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch
from api import app
from pydantic import ValidationError
from models import CodeHint

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@patch("api.get_code_hints_from_openai")
def test_py_1(mock_get_code_hints_from_openai, client):
    mock_get_code_hints_from_openai.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": '{"runtime_error_free": true, "runtime_error_line": null, "small_hint": "", "big_hint": "", "content_warning": false, "logical_error": false, "logical_error_hint": ""}'
                }
            }
        ]
    }
    valid_code = """
    def add_numbers(a, b):
        return a + b

    result = add_numbers(3, 4)
    print(result)
    """
    response = client.post("/get_code_hints", json={"code": valid_code})
    assert response.status_code == 200
    data = response.json()
    assert data['is_python'] is True

@patch("api.get_code_hints_from_openai")
def test_valid_code_1(mock_get_code_hints_from_openai, client):
    mock_get_code_hints_from_openai.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": '{"runtime_error_free": true, "runtime_error_line": null, "small_hint": "", "big_hint": "", "content_warning": false, "logical_error": false, "logical_error_hint": ""}'
                }
            }
        ]
    }
    valid_code = """
    def add_numbers(a, b):
        return a + b

    result = add_numbers(3, 4)
    print(result)
    """
    response = client.post("/get_code_hints", json={"code": valid_code})
    assert response.status_code == 200
    data = response.json()
    assert data['runtime_error_free'] is True
    assert data['runtime_error_line'] is None

@patch("api.get_code_hints_from_openai")
def test_valid_code_2(mock_get_code_hints_from_openai, client):
    mock_get_code_hints_from_openai.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": '{"runtime_error_free": true, "runtime_error_line": null, "small_hint": "", "big_hint": "", "content_warning": false, "logical_error": false, "logical_error_hint": ""}'
                }
            }
        ]
    }
    valid_code = """
class MyClass:
    def __init__(self, name):
        self.name = name

obj = MyClass("Test")
print(obj.name)
"""
    response = client.post("/get_code_hints", json={"code": valid_code})
    assert response.status_code == 200
    data = response.json()
    assert data['runtime_error_free'] is True
    assert data['runtime_error_line'] is None

@patch("api.get_code_hints_from_openai")
def test_invalid_code_1(mock_get_code_hints_from_openai, client):
    mock_get_code_hints_from_openai.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": '{"runtime_error_free": false, "runtime_error_line": 2, "small_hint": "Fix syntax error", "big_hint": "Add a colon after the for loop condition", "content_warning": false, "logical_error": false, "logical_error_hint": ""}'
                }
            }
        ]
    }
    invalid_code = """
for i in range(5)
    print(i)
"""
    response = client.post("/get_code_hints", json={"code": invalid_code})
    assert response.status_code == 200
    data = response.json()
    assert data['runtime_error_free'] is False
    assert isinstance(data['runtime_error_line'], int)
    assert data['runtime_error_line'] > 0

@patch("api.get_code_hints_from_openai")
def test_invalid_code_2(mock_get_code_hints_from_openai, client):
    mock_get_code_hints_from_openai.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": '{"runtime_error_free": false, "runtime_error_line": 1, "small_hint": "Fix syntax error", "big_hint": "Add parentheses after the function name", "content_warning": false, "logical_error": false, "logical_error_hint": ""}'
                }
            }
        ]
    }
    invalid_code = """
def my_function()
    return "Hello, world!"
"""
    response = client.post("/get_code_hints", json={"code": invalid_code})
    assert response.status_code == 200
    data = response.json()
    assert data['runtime_error_free'] is False
    assert isinstance(data['runtime_error_line'], int)
    assert data['runtime_error_line'] > 0