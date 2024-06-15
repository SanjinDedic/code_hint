# Project Sitemap

## /Users/sanjindedic/Library/CloudStorage/GoogleDrive-ozrobotix@gmail.com/My Drive/PROJECTS/x/code_hint

[api.py](/Users/sanjindedic/Library/CloudStorage/GoogleDrive-ozrobotix@gmail.com/My Drive/PROJECTS/x/code_hint/api.py)
### /Users/sanjindedic/Library/CloudStorage/GoogleDrive-ozrobotix@gmail.com/My Drive/PROJECTS/x/code_hint/api.py
```
from xml.dom import ValidationErr
from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from models import CodeHint, CodeSnippet
from database import create_db_and_tables, get_session
import json
import uvicorn
import requests
import os
from sqlmodel import Session

app = FastAPI()
load_dotenv()  # Load the .env file

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def get_code_hints_from_openai(code: str, attempt=1):
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Adjust temperature based on the attempt
    temperature = 0 if attempt == 1 else 0.8

    data = {
        "model": "gpt-4o",
        "temperature": temperature,
        "max_tokens": 150,
        "messages": [
            {
                "role": "system",
                "content": "You are an assistant. Your task is to analyze Python code and provide a JSON response with the following structure: {\"runtime_error_free\": BOOLEAN (True if the code has no errors at runtime), \"runtime_error_line\": INT (None if runtime_error_free is true), \"small_hint\": STR (puts the student on the right path to fixing the runtime error, maximum of 8 words), \"big_hint\": STR (provides all the information needed to fix the runtime error, up to 30 words), \"content_warning\": BOOLEAN, \"logical_error\": BOOLEAN, \"logical_error_hint\": STR (up to 200 characters)}. You should not make up any additional values or provide any information not requested."
            },
            {
                "role": "user",
                "content": f"Analyze this Python code:\n{code}\n Identify any runtime errors and logical errors (any errors that mean the code does not fulfill its purpose) and provide a JSON response with the following structure: {{\"runtime_error_free\": BOOLEAN (True if the code has no errors at runtime), \"runtime_error_line\": INT (None if runtime_error_free is true), \"small_hint\": STR (puts the student on the right path to fixing the runtime error, maximum of 8 words), \"big_hint\": STR (provides all the information needed to fix the runtime error, up to 30 words), \"content_warning\": BOOLEAN, \"logical_error\": BOOLEAN, \"logical_error_hint\": STR (up to 200 characters)}}"
            }
        ],
        "response_format": {
            "type": "json_object"
        }
    }

    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    return response.json()

@app.get("/")
async def root():
    return {"message": "Hello World I am the code hint api"}

@app.post("/get_code_hints")
async def get_code_hints(code_request: CodeSnippet, session: Session = Depends(get_session)):
    code_snippet = code_request.code
    attempt = 1
    while attempt <= 3:
        openai_response = get_code_hints_from_openai(code_snippet, attempt)
        messages = openai_response.get("choices", [])
        
        json_reply = next((msg for msg in messages if msg.get("message", {}).get("role") == "assistant"), None)
        if json_reply and json_reply.get("message", {}).get("content"):
            try:
                data_to_send = json.loads(json_reply["message"]["content"])
                data_to_send["is_python"] = True

                code_snippet_instance = CodeSnippet(code=code_snippet)
                session.add(code_snippet_instance)
                session.commit()
                session.refresh(code_snippet_instance)

                code_hint_instance = CodeHint(
                    code_snippet_id=code_snippet_instance.id,
                    small_hint=data_to_send["small_hint"],
                    big_hint=data_to_send["big_hint"],
                    content_warning=data_to_send["content_warning"],
                    logical_error=data_to_send["logical_error"],
                    logical_error_hint=data_to_send["logical_error_hint"],
                    runtime_error_free=data_to_send["runtime_error_free"],
                    runtime_error_line=data_to_send["runtime_error_line"]
                )
                session.add(code_hint_instance)
                session.commit()
                session.refresh(code_hint_instance)
                return code_hint_instance
            except ValidationErr as e:
                print(f"Attempt {attempt}: ValidationError - {str(e)}")
                attempt += 1
        else:
            attempt += 1

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to get valid code hints after 3 attempts")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```
## /Users/sanjindedic/Library/CloudStorage/GoogleDrive-ozrobotix@gmail.com/My Drive/PROJECTS/x/code_hint

