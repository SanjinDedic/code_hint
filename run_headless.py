import requests
from fastapi.testclient import TestClient
from api import app

from database import create_db_and_tables

create_db_and_tables()

client = TestClient(app)

# Code snippets to be analyzed
code_snippets = {
    1: """
name = input('Enter your name: ') 
if name.isupper():
  print('Your name is in uppercase.')
elif name.lower():
  print('Your name is in lowercase.')
else:
  print('Your name is in mixed case.')
""",
    2: """
def factorial(n):
    if n == 1:
        return 1
    else:
        return n * factorial(n)
""",
    3: """
def is_palindrome(s):
    return s == s[::-1]

print(is_palindrome("racecar"))
print(is_palindrome("hello"))
"""
}

choice = int(input("Enter the number of the code snippet you want to analyze: "))

if choice not in code_snippets:
    print("Invalid choice. Exiting...")
    exit()

code_snippet = code_snippets[choice]

data = {
    "code": code_snippet
}
response = client.post("/get_code_hints", json=data)

result = response.json()

print("\nCode Snippet:")
print("=" * 20)
print(code_snippet)
print("=" * 20)

print("\nAnalysis Results:")
print("=" * 20)
print(f"Small Hint: {result['small_hint']}")
print(f"Big Hint: {result['big_hint']}")
print(f"Logical Error Hint: {result['logical_error_hint']}")
print("=" * 20)

print(f"| Content Warning: {result['content_warning']}, | Logical Error: {result['logical_error']}, | Runtime Error Free: {result['runtime_error_free']}, | Is Python: {result['is_python']} |")