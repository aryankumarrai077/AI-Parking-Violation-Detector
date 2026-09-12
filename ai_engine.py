"""
ai_engine.py
------------
This module isolates all AI/computer-vision logic from the Streamlit UI.

For this prototype, functions return realistic dummy detections so the
dashboard can be demonstrated end-to-end. When the real models are
ready, replace the body of each function - the UI code in
modules/live_monitoring.py does not need to change because it only
calls these functions.

Planned real implementation:
    - detect_vehicles(frame): run a YOLOv8 model (ultralytics) on the
      frame and return bounding boxes + class + confidence.
    - read_number_plate(cropped_plate_image): run OCR (EasyOCR /
      Tesseract) on the cropped plate region.
    - is_inside_restricted_zone(bbox, zone_polygon): use OpenCV
      point-in-polygon check (cv2.pointPolygonTest).
"""

import random

VEHICLE_CLASSES = ["Car", "Motorcycle", "Truck", "Bus", "Auto-rickshaw"]


def detect_vehicles(frame=None):
    """
    Placeholder for YOLO vehicle detection.
    Returns a list of dummy detections: bbox, class, confidence.
    """
    detections = []
    for _ in range(random.randint(2, 5)):
        detections.append(
            {
                "bbox": (
                    random.randint(20, 300),
                    random.randint(20, 200),
                    random.randint(320, 600),
                    random.randint(220, 400),
                ),
                "class": random.choice(VEHICLE_CLASSES),
                "confidence": round(random.uniform(0.80, 0.99), 2),
                "in_restricted_zone": random.random() < 0.3,
            }
        )
    return detections


def read_number_plate(cropped_plate_image=None):
    """Placeholder for OCR number plate recognition."""
    return {"plate_text": "UP70 AB 1234", "confidence": round(random.uniform(0.75, 0.97), 2)}


def check_zone_violation(detection):
    """Placeholder logic for restricted-zone violation checking."""
    return detection.get("in_restricted_zone", False)


def get_engine_status():
    """Returns current status of each AI module (for status widgets)."""
    return {
        "YOLO Vehicle Detection": "Active",
        "Parking Zone Detection": "Active",
        "Number Plate OCR": "Active",
        "OpenCV Processing": "Active",
        "Database": "Connected",
    }