[models.py](/Users/sanjindedic/Library/CloudStorage/GoogleDrive-ozrobotix@gmail.com/My Drive/PROJECTS/x/code_hint/models.py)
### /Users/sanjindedic/Library/CloudStorage/GoogleDrive-ozrobotix@gmail.com/My Drive/PROJECTS/x/code_hint/models.py
```
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from pydantic import validator
from utils import is_this_python

class CodeSnippet(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(min_length=10, max_length=80*50, description="The code snippet to be analyzed")
    hints: Optional["CodeHint"] = Relationship(back_populates="code_snippet")

    @validator('code')
    def validate_code(cls, code):
        if not is_this_python(code):
            raise ValueError("The provided code is not valid Python")
        return code

class CodeHint(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code_snippet_id: int = Field(foreign_key="codesnippet.id")
    code_snippet: Optional[CodeSnippet] = Relationship(back_populates="hints")
    small_hint: str = Field(max_length=50, description="A small hint")
    big_hint: str = Field(max_length=200, description="A big hint")
    content_warning: bool = Field(default=False, description="True if inappropriate or abusive language is detected")
    logical_error: bool = Field(default=False, description="True if the code runs but fails to achieve its intended purpose")
    logical_error_hint: str = Field(max_length=200, description="Explanation of the logical error, if any")
    runtime_error_free: bool = Field(default=True, description="True if the code runs without any runtime errors")
    runtime_error_line: Optional[int] = Field(None, ge=1, description="The line number of the first error")

    @validator('logical_error_hint')
    def validate_logical_error_hint(cls, logical_error_hint, values):
        logical_error = values.get('logical_error')
        if logical_error and not logical_error_hint:
            raise ValueError("logical_error_hint must not be empty if logical_error is True")
        return logical_error_hint
```
## /Users/sanjindedic/Library/CloudStorage/GoogleDrive-ozrobotix@gmail.com/My Drive/PROJECTS/x/code_hint

[run_headless.py](/Users/sanjindedic/Library/CloudStorage/GoogleDrive-ozrobotix@gmail.com/My Drive/PROJECTS/x/code_hint/run_headless.py)
### /Users/sanjindedic/Library/CloudStorage/GoogleDrive-ozrobotix@gmail.com/My Drive/PROJECTS/x/code_hint/run_headless.py
```
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
```
## /Users/sanjindedic/Library/CloudStorage/GoogleDrive-ozrobotix@gmail.com/My Drive/PROJECTS/x/code_hint

[utils.py](/Users/sanjindedic/Library/CloudStorage/GoogleDrive-ozrobotix@gmail.com/My Drive/PROJECTS/x/code_hint/utils.py)
### /Users/sanjindedic/Library/CloudStorage/GoogleDrive-ozrobotix@gmail.com/My Drive/PROJECTS/x/code_hint/utils.py
```
import re
import keyword

def is_this_python(s):
    # Remove single-line comments
    s = re.sub(r"#.*", "", s)
    # Remove single and double-quoted strings
    s = re.sub(r'".*?"', '', s)
    s = re.sub(r"'.*?'", '', s)
    # Remove multi-line strings
    s = re.sub(r"'''(.*?)'''", '', s, flags=re.DOTALL)
    s = re.sub(r'"""(.*?)"""', '', s, flags=re.DOTALL)

    # List of Python keywords
    python_keywords = set(keyword.kwlist)
    # List of Python operators
    python_operators = {"+", "-", "*", "/", "//", "%", "**", "=", "==", "!=", ">", "<", ">=", "<=", "[", "]", "{", "}", ":",
                        "and", "or", "not", "is", "is not", "in", "not in", "&", "|", "^", "~", ")", "("}
    # Special case for single print statement
    if s.strip().startswith('print(') and s.strip().endswith(')'):
        return True
    # Tokenize the input string, including special characters
    words = re.findall(r"\b\w+\b|[+\-*/%=<>!&|^~()\[\]{}]", s)
    # Count the number of keywords and operators
    count = sum(word in python_keywords or word in python_operators for word in words)
    # Adjusting the threshold
    ratio = count / len(words) if words else 0
    return ratio > 0.3
```
## /Users/sanjindedic/Library/CloudStorage/GoogleDrive-ozrobotix@gmail.com/My Drive/PROJECTS/x/code_hint

[database.py](/Users/sanjindedic/Library/CloudStorage/GoogleDrive-ozrobotix@gmail.com/My Drive/PROJECTS/x/code_hint/database.py)
### /Users/sanjindedic/Library/CloudStorage/GoogleDrive-ozrobotix@gmail.com/My Drive/PROJECTS/x/code_hint/database.py
```
from sqlmodel import create_engine, SQLModel, Session
from models import CodeSnippet, CodeHint


DATABASE_URL = "sqlite:///./code_hints.db"
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def save_code_snippet_and_hints(code: str, hints: dict):
    with Session(engine) as session:
        code_snippet = CodeSnippet(code=code)
        session.add(code_snippet)
        session.commit()
        session.refresh(code_snippet)

        code_hint = CodeHint(
            code_snippet_id=code_snippet.id,
            small_hint=hints["small_hint"],
            big_hint=hints["big_hint"],
            content_warning=hints["content_warning"],
            logical_error=hints["logical_error"],
            logical_error_hint=hints["logical_error_hint"]
        )
        session.add(code_hint)
        session.commit()
```
