"""
database.py
------------
This module is the ONLY place the rest of the app talks to for data.

Right now every function returns sample data (see sample_data.py).
Later, swap the body of each function to run a real MySQL query using
`mysql-connector-python` or `SQLAlchemy` - the function names and
return shapes (list of dicts) are already designed to match what a
`cursor.fetchall()` call would give you, so the UI pages will not need
any changes.

Example of how a real connection would look once MySQL is ready:

    import mysql.connector
    from config import DB_CONFIG

    def get_connection():
        return mysql.connector.connect(**DB_CONFIG)

    def get_violations(n=60):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM violations ORDER BY datetime DESC LIMIT %s", (n,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
"""

import sample_data


def get_connection_status():
    """Placeholder for a real MySQL ping/health-check."""
    # In production: try connecting with mysql.connector and catch errors.
    return {"connected": True, "engine": "MySQL 8.0 (sample mode)", "last_sync": "just now"}


def get_cameras():
    return sample_data.get_cameras()


def get_violations(n=60):
    return sample_data.get_violations(n=n)


def get_dashboard_metrics(violations=None):
    violations = violations if violations is not None else get_violations()
    return sample_data.get_dashboard_metrics(violations)


def get_weekly_violation_trend():
    return sample_data.get_weekly_violation_trend()


def get_reports_table(days=7):
    return sample_data.get_reports_table(days=days)
