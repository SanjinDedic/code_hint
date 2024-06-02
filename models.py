from pydantic import BaseModel, StrictStr, StrictInt, Field, validator, ValidationError, StrictBool
from typing import Optional

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
        if 'runtime_error_free' not in values:
            return
        runtime_error_free = values['runtime_error_free']
        if runtime_error_free and er_line is not None:
            raise ValueError("CONTRADICTION runtime_error_line must be None if runtime_error_free is True")
        if not runtime_error_free and (er_line is None or er_line < 1):
            raise ValueError("runtime_error_line must be an integer > 0 if runtime_error_free is False")
        return er_line
    
    @validator('runtime_error_free')
    def validate_error_free(cls, error_free, values):
        print("values", values, "we are looking for is_python")
        if len(values) == 0:
            return
        is_python = values['is_python']
        if not is_python and error_free:
            raise ValueError("CONTRADICTION runtime_error_free must be False if is_python is False")
        return error_free

    @validator('logical_error_hint')
    def validate_logical_error_hint(cls, logical_error_hint, values):
        if len(values) == 0 or 'logical_error' not in values:
            return
        logical_error = values['logical_error']
        if logical_error and logical_error_hint == "":
            raise ValueError("logical_error_hint must not be empty if logical_error is True")
        return logical_error_hint

class CodeRequest(BaseModel):
    code: str