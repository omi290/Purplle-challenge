from pydantic import BaseModel
from typing import List

class FunnelStage(BaseModel):
    name: str
    count: int
    percentage: float
    drop_off: float = 0.0

class FunnelResponse(BaseModel):
    stages: List[FunnelStage]
    overall_conversion: float
    confidence: float
