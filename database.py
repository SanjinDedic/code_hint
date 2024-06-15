from sqlmodel import create_engine, SQLModel, Session
from models import CodeSnippet, CodeHint


DATABASE_URL = "sqlite:///./code_hints.db"
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def save_code_snippet_and_hints(code: str, hints: dict):
    with Session(engine) as session:
        code_snippet = CodeSnippet(code=code)
        session.add(code_snippet)
        session.commit()
        session.refresh(code_snippet)

        code_hint = CodeHint(
            code_snippet_id=code_snippet.id,
            small_hint=hints["small_hint"],
            big_hint=hints["big_hint"],
            content_warning=hints["content_warning"],
            logical_error=hints["logical_error"],
            logical_error_hint=hints["logical_error_hint"]
        )
        session.add(code_hint)
        session.commit()