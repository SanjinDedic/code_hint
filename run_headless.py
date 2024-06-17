import requests
from fastapi.testclient import TestClient
from api import app

from database import create_db_and_tables

create_db_and_tables()

client = TestClient(app)

# Code snippets to be analyzed
code_snippets = {
    1: """
# This snippet takes a name as input and checks its case (uppercase, lowercase, or mixed case),
# and prints the corresponding message.
name = input('Enter your name: ') 
if name.isupper():
  print('Your name is in uppercase.')
elif name.lower():
  print('Your name is in lowercase.')
else:
  print('Your name is in mixed case.')
""",
    2: """
# This snippet defines a recursive function to calculate the factorial of a given number.
def factorial(n):
    if n == 1:
        return 1
    else:
        return n * factorial(n)
""",
    3: """
# This snippet defines a function to check if a given string is a palindrome.
# It compares the string with its reverse and returns True if they are equal.
def is_palindrome(s):
    return s == s[::-1]

print(is_palindrome("racecar"))
print(is_palindrome("hello"))
""",
    4: """
# This snippet defines a function to find the maximum sum of a subarray within a given array.
# It uses Kadane's algorithm to efficiently solve the problem.
def find_max_subarray_sum(arr):
    max_sum = float('-inf')
    current_sum = 0

    for num in arr:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)

    return max_sum

arr = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
print(find_max_subarray_sum(arr))
""",
    5: """
# This snippet defines a function to check if a given string of parentheses is valid.
# It uses a stack to keep track of opening parentheses and checks if they match the closing parentheses.
def is_valid_parentheses(s):
    stack = []
    mapping = {")": "(", "]": "[", "}": "{"}

    for char in s:
        if char in mapping:
            if not stack or stack.pop() != mapping[char]:
                return False
        else:
            stack.append(char)

    return not stack

print(is_valid_parentheses("()[]{}"))
print(is_valid_parentheses("([)]"))
print(is_valid_parentheses("{[]}"))
"""
}

choice = int(input("Enter the number of the code snippet you want to analyze (1-3 easy, 4-5 rare and hard): "))

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