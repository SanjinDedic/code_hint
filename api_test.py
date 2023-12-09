import requests
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

# The code snippet to be analyzed
code_snippet = """
name = input('Enter your name: ') 
if name.isupper():
  print('Your name is in uppercase.')
elif name.lower():
  print('Your name is in lowercase.')
else:
  print('Your name is in mixed case.')
"""

data = {
  "code": code_snippet
}

response = client.post("/get_code_hints", json=data)

print(response.json())
