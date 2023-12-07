from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from pydantic import validator, Field
import requests
from dotenv import load_dotenv
import os
import json

app = FastAPI()
load_dotenv()  # Load the .env file

class CodeHintResponse(BaseModel):
    error_free: bool
    error_line: int = Field(default=None, alias='error_line')
    small_hint: str
    big_hint: str

    @validator('error_line', pre=True, always=True)
    def validate_error_line(cls, v, values, **kwargs):
        if values.get('error_free') is True and v is not None:
            raise ValueError("error_line must be None if error_free is True")
        if values.get('error_free') is False and (v is None or v <= 0):
            raise ValueError("error_line must be an integer > 0 if error_free is False")
        return v
    
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
                "content": "You are an assistant. Your task is to analyze Python code and provide a JSON response with the following structure: {\"error_free\": BOOLEAN, \"error_line\": INT or None, \"small_hint\": STR (maximum of 8 words), \"big_hint\": STR (up to 30 words)}. You should not make up any additional values or provide any information not requested."
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
    else:
        # Fallback values if the parsing fails
        error_free = True
        error_line = None
        small_hint = "Could not get hint"
        big_hint = "Could not get hint"

    hint_response = CodeHintResponse(
        error_free=error_free,
        error_line=error_line,
        small_hint=small_hint,
        big_hint=big_hint
    )

    # Return the JSON representation
    return hint_response.json(by_alias=True)

@app.get("/")
async def root():
    return {"message": "Hello World I am the code hint api"}


@app.post("/get_code_hints")
async def get_code_hints(code_request: CodeRequest):
    try:
        return process_code_snippet(code_request.code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)