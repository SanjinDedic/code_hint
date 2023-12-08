from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, StrictStr, StrictInt, Field, field_validator, ValidationError, StrictBool
from pydantic_core.core_schema import FieldValidationInfo
from typing import Optional
import uvicorn
import requests
from dotenv import load_dotenv
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
#test2 = CodeHintResponse(error_free=True, error_line=5, small_hint="", big_hint="")
class CodeHintResponse(BaseModel):
    error_free: StrictBool
    error_line: Optional[int] = Field(None, ge=1, description="The line number of the first error")
    small_hint: StrictStr = Field("", max_length=50, description="A small hint")
    big_hint: StrictStr = Field("", max_length=200, description="A big hint")

    @field_validator('error_line')
    def validate_error_line(cls, er_line, info: FieldValidationInfo):
        if len(info.data) == 0:
            return
        #view the information contained FieldValidationInfo
        print("info.data", info.data)
        error_free = info.data['error_free']
        if error_free and er_line != None:
            raise ValueError("CONTRADICTION error_line must be None if error_free is True")
        if error_free == False and (er_line == None or er_line < 1):
            raise ValueError("error_line must be an integer > 0 if error_free is False")
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
        "max_tokens": 64,
        "messages": [
            {
                "role": "system",
                "content": "You are an assistant. Your task is to analyze Python code and provide a JSON response with the following structure: {\"error_free\": BOOLEAN, \"error_line\": INT (None if error_free is true), \"small_hint\": STR (maximum of 8 words), \"big_hint\": STR (up to 30 words)}. You should not make up any additional values or provide any information not requested."
            },
            {
                "role": "user",
                "content": f"Analyze this Python code:\n{code}\nWill this code run without errors? If not, on which line is the first error? Provide a small hint and a big hint."
            }
        ],
        "response_format": {
            "type": "json_object"
        }
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    print(response.json())
    return response.json()

def process_code_snippet(code_snippet: str):
    openai_response = get_code_hints_from_openai(code_snippet)
    messages = openai_response.get("choices", [])
    
    # Find the assistant's reply message containing the JSON object
    json_reply = next((msg for msg in messages if msg.get("message", {}).get("role") == "assistant"), None)
    # Extract the JSON content from the reply
    if json_reply and json_reply.get("message", {}).get("content"):
        json_content = json.loads(json_reply["message"]["content"])
        error_free = json_content.get("error_free", False)
        error_line = json_content.get("error_line", None)
        small_hint = json_content.get("small_hint", "")
        big_hint = json_content.get("big_hint", "")
        print("error_free", error_free, type(error_free))
        print("error_line", error_line, type(error_line))
        print("small_hint", small_hint , type(small_hint))
        print("big_hint", big_hint , type(big_hint))
        print('----------------------------------')

    else:
        # Fallback values if the parsing fails
        error_free = True
        error_line = None
        small_hint = "Could not get hint"
        big_hint = "Could not get hint"

    if error_free:
        error_line = None
        small_hint = ""
        big_hint = ""

    hint_response = CodeHintResponse(
        error_free=error_free,
        error_line=error_line,
        small_hint=small_hint,
        big_hint=big_hint
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