"""
sample_data.py
--------------
Generates realistic sample/demo data for the prototype.

IMPORTANT FOR FUTURE INTEGRATION:
Every function here mirrors a future MySQL query (see database.py).
When the real database is ready, only database.py needs to change -
these functions can simply be deleted, and the UI code will not need
any changes because it always calls database.py, not this file directly.
"""

import random
from datetime import datetime, timedelta

random.seed(42)  # keeps demo data consistent across reruns

CAMERAS = [
    {
        "id": "CAM-01",
        "name": "Camera 01",
        "location": "Main Road",
        "status": "Online",
        "fps": 30,
        "resolution": "1920x1080",
        "last_activity": "2 sec ago",
        "source": "rtsp://192.168.1.10:554/stream1",
        "camera_type": "IP Camera",
    },
    {
        "id": "CAM-02",
        "name": "Camera 02",
        "location": "Parking Area",
        "status": "Online",
        "fps": 28,
        "resolution": "1920x1080",
        "last_activity": "1 sec ago",
        "source": "rtsp://192.168.1.11:554/stream1",
        "camera_type": "IP Camera",
    },
    {
        "id": "CAM-03",
        "name": "Camera 03",
        "location": "College Gate",
        "status": "Online",
        "fps": 30,
        "resolution": "1280x720",
        "last_activity": "3 sec ago",
        "source": "rtsp://192.168.1.12:554/stream1",
        "camera_type": "IP Camera",
    },
    {
        "id": "CAM-04",
        "name": "Camera 04",
        "location": "Market Road",
        "status": "Offline",
        "fps": 0,
        "resolution": "Unknown",
        "last_activity": "42 min ago",
        "source": "rtsp://192.168.1.13:554/stream1",
        "camera_type": "IP Camera",
    },
]

VIOLATION_TYPES = [
    "Illegal Parking",
    "No Parking Zone",
    "Restricted Zone",
    "Long Duration Parking",
]

LOCATIONS = ["Main Road", "Parking Area", "College Gate", "Market Road"]

STATUSES = ["Pending", "Confirmed", "Dismissed"]

STATE_CODES = ["UP70", "DL8C", "MH12", "UP32", "RJ14", "GJ05"]


def _random_plate():
    code = random.choice(STATE_CODES)
    letters = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ", k=2))
    digits = random.randint(1000, 9999)
    return f"{code} {letters} {digits}"


def get_cameras():
    """Returns list of camera dictionaries (future: SELECT * FROM cameras)."""
    return CAMERAS


def get_violations(n=60):
    """Returns a list of sample violation records."""
    violations = []
    now = datetime.now()
    for i in range(n):
        dt = now - timedelta(hours=random.randint(0, 24 * 10), minutes=random.randint(0, 59))
        violations.append(
            {
                "id": f"VLN-{1000 + i}",
                "vehicle_number": _random_plate(),
                "violation_type": random.choice(VIOLATION_TYPES),
                "location": random.choice(LOCATIONS),
                "camera": random.choice(CAMERAS)["name"],
                "date": dt.strftime("%Y-%m-%d"),
                "time": dt.strftime("%H:%M:%S"),
                "datetime": dt,
                "confidence": round(random.uniform(0.78, 0.99), 2),
                "plate_confidence": round(random.uniform(0.70, 0.98), 2),
                "status": random.choices(STATUSES, weights=[0.3, 0.5, 0.2])[0],
            }
        )
    violations.sort(key=lambda v: v["datetime"], reverse=True)
    return violations


def get_dashboard_metrics(violations):
    """Aggregates a few headline metrics for the Dashboard page."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    total_vehicles_detected = 4820 + len(violations) * 3
    todays_violations = sum(1 for v in violations if v["date"] == today_str)
    active_cameras = sum(1 for c in CAMERAS if c["status"] == "Online")
    pending_reviews = sum(1 for v in violations if v["status"] == "Pending")
    return {
        "total_vehicles_detected": total_vehicles_detected,
        "todays_violations": todays_violations,
        "active_cameras": active_cameras,
        "total_cameras": len(CAMERAS),
        "pending_reviews": pending_reviews,
    }


def get_weekly_violation_trend():
    """Returns violation counts per violation type for the last 7 days."""
    days = [(datetime.now() - timedelta(days=i)).strftime("%a %d") for i in range(6, -1, -1)]
    data = {"day": days}
    for vt in VIOLATION_TYPES:
        data[vt] = [random.randint(1, 14) for _ in days]
    return data


def get_reports_table(days=7):
    """Returns a per-day summary table used in Reports & Analytics."""
    rows = []
    for i in range(days - 1, -1, -1):
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        total_vehicles = random.randint(400, 900)
        violations = random.randint(10, 45)
        confirmed = int(violations * random.uniform(0.5, 0.8))
        dismissed = violations - confirmed
        rows.append(
            {
                "Date": d,
                "Total Vehicles": total_vehicles,
                "Violations": violations,
                "Confirmed": confirmed,
                "Dismissed": dismissed,
            }
        )
    return rows
