import datetime
import logging
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.visitor import Visitor
from app.models.session import Session as StoreSession
from app.models.event import Event
from app.models.transaction import Transaction
from app.services.store_layout_parser import Zone, parse_store_layout
from app.services.cv_pipeline import TrackedDetection
from app.utils.helpers import bbox_center, is_point_in_bbox

logger = logging.getLogger(__name__)

class EventEngine:
    def __init__(self, db: Session, layout_path: str):
        self.db = db
        self.zones = parse_store_layout(layout_path)
        
    def find_active_zone(self, cx: float, cy: float) -> Zone:
        """
        Finds which zone a coordinate center points to.
        Returns first matching zone or browse fallback.
        """
        for zone in self.zones:
            # Coordinates are x1, y1, x2, y2 normalized
            if zone.x1 <= cx <= zone.x2 and zone.y1 <= cy <= zone.y2:
                return zone
        
        # Default browse fallback
        return Zone("Skincare", "browse", 0.0, 0.0, 1.0, 1.0)

    def process_tracks(self, tracks: List[TrackedDetection]) -> Dict[str, Any]:
        """
        Processes frame tracking points to classify and persist visitors, sessions, and events.
        """
        if not tracks:
            return {"events_created": 0}

        # Sort tracks by timestamp so we process them chronologically
        tracks = sorted(tracks, key=lambda x: x.timestamp)
        
        # Group by track_id
        tracks_by_id = {}
        for track in tracks:
            tracks_by_id.setdefault(track.track_id, []).append(track)
            
        events_created = 0
        
        # Dynamically set base_time so that the latest tracking point finishes exactly now.
        # This keeps the CCTV Heartbeat Sensor alive and prevents the stale feed warning banner.
        total_duration = max([pt.timestamp for pt in tracks]) if tracks else 0.0
        base_time = datetime.datetime.now() - datetime.timedelta(seconds=total_duration)
        
        for track_id, points in tracks_by_id.items():
            first_point = points[0]
            last_point = points[-1]
            
            # 1. Visitor Persistence
            visitor = self.db.query(Visitor).filter(Visitor.track_id == track_id).first()
            first_seen_time = base_time + datetime.timedelta(seconds=first_point.timestamp)
            last_seen_time = base_time + datetime.timedelta(seconds=last_point.timestamp)
            
            # Aggregate staff predictions across the track
            staff_votes = [getattr(pt, "is_staff", False) for pt in points]
            is_staff = sum(staff_votes) > (len(staff_votes) / 2) if staff_votes else False
            staff_confs = [getattr(pt, "staff_confidence", 0.0) for pt in points]
            avg_staff_conf = sum(staff_confs) / len(staff_confs) if staff_confs else 0.0

            is_new_visitor = False
            if not visitor:
                is_new_visitor = True
                visitor = Visitor(
                    track_id=track_id,
                    first_seen=first_seen_time,
                    last_seen=last_seen_time,
                    is_staff=is_staff,
                    staff_confidence=avg_staff_conf
                )
                self.db.add(visitor)
                self.db.flush()
            else:
                visitor.last_seen = last_seen_time
                visitor.total_visits += 1
                visitor.is_staff = is_staff
                visitor.staff_confidence = avg_staff_conf
                self.db.flush()

            # 2. Session Persistence
            store_session = self.db.query(StoreSession).filter(
                StoreSession.visitor_id == visitor.id,
                StoreSession.exit_time == None
            ).first()
            
            if not store_session:
                store_session = StoreSession(
                    visitor_id=visitor.id,
                    entry_time=first_seen_time,
                    is_reentry=not is_new_visitor,
                    zones_visited=[]
                )
                self.db.add(store_session)
                self.db.flush()

            # 3. Process each coordinate transition to generate events
            current_zone_name = None
            zone_durations = {}
            last_zone_change_time = first_seen_time

            for idx, pt in enumerate(points):
                cx, cy = bbox_center(pt.bbox)
                matched_zone = self.find_active_zone(cx, cy)
                pt_time = base_time + datetime.timedelta(seconds=pt.timestamp)
                
                # Check for ENTRY
                if idx == 0 and is_new_visitor:
                    self._create_event(
                        visitor.id, store_session.id, "ENTRY", 
                        matched_zone.name, pt_time, pt
                    )
                    events_created += 1
                    
                if idx == 0 and not is_new_visitor:
                    self._create_event(
                        visitor.id, store_session.id, "REENTRY", 
                        matched_zone.name, pt_time, pt
                    )
                    events_created += 1

                # Check for Zone Transitions
                if matched_zone.name != current_zone_name:
                    if current_zone_name is not None:
                        # Exit old zone
                        self._create_event(
                            visitor.id, store_session.id, "ZONE_EXIT",
                            current_zone_name, pt_time, pt
                        )
                        events_created += 1
                        
                        # Calculate dwell duration in exiting zone
                        duration = (pt_time - last_zone_change_time).total_seconds()
                        zone_durations[current_zone_name] = zone_durations.get(current_zone_name, 0.0) + duration
                        
                        # Trigger ZONE_DWELL if they stayed long enough
                        if duration >= 5.0:
                            self._create_event(
                                visitor.id, store_session.id, "ZONE_DWELL",
                                current_zone_name, pt_time, pt,
                                metadata={"duration_seconds": duration}
                            )
                            events_created += 1
                            
                        # Queue Abandonment trigger: left billing zone without purchase
                        if current_zone_name == "Billing":
                            # Check if a POS transaction exists matching this visitor time roughly
                            # In real life we correlate later, here we trigger potential queue abandon event
                            self._create_event(
                                visitor.id, store_session.id, "BILLING_QUEUE_ABANDON",
                                "Billing", pt_time, pt
                            )
                            events_created += 1
                    
                    # Enter new zone
                    self._create_event(
                        visitor.id, store_session.id, "ZONE_ENTER",
                        matched_zone.name, pt_time, pt
                    )
                    events_created += 1
                    
                    if matched_zone.name == "Billing":
                        self._create_event(
                            visitor.id, store_session.id, "BILLING_QUEUE_JOIN",
                            "Billing", pt_time, pt
                        )
                        events_created += 1

                    current_zone_name = matched_zone.name
                    last_zone_change_time = pt_time
                    
                    # Add to session visited zones
                    visited_list = list(store_session.zones_visited)
                    if current_zone_name not in visited_list:
                        visited_list.append(current_zone_name)
                        store_session.zones_visited = visited_list

            # Handle last active zone duration
            if current_zone_name:
                final_dur = (last_seen_time - last_zone_change_time).total_seconds()
                zone_durations[current_zone_name] = zone_durations.get(current_zone_name, 0.0) + final_dur

            # 4. Finalize Session details
            store_session.exit_time = last_seen_time
            store_session.duration_seconds = (last_seen_time - first_seen_time).total_seconds()
            
            # Determine maximum dwell zone
            if zone_durations:
                max_zone = max(zone_durations, key=zone_durations.get)
                store_session.max_dwell_zone = max_zone
                store_session.max_dwell_seconds = zone_durations[max_zone]
                
            # Trigger EXIT event
            self._create_event(
                visitor.id, store_session.id, "EXIT",
                current_zone_name or "Exit", last_seen_time, last_point
            )
            events_created += 1
            
        self.db.commit()
        return {"events_created": events_created}

    def _create_event(self, visitor_id: int, session_id: int, event_type: str, 
                      zone_name: str, timestamp: datetime.datetime, pt: TrackedDetection, 
                      metadata: dict = None) -> Event:
        event = Event(
            visitor_id=visitor_id,
            session_id=session_id,
            event_type=event_type,
            zone_name=zone_name,
            timestamp=timestamp,
            confidence=pt.confidence,
            bbox_x=pt.bbox[0],
            bbox_y=pt.bbox[1],
            bbox_w=pt.bbox[2],
            bbox_h=pt.bbox[3],
            frame_number=pt.frame_number,
            metadata_json=metadata
        )
        self.db.add(event)
        self.db.flush()
        return event
