from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, func
from sqlalchemy.orm import relationship
from app.database import Base

class Visitor(Base):
    __tablename__ = "visitors"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(String(64), unique=True, index=True, nullable=False)
    first_seen = Column(DateTime, index=True, default=func.now())
    last_seen = Column(DateTime, default=func.now())
    is_staff = Column(Boolean, default=False)
    staff_confidence = Column(Float, nullable=True)
    total_visits = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())

    sessions = relationship("Session", back_populates="visitor", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="visitor", cascade="all, delete-orphan")

    @property
    def confidence_score(self) -> float:
        return self.staff_confidence if self.staff_confidence is not None else 1.0

    @property
    def confidence_level(self) -> str:
        conf = self.staff_confidence if self.staff_confidence is not None else 1.0
        if conf < 0.65:
            return "LOW"
        elif conf < 0.85:
            return "MEDIUM"
        else:
            return "HIGH"

