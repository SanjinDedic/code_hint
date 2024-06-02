from pydantic import BaseModel, StrictStr, StrictInt, Field, validator, ValidationError, StrictBool
from typing import Optional
from utils import is_this_python

class CodeHintResponse(BaseModel):
    is_python: StrictBool = Field(False, description="True if the input is Python code")
    runtime_error_free: StrictBool
    runtime_error_line: Optional[int] = Field(None, ge=1, description="The line number of the first error")
    small_hint: StrictStr = Field("", max_length=50, description="A small hint")
    big_hint: StrictStr = Field("", max_length=200, description="A big hint")
    content_warning: StrictBool = Field(False, description="True if inappropriate or abusive language is detected")
    logical_error: StrictBool = Field(False, description="True if the code runs but fails to achieve its intended purpose")
    logical_error_hint: StrictStr = Field("", max_length=200, description="Explanation of the logical error, if any")

    @validator('runtime_error_line')
    def validate_runtime_error_line(cls, er_line, values):
        runtime_error_free = values.get('runtime_error_free')
        if runtime_error_free and er_line is not None:
            raise ValueError("runtime_error_line must be None if runtime_error_free is True")
        if not runtime_error_free and (er_line is None or er_line < 1):
            raise ValueError("runtime_error_line must be an integer > 0 if runtime_error_free is False")
        return er_line
    
    @validator('logical_error_hint')
    def validate_logical_error_hint(cls, logical_error_hint, values):
        logical_error = values.get('logical_error')
        if logical_error and not logical_error_hint:
            raise ValueError("logical_error_hint must not be empty if logical_error is True")
        return logical_error_hint

class CodeRequestModel(BaseModel):
    code: str = Field(..., min_length=10, max_length=80*500, description="The code snippet to be analyzed")

    @validator('code')
    def validate_code(cls, code):
        if not is_this_python(code):
            raise ValueError("The provided code is not valid Python")
        return code