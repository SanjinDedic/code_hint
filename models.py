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
    is_python: bool = Field(False, description="True if the input is Python code")
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