from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, func
from app.database import Base

class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    anomaly_type = Column(String(64), nullable=False, index=True)  # queue_spike, conversion_drop, unusual_dwell, low_footfall, high_abandonment, revenue_leakage
    severity = Column(String(16), nullable=False, default="medium")  # low, medium, high, critical
    description = Column(Text, nullable=False)
    suggested_action = Column(Text, nullable=True)
    detected_at = Column(DateTime, index=True, default=func.now())
    confidence = Column(Float, nullable=False, default=1.0)
    metric_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    zone_name = Column(String(128), index=True, nullable=True)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
