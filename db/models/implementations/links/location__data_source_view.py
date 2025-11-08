from sqlalchemy import Column, Integer

from db.models.base import Base
from middleware.enums import Relations


class LinkLocationDataSourceView(Base):
    __tablename__ = Relations.LINK_LOCATIONS_DATA_SOURCES_VIEW.value
    location_id = Column(Integer, primary_key=True)
    data_source_id = Column(Integer, primary_key=True)
