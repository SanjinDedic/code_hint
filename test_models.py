# test_models.py
from sqlmodel import SQLModel, create_engine
from sqlalchemy.orm import sessionmaker
from models import CodeSnippet, CodeHint
from pydantic import ValidationError

# Set up the test database
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def setup_function():
    # Clear the test database before each test
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

def test_create_code_snippet():
    session = Session()
    code = "print('Hello, World!')"
    snippet = CodeSnippet(code=code)
    session.add(snippet)
    session.commit()
    retrieved_snippet = session.query(CodeSnippet).first()
    assert retrieved_snippet.code == code
    session.close()

def test_code_snippet_validation():
    code = "invalid code"
    snippet = CodeSnippet(code=code)
    try:
        CodeSnippet.model_validate(snippet)
    except ValueError as e:
        assert str(e) == "The provided code is not valid Python"

def test_create_code_hint():
    session = Session()
    code = "print('Hello, World!')"
    snippet = CodeSnippet(code=code)
    session.add(snippet)
    session.commit()
    hint = CodeHint(
        is_python=True,
        code_snippet_id=snippet.id,
        small_hint="A small hint",
        big_hint="A big hint",
        content_warning=False,
        logical_error=False,
        logical_error_hint="",
        runtime_error_free=True,
        runtime_error_line=None,
        attempt=1
    )
    session.add(hint)
    session.commit()
    retrieved_hint = session.query(CodeHint).first()
    assert retrieved_hint.is_python == True
    assert retrieved_hint.code_snippet_id == snippet.id
    session.close()

def test_code_hint_validation():
    hint = CodeHint(
        is_python=True,
        code_snippet_id=1,
        small_hint="A small hint",
        big_hint="A big hint",
        content_warning=False,
        logical_error=True,
        logical_error_hint="Logical error hint",
        runtime_error_free=True,
        runtime_error_line=None,
        attempt=1
    )
    CodeHint.model_validate(hint)

    hint.logical_error = False
    hint.runtime_error_free = False
    hint.big_hint = "A big hint"
    try:
        CodeHint.model_validate(hint)
    except ValueError as e:
        assert "big_hint must be empty if runtime_error_free is True" in str(e)

    hint.runtime_error_free = False
    hint.runtime_error_line = 0
    try:
        CodeHint.model_validate(hint)
    except ValidationError as e:
        assert "Input should be greater than or equal to 1" in str(e)