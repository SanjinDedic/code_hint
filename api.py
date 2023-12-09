from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, StrictStr, StrictInt, Field, field_validator, ValidationError, StrictBool
from pydantic_core.core_schema import FieldValidationInfo
from typing import Optional
from dotenv import load_dotenv
import uvicorn
import requests
import re
import keyword
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

def is_python_code(s):
    # List of Python keywords
    python_keywords = set(keyword.kwlist)
    # List of Python operators
    python_operators = {"+", "-", "*", "/", "//", "%", "**", "=", "==", "!=", ">", "<", ">=", "<=","[", "]", "{", "}", ":",
                        "and", "or", "not", "is", "is not", "in", "not in", "&", "|", "^", "~", ")", "("}
    # Tokenize the input string
    words = re.findall(r"\b\w+\b", s)
    # Count the number of keywords and operators
    count = sum(word in python_keywords or word in python_operators for word in words)
    # Check if count is more than 15% of the total words
    return count >= len(words) * 0.15


class CodeHintResponse(BaseModel):
    is_python: StrictBool = Field(False, description="True if the input is Python code")
    runtime_error_free: StrictBool
    runtime_error_line: Optional[int] = Field(None, ge=1, description="The line number of the first error")
    small_hint: StrictStr = Field("", max_length=50, description="A small hint")
    big_hint: StrictStr = Field("", max_length=200, description="A big hint")
    content_warning: StrictBool = Field(False, description="True if inappropriate or abusive language is detected")
    logical_error: StrictBool = Field(False, description="True if the code runs but fails to achieve its intended purpose")
    logical_error_hint: StrictStr = Field("", max_length=200, description="Explanation of the logical error, if any")

    @field_validator('runtime_error_line')
    def validate_runtime_error_line(cls, er_line, info: FieldValidationInfo):
        if len(info.data) == 0:
            return
        #view the information contained FieldValidationInfo
        print("info.data", info.data)
        runtime_error_free = info.data['runtime_error_free']
        if runtime_error_free and er_line != None:
            raise ValueError("CONTRADICTION runtime_error_line must be None if runtime_error_free is True")
        if runtime_error_free == False and (er_line == None or er_line < 1):
            raise ValueError("runtime_error_line must be an integer > 0 if runtime_error_free is False")
        return er_line
    
    
class CodeRequest(BaseModel):
    code: str

def get_code_hints_from_openai(code: str):
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4-1106-preview",
        "temperature": 0,
        "max_tokens": 150,  # Increased to accommodate additional information
        "messages": [
            {
                "role": "system",
                "content": "You are an assistant. Your task is to analyze Python code and provide a JSON response with the following structure: {\"runtime_error_free\": BOOLEAN (True if the code has no errors at runtime), \"runtime_error_line\": INT (None if runtime_error_free is true), \"small_hint\": STR (puts the student on the right path to fixing the runtime error, maximum of 8 words), \"big_hint\": STR (provides all the information needed to fix the runtime error, up to 30 words), \"content_warning\": BOOLEAN, \"logical_error\": BOOLEAN, \"logical_error_hint\": STR (up to 200 characters)}. You should not make up any additional values or provide any information not requested."
            },
            {
                "role": "user",
                "content": f"Analyze this Python code:\n{code}\nWill this code run without errors? If not, on which line is the first error? Provide a small hint, a big hint, information about content warning, logical error, and a logical error hint."
            }
        ],
        "response_format": {
            "type": "json_object"
        }
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    print("response.json()", response.json())
    return response.json()

def process_code_snippet(code_snippet: str):
    openai_response = get_code_hints_from_openai(code_snippet)
    messages = openai_response.get("choices", [])
    
    # Find the assistant's reply message containing the JSON object
    json_reply = next((msg for msg in messages if msg.get("message", {}).get("role") == "assistant"), None)
    # Extract the JSON content from the reply
    if json_reply and json_reply.get("message", {}).get("content"):
        json_content = json.loads(json_reply["message"]["content"])
        is_python = is_python_code(code_snippet)
        runtime_error_free = json_content.get("runtime_error_free", False)
        runtime_error_line = json_content.get("runtime_error_line", None)
        small_hint = json_content.get("small_hint", "")
        big_hint = json_content.get("big_hint", "")
        content_warning = json_content.get("content_warning", False)
        logical_error = json_content.get("logical_error", False)
        logical_error_hint = json_content.get("logical_error_hint", "")
        print("runtime_error_free", runtime_error_free, type(runtime_error_free))
        print("runtime_error_line", runtime_error_line, type(runtime_error_line))
        print("small_hint", small_hint , type(small_hint))
        print("big_hint", big_hint , type(big_hint))
        print("content_warning", content_warning , type(content_warning))
        print("logical_error", logical_error , type(logical_error))
        print("logical_error_hint", logical_error_hint , type(logical_error_hint))
        print('----------------------------------')

    else:
        # Fallback values if the parsing fails
        is_python = False
        runtime_error_free = True
        runtime_error_line = None
        small_hint = "Could not get hint"
        big_hint = "Could not get hint"
        content_warning = False
        logical_error = False
        logical_error_hint = ""

    if runtime_error_free:
        runtime_error_line = None
        small_hint = ""
        big_hint = ""
    
    if logical_error == False:
        logical_error_hint = ""

    hint_response = CodeHintResponse(
        is_python=is_python,
        runtime_error_free=runtime_error_free,
        runtime_error_line=runtime_error_line,
        small_hint=small_hint,
        big_hint=big_hint,
        content_warning=content_warning,
        logical_error=logical_error,
        logical_error_hint=logical_error_hint
    )
    print("after hint_response")
    # Return the JSON representation using model dump
    return hint_response.model_dump()

@app.get("/")
async def root():
    return {"message": "Hello World I am the code hint api"}


@app.post("/get_code_hints")
async def get_code_hints(code_request: CodeRequest):
    return process_code_snippet(code_request.code)

    
# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)