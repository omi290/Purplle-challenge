from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    visitor_id = Column(Integer, ForeignKey("visitors.id", ondelete="CASCADE"), nullable=True, index=True)
    event_type = Column(String(32), nullable=False, index=True)  # ENTRY, EXIT, ZONE_ENTER, ZONE_EXIT, ZONE_DWELL, BILLING_QUEUE_JOIN, BILLING_QUEUE_ABANDON, REENTRY
    zone_name = Column(String(128), index=True, nullable=True)
    timestamp = Column(DateTime, index=True, nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)
    bbox_x = Column(Float, nullable=True)
    bbox_y = Column(Float, nullable=True)
    bbox_w = Column(Float, nullable=True)
    bbox_h = Column(Float, nullable=True)
    frame_number = Column(Integer, nullable=True)
    metadata_json = Column(JSON, nullable=True)

    visitor = relationship("Visitor", back_populates="events")
    session = relationship("Session", back_populates="events")

    @property
    def confidence_score(self) -> float:
        return self.confidence

    @property
    def confidence_level(self) -> str:
        if self.confidence < 0.65:
            return "LOW"
        elif self.confidence < 0.85:
            return "MEDIUM"
        else:
            return "HIGH"

