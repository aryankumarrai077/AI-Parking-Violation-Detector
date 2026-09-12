"""
modules/live_monitoring.py
---------------------------
Simulated CCTV control-room view. Lets the user upload a demo video
(or in future connect a real webcam/RTSP feed via OpenCV), runs a
placeholder YOLO detection pass, and shows a violation-alert workflow.
"""

import random
import time
from datetime import datetime

import streamlit as st

import ai_engine
import database
from components import page_header, card_start, card_end, badge_html


def render():
    page_header(
        "Live Monitoring",
        "Real-time AI-powered parking violation detection",
    )

    # ---------------- TOP STATUS BAR ----------------
    status_cols = st.columns(6)
    items = [
        ("● LIVE", "red"),
        ("AI Engine: Active", "green"),
        ("YOLO: Running", "green"),
        ("OCR: Ready", "blue"),
        ("FPS: 28", "blue"),
        ("Avg Confidence: 94%", "green"),
    ]
    for col, (text, color) in zip(status_cols, items):
        with col:
            st.markdown(badge_html(text, color), unsafe_allow_html=True)

    st.write("")

    # ---------------- CAMERA SELECTOR ----------------
    cameras = database.get_cameras()
    camera_names = [f'{c["name"]} - {c["location"]}' for c in cameras]
    selected_camera = st.selectbox("Select Camera", camera_names)
    cam_info = cameras[camera_names.index(selected_camera)]

    main_col, side_col = st.columns([2.2, 1])

    with main_col:
        card_start("Live Camera Feed")

        video_file = st.file_uploader(
            "Upload a demo video for this camera (prototype input)", type=["mp4", "avi", "mov"]
        )
        use_webcam = st.checkbox("Or connect webcam via OpenCV (future integration)")

        if video_file is None and not use_webcam:
            st.info(
                "📡 No camera or video connected. Upload a demo video above, "
                "or enable webcam mode, to preview AI detection on this feed."
            )
            st.markdown(
                """
                <div style="background:#0e1117; border:1px dashed #2a313d; border-radius:10px;
                            height:280px; display:flex; align-items:center; justify-content:center;
                            color:#6b7280; font-size:14px;">
                    🎥 Camera feed preview will appear here
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            if video_file is not None:
                st.video(video_file)
            else:
                st.warning(
                    "Webcam integration point: connect `cv2.VideoCapture(0)` here in production. "
                    "Live OpenCV frames are not available in this hosted prototype."
                )

            st.markdown('<div class="section-title">AI Detection Preview</div>', unsafe_allow_html=True)
            detections = ai_engine.detect_vehicles()
            for d in detections:
                zone_color = "red" if d["in_restricted_zone"] else "green"
                zone_label = "RESTRICTED ZONE" if d["in_restricted_zone"] else "ALLOWED ZONE"
                st.markdown(
                    f'<div class="camera-card">'
                    f'<b>{d["class"]}</b> — confidence {d["confidence"]*100:.0f}% '
                    f'{badge_html(zone_label, zone_color)}</div>',
                    unsafe_allow_html=True,
                )
            st.caption("Bounding boxes / zone overlay will render on real video frames once OpenCV + YOLO are connected.")

        card_end()

        # ---------------- PARKING ZONE LEGEND ----------------
        card_start("Parking Zone Legend")
        z1, z2, z3 = st.columns(3)
        with z1:
            st.markdown(badge_html("Allowed Zone", "green"), unsafe_allow_html=True)
        with z2:
            st.markdown(badge_html("Restricted Zone", "red"), unsafe_allow_html=True)
        with z3:
            st.markdown(badge_html("Detected Vehicle", "blue"), unsafe_allow_html=True)
        card_end()

        # ---------------- VIOLATION ALERT ----------------
        if video_file is not None and any(d["in_restricted_zone"] for d in detections):
            v = random.choice(database.get_violations(5))
            st.markdown(
                f"""
                <div class="alert-critical">
                    <div class="alert-title">⚠ ILLEGAL PARKING DETECTED</div>
                    <div style="margin-top:8px; font-size:13px; color:#e6e9ef; line-height:1.9;">
                        <b>Vehicle Number:</b> {v['vehicle_number']}<br>
                        <b>Location:</b> {cam_info['location']}<br>
                        <b>Camera:</b> {cam_info['name']}<br>
                        <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                        <b>Violation Type:</b> {v['violation_type']}<br>
                        <b>Confidence:</b> {v['confidence']*100:.0f}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("📸 Evidence image will be auto-captured and stored once camera pipeline is live.")

        # ---------------- CONTROL BUTTONS ----------------
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            st.button("▶ Start Monitoring", use_container_width=True)
        with b2:
            st.button("⏹ Stop Monitoring", use_container_width=True)
        with b3:
            st.button("📸 Capture Evidence", use_container_width=True)
        with b4:
            st.button("⛶ Full Screen", use_container_width=True)

    with side_col:
        card_start("AI Detection Status")
        checks = ["Vehicle Detection", "Parking Zone Analysis", "Violation Detection", "Number Plate OCR", "Evidence Capture"]
        for c in checks:
            st.markdown(f'<div style="margin-bottom:6px;">✅ {c}</div>', unsafe_allow_html=True)
        card_end()

        card_start("Recent Live Alerts")
        for v in database.get_violations(5):
            st.markdown(
                f"""
                <div class="camera-card">
                    <div class="camera-meta">{v['time']}</div>
                    <div class="camera-name">{v['vehicle_number']}</div>
                    <div class="camera-meta">{v['location']} • {v['violation_type']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        card_end()

        card_start("Camera Information")
        st.markdown(
            f"""
            <div style="font-size:13px; line-height:2;">
            <b>Resolution:</b> {cam_info['resolution']}<br>
            <b>FPS:</b> {cam_info['fps']}<br>
            <b>Status:</b> {badge_html(cam_info['status'])}<br>
            <b>Last Frame:</b> {cam_info['last_activity']}<br>
            <b>Network:</b> {badge_html('Connected' if cam_info['status']=='Online' else 'Disconnected', 'green' if cam_info['status']=='Online' else 'red')}
            </div>
            """,
            unsafe_allow_html=True,
        )
        card_end()
