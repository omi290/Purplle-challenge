import os
import openpyxl
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class Zone:
    def __init__(self, name: str, zone_type: str, x1: float, y1: float, x2: float, y2: float):
        self.name = name
        self.zone_type = zone_type  # entrance, exit, browse, billing
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone_name": self.name,
            "zone_type": self.zone_type,
            "coordinates": {
                "x1": self.x1,
                "y1": self.y1,
                "x2": self.x2,
                "y2": self.y2
            }
        }

def get_default_zones() -> List[Zone]:
    """
    Returns standard retail store layout zones.
    All coordinates normalized to 0.0 - 1.0 (relative to video resolution).
    """
    return [
        Zone("Entrance", "entrance", 0.0, 0.0, 0.3, 0.3),
        Zone("Exit", "exit", 0.7, 0.0, 1.0, 0.3),
        Zone("Skincare", "browse", 0.0, 0.3, 0.5, 0.7),
        Zone("Makeup", "browse", 0.5, 0.3, 1.0, 0.7),
        Zone("Fragrance & Hair", "browse", 0.0, 0.7, 0.5, 1.0),
        Zone("Billing", "billing", 0.5, 0.7, 1.0, 1.0)
    ]

def parse_store_layout(file_path: str) -> List[Zone]:
    """
    Parse zones from XLSX file.
    If layout parser fails, returns fallback default retail zones.
    """
    if not os.path.exists(file_path):
        logger.warning(f"Store layout file {file_path} not found. Using default layout.")
        return get_default_zones()

    try:
        wb = openpyxl.load_workbook(file_path, read_only=True)
        sheet = wb.active
        zones = []
        
        # Read layout columns. Layout sheet expected structure:
        # A: Zone Name, B: Zone Type, C: X1, D: Y1, E: X2, F: Y2
        # Let's read starting from row 2
        for row in sheet.iter_rows(min_row=2, max_col=6, values_only=True):
            if not row or not row[0]:
                continue
            name = str(row[0])
            z_type = str(row[1]) if row[1] else "browse"
            
            # Convert coordinate percentages
            try:
                x1 = float(row[2]) if row[2] is not None else 0.0
                y1 = float(row[3]) if row[3] is not None else 0.0
                x2 = float(row[4]) if row[4] is not None else 1.0
                y2 = float(row[5]) if row[5] is not None else 1.0
                
                # Make sure coordinates are normalized
                if x1 > 1.0 or y1 > 1.0 or x2 > 1.0 or y2 > 1.0:
                    x1, y1, x2, y2 = x1/100, y1/100, x2/100, y2/100
                
                zones.append(Zone(name, z_type, x1, y1, x2, y2))
            except Exception as e:
                logger.error(f"Error parsing zone layout row {row}: {e}")
                continue
                
        if not zones:
            logger.warning("No valid zones parsed from sheet. Using defaults.")
            return get_default_zones()
            
        logger.info(f"Successfully parsed {len(zones)} zones from {file_path}")
        return zones
        
    except Exception as e:
        logger.error(f"Failed to parse store layout from Excel: {e}. Using defaults.")
        return get_default_zones()
