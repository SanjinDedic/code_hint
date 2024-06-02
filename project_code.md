# Project Sitemap

## /home/slowturing/Google Drive/PROJECTS/code_hint

[api.py](/home/slowturing/Google Drive/PROJECTS/code_hint/api.py)
### /home/slowturing/Google Drive/PROJECTS/code_hint/api.py
```
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, StrictStr, StrictInt, Field, field_validator, ValidationError, StrictBool
from pydantic_core.core_schema import ValidationInfo
from typing import Optional
from dotenv import load_dotenv
import utils
import uvicorn
import requests
import os
import json

app = FastAPI()
load_dotenv()  # Load the .env file

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class CodeHintResponse(BaseModel):
    is_python: StrictBool = Field(False, description="True if the input is Python code")
    runtime_error_free: StrictBool
    runtime_error_line: Optional[int] = Field(None, ge=1, description="The line number of the first error")
    small_hint: StrictStr = Field("", max_length=50, description="A small hint")
    big_hint: StrictStr = Field("", max_length=200, description="A big hint")
    content_warning: StrictBool = Field(False, description="True if inappropriate or abusive language is detected")
    logical_error: StrictBool = Field(False, description="True if the code runs but fails to achieve its intended purpose")
    logical_error_hint: StrictStr = Field("", max_length=200, description="Explanation of the logical error, if any")


    # @model_validator with mode ='before' and mode = 'after' is the new way to do this
    @field_validator('runtime_error_line')
    def validate_runtime_error_line(cls, er_line, info: ValidationInfo):
        if 'runtime_error_free' not in info.data:
            return
        #view the information contained FieldValidationInfo
        runtime_error_free = info.data['runtime_error_free']
        if runtime_error_free and er_line != None:
            raise ValueError("CONTRADICTION runtime_error_line must be None if runtime_error_free is True")
        if runtime_error_free == False and (er_line == None or er_line < 1):
            raise ValueError("runtime_error_line must be an integer > 0 if runtime_error_free is False")
        return er_line
    

    @field_validator('runtime_error_free')
    def validate_error_free(cls, error_free, info: ValidationInfo):
        print("info.data", info.data, "we are looking for is_python")
        if len(info.data) == 0:
            return
        is_python = info.data['is_python']
        if is_python == False and error_free == True:
            raise ValueError("CONTRADICTION runtime_error_free must be False if is_python is False")
        return error_free
    
    @field_validator('logical_error_hint')
    def validate_logical_error_hint(cls, logical_error_hint, info: ValidationInfo):
        if len(info.data) == 0 or 'logical_error' not in info.data:
            return
        logical_error = info.data['logical_error']
        if logical_error and logical_error_hint == "":
            raise ValueError("logical_error_hint must not be empty if logical_error is True")
        return logical_error_hint
    
class CodeRequest(BaseModel):
    code: str

def get_code_hints_from_openai(code: str, attempt=1):
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Adjust temperature based on the attempt
    temperature = 0 if attempt == 1 else 0.8

    data = {
        "model": "gpt-4-1106-preview",
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

def process_code_snippet(code_snippet: str):
    if len(code_snippet.split("\n")) > 80:
        return {"error": "Code snippet has more than 80 lines"}
    #make sure that length of the string is at least 10 characters
    if len(code_snippet) < 10:
        return {"error": "Code snippet is too short"}
    is_python = utils.is_python(code_snippet)
    attempt = 1
    while attempt <= 3:
        openai_response = get_code_hints_from_openai(code_snippet, attempt)
        messages = openai_response.get("choices", [])
        
        json_reply = next((msg for msg in messages if msg.get("message", {}).get("role") == "assistant"), None)
        if json_reply and json_reply.get("message", {}).get("content"):
            try:
                # Try to parse the response into CodeHintResponse
                # inclue the is_python value in the data
                data_to_send =  json.loads(json_reply["message"]["content"])
                data_to_send["is_python"] = is_python
                data_to_send = json.dumps(data_to_send)
                hint_response = CodeHintResponse.model_validate_json(data_to_send)
                # If parsing is successful, return the response
                return hint_response.model_dump()
            except ValidationError as e:
                # If parsing fails, print the error for logging and try again
                print(f"Attempt {attempt}: ValidationError - {str(e)}")
                attempt += 1
        else:
            # If no valid reply is found, try again
            attempt += 1

    # If all attempts fail, return an error message
    return {"error": "Unable to get valid code hints after 3 attempts"}

@app.get("/")
async def root():
    return {"message": "Hello World I am the code hint api"}


@app.post("/get_code_hints")
async def get_code_hints(code_request: CodeRequest):
    return process_code_snippet(code_request.code)

    
# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```
## /home/slowturing/Google Drive/PROJECTS/code_hint

[utils.py](/home/slowturing/Google Drive/PROJECTS/code_hint/utils.py)
### /home/slowturing/Google Drive/PROJECTS/code_hint/utils.py
```
import re
import keyword

def is_python(s):
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
## /home/slowturing/Google Drive/PROJECTS/code_hint

[run_headless.py](/home/slowturing/Google Drive/PROJECTS/code_hint/run_headless.py)
### /home/slowturing/Google Drive/PROJECTS/code_hint/run_headless.py
```
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

```
