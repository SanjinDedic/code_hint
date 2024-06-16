from xml.dom import ValidationErr
from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from models import CodeHint, CodeSnippet
from database import create_db_and_tables, get_session, save_code_snippet_and_hints
from utils import is_this_python
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

from database import save_code_snippet_and_hints

@app.post("/get_code_hints")
async def get_code_hints(code_request: CodeSnippet, session: Session = Depends(get_session)):
    code_snippet = code_request.code
    attempt = 1
    if not is_this_python(code_snippet):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The code provided is not valid Python code")

    while attempt <= 3:
        openai_response = get_code_hints_from_openai(code_snippet, attempt)
        messages = openai_response.get("choices", [])
        
        json_reply = next((msg for msg in messages if msg.get("message", {}).get("role") == "assistant"), None)
        if json_reply and json_reply.get("message", {}).get("content"):
            try:
                hint_data = json.loads(json_reply["message"]["content"])
                hint_data["is_python"] = is_this_python(code_snippet)

                save_code_snippet_and_hints(session, code_snippet, hint_data)
                return hint_data
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