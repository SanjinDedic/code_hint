from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from models import CodeHintResponse, CodeRequest
from utils import is_this_python
import json
import uvicorn
import requests
import os

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
    is_python = is_this_python(code_snippet)
    attempt = 1
    while attempt <= 3:
        openai_response = get_code_hints_from_openai(code_snippet, attempt)
        messages = openai_response.get("choices", [])
        
        json_reply = next((msg for msg in messages if msg.get("message", {}).get("role") == "assistant"), None)
        if json_reply and json_reply.get("message", {}).get("content"):
            try:
                # Try to parse the response into CodeHintResponse
                # include the is_python value in the data
                data_to_send =  json.loads(json_reply["message"]["content"])
                data_to_send["is_python"] = is_python
                hint_response = CodeHintResponse.model_validate(data_to_send)
                # If parsing is successful, return the response
                return hint_response.model_dump()
            except Exception as e:
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