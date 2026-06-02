from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

class EventBase(BaseModel):
    event_type: str = Field(..., description="ENTRY, EXIT, ZONE_ENTER, ZONE_EXIT, ZONE_DWELL, BILLING_QUEUE_JOIN, BILLING_QUEUE_ABANDON, REENTRY")
    track_id: str
    zone_name: Optional[str] = None
    timestamp: datetime
    confidence: float = 1.0
    bbox_x: Optional[float] = None
    bbox_y: Optional[float] = None
    bbox_w: Optional[float] = None
    bbox_h: Optional[float] = None
    frame_number: Optional[int] = None
    metadata_json: Optional[Dict[str, Any]] = None

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int

    class Config:
        from_attributes = True

class EventIngest(BaseModel):
    events: List[EventCreate]
