from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class TrackingStatus(Base):
    __tablename__ = 'tracking_statuses'

    id = Column(Integer, primary_key=True)
    tracking_id = Column(String, unique=True, nullable=False)
    status = Column(Enum('Processed', 'Shipped', 'Out for Delivery', 'Delivered'), nullable=False)
    hub = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<TrackingStatus(tracking_id={self.tracking_id}, status={self.status}, hub={self.hub}, timestamp={self.timestamp})>"
