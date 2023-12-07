import requests

endpoint = "http://192.168.0.229:8000/get_code_hints"

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

response = requests.post(endpoint, json=data)

print(response.json())
