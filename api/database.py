import geoalchemy2
import sqlean
from geoalchemy2 import load_spatialite
from geoalchemy2.functions import GenericFunction
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session


def _connect():
    sqlean.extensions.enable("unicode")
    conn = sqlean.connect("file:boundaries.sqlite?immutable=1", uri=True)
    load_spatialite(conn)
    return conn


engine = create_engine("sqlite://", creator=_connect, echo=True, echo_pool=True)
session = sessionmaker(engine)
Base = declarative_base()


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
    inherit_cache = True


class GeomFromEWKB(GenericFunction):
    """
    Returns geometric object given its EWKB Representation

    see https://www.gaia-gis.it/gaia-sins/spatialite-sql-5.1.0.html

    Return type: :class:`geoalchemy2.types.Geometry`.
    """

    type = geoalchemy2.types.Geometry()
    inherit_cache = True
