from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AnomalyBase(BaseModel):
    anomaly_type: str
    severity: str
    description: str
    suggested_action: Optional[str] = None
    detected_at: datetime
    confidence: float
    metric_value: Optional[float] = None
    threshold_value: Optional[float] = None
    zone_name: Optional[str] = None
    resolved: bool = False

class AnomalyResponse(AnomalyBase):
    id: int

    class Config:
        from_attributes = True
