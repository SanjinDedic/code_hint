from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from pydantic import validator, StrictBool
from utils import is_this_python

class CodeSnippet(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(min_length=10, max_length=80*50, description="The code snippet to be analyzed")
    hints: Optional["CodeHint"] = Relationship(back_populates="code_snippet")

'''Currently handled manually in the API code
    @validator('code')
    def validate_code(cls, code):
        if not is_this_python(code):
            raise ValueError("The provided code is not valid Python")
        return code
'''

class CodeHint(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    is_python: StrictBool = Field(False, description="True if the input is Python code")
    code_snippet_id: int = Field(foreign_key="codesnippet.id")
    code_snippet: Optional[CodeSnippet] = Relationship(back_populates="hints")
    small_hint: str = Field(max_length=50, description="A small hint")
    big_hint: str = Field(max_length=200, description="A big hint")
    content_warning: StrictBool = Field(default=False, description="True if inappropriate or abusive language is detected")
    logical_error: StrictBool = Field(default=False, description="True if the code runs but fails to achieve its intended purpose")
    logical_error_hint: str = Field(max_length=200, description="Explanation of the logical error, if any")
    runtime_error_free: StrictBool = Field(default=True, description="True if the code runs without any runtime errors")
    runtime_error_line: Optional[int] = Field(None, ge=1, description="The line number of the first error")

    @validator('logical_error_hint')
    def validate_logical_error_hint(cls, logical_error_hint, values):
        logical_error = values.get('logical_error')
        if logical_error and not logical_error_hint:
            raise ValueError("logical_error_hint must not be empty if logical_error is True")
        return logical_error_hint
    
    @validator('big_hint')
    def validate_big_hint(cls, big_hint, values):
        runtime_error_free = values.get('runtime_error_free')
        runtime_error_line = values.get('runtime_error_line')
        if runtime_error_free and not runtime_error_line:
            if big_hint:
                raise ValueError("big_hint must be empty if runtime_error_free is True")
        return big_hint
'''
    @validator('runtime_error_line')
    def validate_runtime_error_line(cls, runtime_error_line, values):
        runtime_error_free = values.get('runtime_error_free')
        if not runtime_error_free:
            #if runtime error line must be an integer or numeric string greater than or equal to 1
            if not isinstance(runtime_error_line, int) or runtime_error_line < 1:
                raise ValueError("runtime_error_line must be an integer greater than or equal to 1")
'''