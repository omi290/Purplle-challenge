from typing import Tuple, Dict, Any, List

def calculate_iou(box1: Tuple[float, float, float, float], box2: Tuple[float, float, float, float]) -> float:
    """
    Calculate Intersection over Union (IoU) of two bounding boxes.
    Boxes are in format (x, y, w, h).
    """
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    
    # Convert to (xmin, ymin, xmax, ymax)
    b1_xmin, b1_ymin, b1_xmax, b1_ymax = x1, y1, x1 + w1, y1 + h1
    b2_xmin, b2_ymin, b2_xmax, b2_ymax = x2, y2, x2 + w2, y2 + h2
    
    # Intersection dimensions
    ixmin = max(b1_xmin, b2_xmin)
    iymin = max(b1_ymin, b2_ymin)
    ixmax = min(b1_xmax, b2_xmax)
    iymax = min(b1_ymax, b2_ymax)
    
    iw = max(0.0, ixmax - ixmin)
    ih = max(0.0, iymax - iymin)
    
    intersection = iw * ih
    
    # Union Area
    area1 = w1 * h1
    area2 = w2 * h2
    union = area1 + area2 - intersection
    
    if union <= 0.0:
        return 0.0
        
    return intersection / union

def is_point_in_bbox(x: float, y: float, bbox: Tuple[float, float, float, float]) -> bool:
    """
    Check if a point (x, y) is inside bounding box (bx, by, bw, bh).
    """
    bx, by, bw, bh = bbox
    return bx <= x <= (bx + bw) and by <= y <= (by + bh)

def bbox_center(bbox: Tuple[float, float, float, float]) -> Tuple[float, float]:
    """
    Get the center coordinates (x, y) of a bounding box (x, y, w, h).
    """
    x, y, w, h = bbox
    return x + w / 2.0, y + h / 2.0
