from db.models.mixins import LocationIDMixin, DataRequestIDMixin
from db.models.templates.standard import StandardBase
from middleware.enums import Relations


class LinkLocationDataRequest(StandardBase, LocationIDMixin, DataRequestIDMixin):
    __tablename__ = Relations.LINK_LOCATIONS_DATA_REQUESTS.value
