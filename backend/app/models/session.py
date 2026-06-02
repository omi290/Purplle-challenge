from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    visitor_id = Column(Integer, ForeignKey("visitors.id", ondelete="CASCADE"), nullable=False, index=True)
    entry_time = Column(DateTime, index=True, nullable=False)
    exit_time = Column(DateTime, index=True, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    is_reentry = Column(Boolean, default=False)
    zones_visited = Column(JSON, default=list)  # List of zone names visited
    max_dwell_zone = Column(String(128), nullable=True)
    max_dwell_seconds = Column(Float, nullable=True)

    visitor = relationship("Visitor", back_populates="sessions")
    events = relationship("Event", back_populates="session", cascade="all, delete-orphan")
