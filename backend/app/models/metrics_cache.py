from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, UniqueConstraint, func
from app.database import Base

class MetricsCache(Base):
    __tablename__ = "metrics_cache"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(128), index=True, nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_data = Column(JSON, nullable=True)  # For complex metrics (like distributions/lists)
    period_start = Column(DateTime, index=True, nullable=False)
    period_end = Column(DateTime, nullable=False)
    computed_at = Column(DateTime, default=func.now(), onupdate=func.now())
    confidence = Column(Float, default=1.0)

    __table_args__ = (
        UniqueConstraint("metric_name", "period_start", name="uix_metric_name_period_start"),
    )
