import sqlite3

from geoalchemy2 import load_spatialite
from sqlalchemy import create_engine
from sqlalchemy.event import listen
from sqlalchemy.orm import declarative_base, sessionmaker, Session


def _connect():
    return sqlite3.connect("file:boundaries.sqlite?immutable=1", uri=True)


engine = create_engine("sqlite://", creator=_connect, echo=True, echo_pool=True)
session = sessionmaker(engine)
Base = declarative_base()

listen(engine, "connect", load_spatialite)


def get_db() -> Session:
    db = session()
    try:
        yield db
    finally:
        db.close()
