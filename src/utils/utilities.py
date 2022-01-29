import os

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session


def datetime_range(start, end, delta):
    current = start
    while current < end:
        yield current
        current += delta


def db_conn() -> Session:
    engine = create_engine(f"sqlite:///{os.getenv('SQLITE_URL')}")
    session = sessionmaker()
    session.configure(bind=engine)
    return session()
