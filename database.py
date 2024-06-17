from sqlmodel import create_engine, SQLModel, Session
from models import CodeSnippet, CodeHint
from pydantic import ValidationError


DATABASE_URL = "sqlite:///./code_hints.db"
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


def save_code_snippet_and_hints(session, code: str, code_hint: dict, attempt: int):
    code_snippet = CodeSnippet(code=code)
    session.add(code_snippet)
    session.commit()
    session.refresh(code_snippet)

    try:
        code_hint_instance = CodeHint(
            code_snippet_id=code_snippet.id,
            is_python=code_hint["is_python"],
            small_hint=code_hint["small_hint"],
            big_hint=code_hint["big_hint"],
            content_warning=code_hint["content_warning"],
            logical_error=code_hint["logical_error"],
            logical_error_hint=code_hint["logical_error_hint"],
            runtime_error_free=code_hint["runtime_error_free"],
            runtime_error_line=code_hint["runtime_error_line"],
            attempt=attempt
        )
        session.add(code_hint_instance)
        session.commit()
    except ValidationError as e:
        # Handle the validation error, e.g., log the error or return an error response
        print(f"Validation error occurred: {str(e)}")
        # You can also raise an exception or return an error response as needed
        raise