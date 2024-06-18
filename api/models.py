from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String, Double, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class BaseBoundaries(Base):
    __abstract__ = True

    feature_id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    area_ha = Column(Double, nullable=False)
    geom = Column(
        Geometry(geometry_type="POLYGON", srid=3346, nullable=False), nullable=False
    )


class Counties(BaseBoundaries):
    __tablename__ = "counties"

    municipalities = relationship("Municipalities", back_populates="county")


class Municipalities(BaseBoundaries):
    __tablename__ = "municipalities"

    county_code = Column(String, ForeignKey("counties.code"))
    county = relationship("Counties", back_populates="municipalities")

    elderships = relationship("Elderships", back_populates="municipality")
    residential_areas = relationship("ResidentialAreas", back_populates="municipality")


class Elderships(BaseBoundaries):
    __tablename__ = "elderships"

    municipality_code = Column(String, ForeignKey("municipalities.code"))
    municipality = relationship("Municipalities", back_populates="elderships")


class ResidentialAreas(BaseBoundaries):
    __tablename__ = "residential_areas"

    municipality_code = Column(String, ForeignKey("municipalities.code"))
    municipality = relationship("Municipalities", back_populates="residential_areas")
