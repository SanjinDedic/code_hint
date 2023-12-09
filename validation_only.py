import pytest
from pydantic import ValidationError
from api2 import CodeHintResponse

def test_valid_inputs():
    """Test with all valid inputs."""
    CodeHintResponse(is_python=True, runtime_error_free=True, runtime_error_line=None, small_hint="", big_hint="")

def test_invalid_error_line_when_runtime_error_free():
    """Test with invalid error_line (should be None if runtime_error_free is True)."""
    with pytest.raises(ValidationError):
        CodeHintResponse(is_python=True, runtime_error_free=True, runtime_error_line=5, small_hint="", big_hint="")

def test_missing_error_line_when_runtime_error_not_free():
    """Test with invalid error_line (should not be None if runtime_error_free is False)."""
    with pytest.raises(ValidationError):
        CodeHintResponse(is_python=True, runtime_error_free=False, runtime_error_line=None, small_hint="", big_hint="")

def test_invalid_data_type_for_error_line():
    """Test with invalid data type for error_line."""
    with pytest.raises(ValidationError):
        CodeHintResponse(is_python=True, runtime_error_free=False, runtime_error_line="not an integer", small_hint="", big_hint="")

def test_missing_optional_fields():
    """Test with missing optional fields."""
    CodeHintResponse(is_python=True, runtime_error_free=True)

def test_field_length_constraints():
    """Test with field length constraints."""
    with pytest.raises(ValidationError):
        CodeHintResponse(is_python=True, runtime_error_free=True, runtime_error_line=None, small_hint="x" * 51, big_hint="x" * 201)

def test_invalid_type_for_runtime_error_free():
    """Test with invalid type for runtime_error_free."""
    with pytest.raises(ValidationError):
        CodeHintResponse(is_python=True, runtime_error_free="not a boolean", runtime_error_line=None, small_hint="", big_hint="")

def test_with_hints():
    """Test with hints."""
    CodeHintResponse(is_python=True, runtime_error_free=False, runtime_error_line=11, small_hint="small hint sdf ds f", big_hint="big hint f asdf asdfa s")

def test_inappropriate_content_warning():
    """Test 9: Inappropriate Content Warning Test"""
    CodeHintResponse(is_python=True, runtime_error_free=True, runtime_error_line=None, content_warning=True)

def test_logical_error_without_hint():
    """Test 10: Logical Error without Hint"""
    with pytest.raises(ValidationError):
        CodeHintResponse(is_python=True, runtime_error_free=True, runtime_error_line=None, logical_error=True, logical_error_hint="")

def test_logical_error_with_hint():
    """Test 11: Logical Error with Hint"""
    CodeHintResponse(is_python=True, runtime_error_free=True, runtime_error_line=None, logical_error=True, logical_error_hint="Explanation of logical error")


def test_non_python_code_without_runtime_error():
    """Test 12: Non-Python Code without Runtime Error"""
    with pytest.raises(ValidationError):
        CodeHintResponse(is_python=False, runtime_error_free=True, runtime_error_line=None)

def test_zero_as_runtime_error_line():
    """Test 13: Zero as Runtime Error Line"""
    with pytest.raises(ValidationError):
        CodeHintResponse(is_python=True, runtime_error_free=False, runtime_error_line=0)

def test_negative_number_as_runtime_error_line():
    """Test 14: Negative Number as Runtime Error Line"""
    with pytest.raises(ValidationError):
        CodeHintResponse(is_python=True, runtime_error_free=False, runtime_error_line=-1)

def test_logical_error_with_excessive_hint_length():
    """Test 16: Logical Error with Excessive Hint Length"""
    with pytest.raises(ValidationError):
        CodeHintResponse(is_python=True, runtime_error_free=True, runtime_error_line=None, logical_error=True, logical_error_hint="x" * 201)
