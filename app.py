import streamlit as st
import cv2
import numpy as np
import time
import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import threading
from collections import deque

now = datetime.now()

# Ensure local 'src' is discoverable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import LIGHT_THEME, DARK_THEME, get_css, PAGE_CONFIG
import src.ui_components as ui
from src.detector import WorkerSafetyDetector

# 1. PAGE CONFIG
st.set_page_config(**PAGE_CONFIG)

def get_safety_detector(conf: float):
    # Forced reload by removing cache
    return WorkerSafetyDetector(conf=conf)

# Initialize detector (using session state confidence or default)
detector = get_safety_detector(st.session_state.get("confidence", 0.35))

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
def _init(key, val):
    if key not in st.session_state:
        st.session_state[key] = val

_init("running",       False)
_init("dark_mode",     True)
_init("confidence",    0.20)

# Cleanup logic for stale video streams (Fixes camera-still-on after reload)
if "vstream" in st.session_state:
    if not st.session_state.get("running", False):
        try:
            st.session_state.vstream.stop()
            st.session_state.vstream = None
            # Force detector reset when camera is killed or stale
            detector.reset()
        except:
            pass

_init("cam_index",     0)
_init("logs",          [])
_init("chart_data",    pd.DataFrame(columns=["Time", "Workers", "Violations", "Falls"]))
_init("page",          "Executive Dashboard")
_init("surveillance_mode", "Standard")
_init("session_start", datetime.now())
_init("total_workers", 0)
_init("total_viols",   0)
_init("emergency",     False)
_init("alert_dismissed", False)

# ─────────────────────────────────────────────
# THEME SELECTION
# ─────────────────────────────────────────────
theme = DARK_THEME if st.session_state.dark_mode else LIGHT_THEME
st.markdown(get_css(theme), unsafe_allow_html=True)

# ─────────────────────────────────────────────
# THREADED VIDEO HELPERS
# ─────────────────────────────────────────────
class VideoStream:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(src)
        self.q = deque(maxlen=2)
        self.stopped = False
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while not self.stopped:
            if not self.cap.isOpened():
                break
            ok, frame = self.cap.read()
            if ok:
                self.q.append(frame)
            else:
                time.sleep(0.01)

    def read(self):
        return self.q[-1] if self.q else None

    def stop(self):
        self.stopped = True
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=0.5)
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()

# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
        <div class='sb-header'>
            <div class='sb-logo'>WORKER SAFETY</div>
            <div style='font-size:0.6rem; opacity:0.6; margin-top:5px; letter-spacing:3px;'>ENTERPRISE INTELLIGENCE</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='sb-section'>Command Center</div>", unsafe_allow_html=True)
    pages = [
        "Executive Dashboard", "Live Monitoring", "Worker Intelligence",
        "Attendance & Shift Tracking", "Safety Analytics", "Threat Detection",
        "Compliance Center", "Incident Timeline", "Environmental Sensors",
        "Restricted Zones", "Predictive Insights", "Surveillance Modes", "System Control"
    ]
    
    for p in pages:
        if st.button(f"{p}", use_container_width=True, type="secondary" if st.session_state.page != p else "primary"):
            st.session_state.page = p
            st.rerun()

    st.markdown("<div class='sb-section'>Detection Settings</div>", unsafe_allow_html=True)
    new_conf = st.slider("Sensitivity (Lower = More Sensitive)", 0.10, 0.90, st.session_state.confidence, 0.05)
    if new_conf != st.session_state.confidence:
        st.session_state.confidence = new_conf
        st.rerun()

    st.markdown("<div class='sb-section'>System Performance</div>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class="sb-mini-grid">
            <div class="sb-mini">
                <div class="sb-mini-val">98.4%</div>
                <div class="sb-mini-lbl">RELIABILITY</div>
            </div>
            <div class="sb-mini">
                <div class="sb-mini-val">0.02s</div>
                <div class="sb-mini-lbl">LATENCY</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.session_state.surveillance_mode = st.selectbox("Surveillance Mode", ["Standard", "Thermal Vision", "Hazard Detection", "Worker Tracking", "Emergency Scan"])
    
    if st.button("RESET SYSTEM", use_container_width=True):
        st.session_state.logs = []
        st.session_state.chart_data = pd.DataFrame(columns=["Time", "Workers", "Violations", "Falls"])
        st.rerun()

# ─────────────────────────────────────────────
# MAIN CONTENT ROUTING
# ─────────────────────────────────────────────
ui.render_header(st.session_state.running, st.session_state.page)

# Calculate dynamic compliance rate
comp_rate = 100
if st.session_state.total_workers > 0:
    comp_rate = int(((st.session_state.total_workers - st.session_state.total_viols) / st.session_state.total_workers) * 100)
    comp_rate = max(0, min(100, comp_rate))

if st.session_state.page == "Executive Dashboard":
    ui.render_stat_cards(st.session_state.total_workers, st.session_state.total_viols, comp_rate)
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("<div class='sec-head'>📈 Predictive Safety Trends</div>", unsafe_allow_html=True)
        # Plotly Chart
        fig = go.Figure()
        x_data = [f"T-{i}h" for i in range(7, 0, -1)]
        fig.add_trace(go.Scatter(x=x_data, y=[12, 18, 15, 25, 20, 28, 22], mode='lines+markers', name='Compliance', 
                                line=dict(color='#38BDF8', width=4), fill='tozeroy', fillcolor='rgba(56, 189, 248, 0.1)'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#F8FAFC", 
                          height=300, margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        ui.render_attendance_table()
        
    with c2:
        ui.render_worker_intelligence()
        log_container = st.empty()
        ui.render_logs(log_container, st.session_state.logs)

elif st.session_state.page == "Live Monitoring":
    emergency_container = st.empty()
    if st.session_state.emergency and not st.session_state.alert_dismissed:
        if ui.render_emergency_banner(True):
            st.session_state.alert_dismissed = True
            st.rerun()
    
    col_v, col_i = st.columns([3, 1])
    
    with col_v:
        video_placeholder = st.empty()
        if not st.session_state.running:
            ui.render_offline_video(video_placeholder)
            if st.button("🚀 INITIALIZE SURVEILLANCE", use_container_width=True):
                detector.reset() # Force reset on every start
                st.session_state.running = True
                st.rerun()
        else:
            if st.button("🛑 DEACTIVATE SYSTEM", use_container_width=True):
                st.session_state.running = False
                if "vstream" in st.session_state and st.session_state.vstream:
                    st.session_state.vstream.stop()
                    st.session_state.vstream = None
                detector.reset() # Reset on stop
                st.rerun()
    
    with col_i:
        stats_container = st.empty()
        st.markdown("<div class='sec-head'>⚡ Real-time Alerts</div>", unsafe_allow_html=True)
        alert_container = st.empty()
        st.markdown("---")
        log_container = st.empty()
        
        # Initial render
        with stats_container.container():
            ui.render_stat_cards(st.session_state.total_workers, st.session_state.total_viols, comp_rate, vertical=True)
        ui.render_alerts(alert_container, [l['msg'] for l in st.session_state.logs[-3:] if l['type'] == 'violation'], st.session_state.total_workers)
        ui.render_logs(log_container, st.session_state.logs)

    if st.session_state.running:
        # Ensure vstream is initialized
        if "vstream" not in st.session_state or st.session_state.vstream is None:
            st.session_state.vstream = VideoStream(st.session_state.cam_index)
        
        vstream = st.session_state.vstream
        
        try:
            while st.session_state.running:
                frame = vstream.read()
                if frame is None:
                    # Show a "Waiting for camera..." if it takes too long
                    time.sleep(0.1)
                    continue
                
                # Real Detection
                frame, w, v, alerts, falls = detector.process_frame(frame)
                
                # Apply Surveillance Modes
                if st.session_state.surveillance_mode == "Thermal Vision":
                    frame = cv2.applyColorMap(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLORMAP_JET)
                elif st.session_state.surveillance_mode == "Emergency Scan":
                    frame = cv2.applyColorMap(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLORMAP_HOT)
                    for j in range(0, frame.shape[0], 20):
                        cv2.line(frame, (0, j), (frame.shape[1], j), (0,0,0), 1)
                
                st.session_state.total_workers = w
                st.session_state.total_viols = v
                
                # Handle emergency and alert dismissal with cooldown
                new_emergency = (falls > 0)
                
                # If no emergency, reset the dismissal so it can trigger next time
                if not new_emergency:
                    if st.session_state.get("emergency_start_time"):
                        # If more than 5 seconds since last fall, allow new alert
                        if time.time() - st.session_state.emergency_start_time > 5:
                            st.session_state.alert_dismissed = False
                else:
                    if "emergency_start_time" not in st.session_state:
                        st.session_state.emergency_start_time = time.time()

                st.session_state.emergency = new_emergency
                
                with emergency_container.container():
                    if st.session_state.emergency and not st.session_state.alert_dismissed:
                        # Use a timestamp-based key to avoid duplicate key errors
                        if ui.render_emergency_banner(True, key_id=str(int(time.time() // 10))):
                            st.session_state.alert_dismissed = True
                            st.rerun()
                
                # Update dynamic compliance rate for loop
                loop_comp_rate = 100
                if w > 0:
                    loop_comp_rate = int(((w - v) / w) * 100)
                    loop_comp_rate = max(0, min(100, loop_comp_rate))

                if alerts:
                    recent_msgs = [l["msg"] for l in st.session_state.logs[-5:]]
                    for a in alerts:
                        if a not in recent_msgs:
                            st.session_state.logs.append({
                                "time": datetime.now().strftime("%H:%M:%S"), 
                                "msg": a, 
                                "type": "violation" if ("⚠️" in a or "🚨" in a) else "info"
                            })

                # Update Placeholders
                video_placeholder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)
                
                with stats_container.container():
                    ui.render_stat_cards(st.session_state.total_workers, st.session_state.total_viols, loop_comp_rate, vertical=True)
                
                ui.render_alerts(alert_container, [l['msg'] for l in st.session_state.logs[-3:] if l['type'] == 'violation'], st.session_state.total_workers)
                ui.render_logs(log_container, st.session_state.logs)
                
                time.sleep(0.01)
        except Exception as e:
            st.error(f"Stream Error: {e}")
        finally:
            if not st.session_state.running:
                if "vstream" in st.session_state and st.session_state.vstream:
                    st.session_state.vstream.stop()
                    st.session_state.vstream = None

else:
    # Modules with specific UI
    if st.session_state.page == "Attendance & Shift Tracking":
        ui.render_attendance_table()
    elif st.session_state.page == "Worker Intelligence":
        ui.render_worker_intelligence()
    elif st.session_state.page == "Incident Timeline":
        log_container = st.empty()
        ui.render_logs(log_container, st.session_state.logs)
    elif st.session_state.page == "Safety Analytics":
        ui.render_safety_analytics()
    elif st.session_state.page == "Threat Detection":
        ui.render_threat_detection()
    elif st.session_state.page == "Compliance Center":
        ui.render_compliance_center()
    elif st.session_state.page == "Environmental Sensors":
        ui.render_environmental_sensors()
    elif st.session_state.page == "Restricted Zones":
        ui.render_restricted_zones()
    elif st.session_state.page == "Predictive Insights":
        ui.render_predictive_insights()
    elif st.session_state.page == "Surveillance Modes":
        ui.render_surveillance_modes()
    elif st.session_state.page == "System Control":
        ui.render_system_control()
    else:
        # Generic Module Placeholder for any others
        st.markdown(f"""
            <div class='glass-card' style='height:400px; display:flex; align-items:center; justify-content:center; flex-direction:column; border: 1px solid rgba(56, 189, 248, 0.2);'>
                <div style='font-size:4rem; animation: float 3s infinite ease-in-out;'>🛰️</div>
                <div style='font-size:2rem; font-weight:900; margin-top:30px; font-family:Space Grotesk; letter-spacing:2px; color:#38BDF8;'>{st.session_state.page.upper()}</div>
                <div style='opacity:0.6; margin-top:10px; font-weight:500;'>MODULE ENCRYPTED | INITIALIZING NEURAL LINK...</div>
                <div style='margin-top:40px; width:300px; height:6px; background:rgba(255,255,255,0.05); border-radius:3px; overflow:hidden;'>
                    <div style='width:65%; height:100%; background:linear-gradient(90deg, #38BDF8, #A855F7); border-radius:3px; box-shadow:0 0 20px #38BDF8;'></div>
                </div>
            </div>
            <style>
                @keyframes float {{
                    0% {{ transform: translateY(0px); }}
                    50% {{ transform: translateY(-20px); }}
                    100% {{ transform: translateY(0px); }}
                }}
            </style>
        """, unsafe_allow_html=True)
