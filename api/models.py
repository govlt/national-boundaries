from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String, Double, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Counties(Base):
    __tablename__ = "counties"

    feature_id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    area_ha = Column(Double, nullable=False)
    geom = Column(
        Geometry(geometry_type="POLYGON", srid=3346, nullable=False), nullable=False
    )

    municipalities = relationship("Municipalities", back_populates="county")


class Municipalities(Base):
    __tablename__ = "municipalities"

    feature_id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    area_ha = Column(Double, nullable=False)
    county_code = Column(String, ForeignKey("counties.code"))
    county = relationship("Counties", back_populates="municipalities")

    elderships = relationship("Elderships", back_populates="municipality")
    residential_areas = relationship("ResidentialAreas", back_populates="municipality")

    geom = Column(
        Geometry(geometry_type="POLYGON", srid=3346, nullable=False), nullable=False
    )


class Elderships(Base):
    __tablename__ = "elderships"

    feature_id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    area_ha = Column(Double, nullable=False)
    municipality_code = Column(String, ForeignKey("municipalities.code"))
    municipality = relationship("Municipalities", back_populates="elderships")

    geom = Column(
        Geometry(geometry_type="POLYGON", srid=3346, nullable=False), nullable=False
    )


class ResidentialAreas(Base):
    __tablename__ = "residential_areas"

    feature_id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    area_ha = Column(Double, nullable=False)
    municipality_code = Column(String, ForeignKey("municipalities.code"))
    municipality = relationship("Municipalities", back_populates="residential_areas")

    geom = Column(
        Geometry(geometry_type="POLYGON", srid=3346, nullable=False), nullable=False
    )
