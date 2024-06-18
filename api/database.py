import sqlite3

import geoalchemy2
from geoalchemy2 import load_spatialite
from geoalchemy2.functions import GenericFunction
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


class GeomFromGeoJSON(GenericFunction):
    """
    Returns the GeoJSON [Geographic JavaScript Object Notation] representation

    see https://www.gaia-gis.it/gaia-sins/spatialite-sql-5.1.0.html

    Return type: :class:`geoalchemy2.types.Geometry`.
    """

    type = geoalchemy2.types.Geometry()


class GeomFromEWKB(GenericFunction):
    """
    Returns geometric object given its EWKB Representation

    see https://www.gaia-gis.it/gaia-sins/spatialite-sql-5.1.0.html

    Return type: :class:`geoalchemy2.types.Geometry`.
    """

    type = geoalchemy2.types.Geometry()
