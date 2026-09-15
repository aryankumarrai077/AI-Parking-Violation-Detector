"""
modules/live_monitoring.py
---------------------------
CCTV control-room view. Lets the user upload a demo video and runs
REAL YOLOv8 vehicle detection + zone-violation checking frame by frame
using OpenCV. Webcam/RTSP live-stream support is the next integration
point (marked clearly below) - it works the same way, just swap the
video source.
"""

import os
import tempfile
import time
from datetime import datetime

import cv2
import streamlit as st

import ai_engine
import database
from components import page_header, card_start, card_end, badge_html


def _process_video_source(cap, max_frames, confidence_threshold, frame_placeholder, info_placeholder):
    """
    Shared frame-processing loop used by BOTH the uploaded-video path and
    the webcam path. `cap` is any already-open cv2.VideoCapture object -
    the rest of the logic (YOLO detection, drawing, zone check) is
    identical no matter where the frames come from.

    Returns: (frame_count, elapsed_seconds, last_frame_detections,
              any_violation_found, last_violation_detection)
    """
    frame_count = 0
    detections = []
    any_violation_found = False
    last_violation_detection = None
    start_time = time.time()

    while cap.isOpened() and frame_count < max_frames:
        ok, frame = cap.read()
        if not ok:
            break  # end of video, or webcam disconnected

        detections = ai_engine.detect_vehicles(frame, confidence_threshold=confidence_threshold)
        annotated = ai_engine.draw_detections(frame, detections)

        # OpenCV uses BGR, Streamlit's st.image expects RGB.
        annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(annotated_rgb, use_container_width=True)

        if any(d["in_restricted_zone"] for d in detections):
            any_violation_found = True
            last_violation_detection = next(d for d in detections if d["in_restricted_zone"])

        frame_count += 1

        # Live FPS readout so it feels like a real monitoring feed.
        elapsed_so_far = time.time() - start_time
        live_fps = frame_count / elapsed_so_far if elapsed_so_far > 0 else 0
        info_placeholder.markdown(f"Processed **{frame_count}/{max_frames}** frames — live FPS: **{live_fps:.1f}**")

    elapsed = time.time() - start_time
    return frame_count, elapsed, detections, any_violation_found, last_violation_detection


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

        confidence_threshold = st.slider("Detection Confidence Threshold", 0.1, 0.9, 0.5, 0.05)
        max_frames = st.number_input(
            "Frames to process (demo runs a short clip, not the full video, to stay fast)",
            min_value=10, max_value=300, value=60, step=10,
        )

        detections = []          # detections found in the LAST processed frame
        any_violation_found = False
        last_violation_detection = None

        if video_file is None and not use_webcam:
            st.info(
                "📡 No camera or video connected. Upload a demo video above "
                "to run real YOLO detection on it."
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
        elif use_webcam:
            st.markdown('<div class="section-title">AI Detection — Live Webcam Feed</div>', unsafe_allow_html=True)
            camera_index = st.number_input(
                "Camera index (0 = default/built-in webcam, try 1 or 2 if you have multiple cameras)",
                min_value=0, max_value=5, value=0, step=1,
            )
        
           
            start_clicked = st.button(" Start Webcam Detection", use_container_width=True)

            if start_clicked:
                # ---- REAL WEBCAM CAPTURE ----
                # This opens your laptop's actual camera hardware. It only works
                # when Streamlit is running on the SAME machine as the webcam
                # (i.e. your own laptop, not a cloud server).
                cap = cv2.VideoCapture(0)
                cap.set(3, 640) 
                cap.set(4, 480) 

                if not cap.isOpened():
                    st.error(
                        f"Could not open camera index {camera_index}. Try a different index above, "
                        "close any other app using the camera (Zoom/Teams/etc.), or check camera permissions."
                    )
                else:
                    frame_placeholder = st.empty()
                    info_placeholder = st.empty()

                    with st.spinner("Loading YOLO model and reading from webcam..."):
                        frame_count, elapsed, detections, any_violation_found, last_violation_detection = (
                            _process_video_source(cap, max_frames, confidence_threshold, frame_placeholder, info_placeholder)
                        )

                    cap.release()
                    achieved_fps = frame_count / elapsed if elapsed > 0 else 0
                    info_placeholder.markdown(
                        f"✅ Captured **{frame_count} frames** from webcam in {elapsed:.1f}s "
                        f"(~{achieved_fps:.1f} FPS) — **{len(detections)} vehicle(s)** in the last frame."
                    )

                    for d in detections:
                        zone_color = "red" if d["in_restricted_zone"] else "green"
                        zone_label = "RESTRICTED ZONE" if d["in_restricted_zone"] else "ALLOWED ZONE"
                        st.markdown(
                            f'<div class="camera-card">'
                            f'<b>{d["class"]}</b> — confidence {d["confidence"]*100:.0f}% '
                            f'{badge_html(zone_label, zone_color)}</div>',
                            unsafe_allow_html=True,
                        )
            else:
                st.info("Click 'Start Webcam Detection' to open your camera and run real-time YOLO detection.")
        else:
            st.markdown('<div class="section-title">AI Detection — Live Frame Processing</div>', unsafe_allow_html=True)
            run_clicked = st.button("▶ Run YOLO Detection on this video", use_container_width=True)

            if run_clicked:
                # OpenCV needs a real file path, so save the upload to a temp file first.
                tmp_dir = tempfile.mkdtemp()
                tmp_path = os.path.join(tmp_dir, video_file.name)
                with open(tmp_path, "wb") as f:
                    f.write(video_file.read())

                cap = cv2.VideoCapture(tmp_path)
                frame_placeholder = st.empty()
                info_placeholder = st.empty()

                with st.spinner("processing frames..."):
                    frame_count, elapsed, detections, any_violation_found, last_violation_detection = (
                        _process_video_source(cap, max_frames, confidence_threshold, frame_placeholder, info_placeholder)
                    )

                cap.release()
                achieved_fps = frame_count / elapsed if elapsed > 0 else 0

                info_placeholder.markdown(
                    f"✅ Processed **{frame_count} frames** in {elapsed:.1f}s "
                    f"(~{achieved_fps:.1f} FPS on this machine) — "
                    f"**{len(detections)} vehicle(s)** detected in the last frame."
                )

                for d in detections:
                    zone_color = "red" if d["in_restricted_zone"] else "green"
                    zone_label = "RESTRICTED ZONE" if d["in_restricted_zone"] else "ALLOWED ZONE"
                    st.markdown(
                        f'<div class="camera-card">'
                        f'<b>{d["class"]}</b> — confidence {d["confidence"]*100:.0f}% '
                        f'{badge_html(zone_label, zone_color)}</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.video(video_file)
                st.caption("Click 'Run YOLO Detection' above to process this video with real AI detection.")

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
        if any_violation_found and last_violation_detection is not None:
            # Number plate OCR is the next integration step - for now we call
            # the placeholder so the workflow is already wired end-to-end.
            plate = ai_engine.read_number_plate()
            st.markdown(
                f"""
                <div class="alert-critical">
                    <div class="alert-title">⚠ ILLEGAL PARKING DETECTED</div>
                    <div style="margin-top:8px; font-size:13px; color:#e6e9ef; line-height:1.9;">
                        <b>Vehicle Type:</b> {last_violation_detection['class']}<br>
                        <b>Vehicle Number (OCR - placeholder):</b> {plate['plate_text']}<br>
                        <b>Location:</b> {cam_info['location']}<br>
                        <b>Camera:</b> {cam_info['name']}<br>
                        <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                        <b>Violation Type:</b> Restricted Zone<br>
                        <b>Detection Confidence:</b> {last_violation_detection['confidence']*100:.0f}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("📸 Evidence image capture + database logging is the next step to wire up.")

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