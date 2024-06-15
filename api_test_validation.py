from fastapi.testclient import TestClient
import pytest
from api import app  # Replace with the actual import of your FastAPI app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_py_1(client):
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




def test_valid_code_1(client):
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

def test_valid_code_2(client):
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

def test_invalid_code_1(client):
    invalid_code = """
for i in range(5)
    print(i)
"""
    response = client.post("/get_code_hints", json={"code": invalid_code})
    assert response.status_code == 200
    data = response.json()
    assert data['runtime_error_free'] is False
    assert isinstance(data['runtime_error_line'], int)
    assert data['runtime_error_line'] > 0  # Assuming the error line is identified correctly

def test_invalid_code_2(client):
    invalid_code = """
def my_function()
    return "Hello, world!"
"""
    response = client.post("/get_code_hints", json={"code": invalid_code})
    assert response.status_code == 200
    data = response.json()
    assert data['runtime_error_free'] is False
    assert isinstance(data['runtime_error_line'], int)
    assert data['runtime_error_line'] > 0  # Assuming the error line is identified correctly
