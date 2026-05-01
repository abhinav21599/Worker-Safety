"""Reusable Streamlit UI building blocks."""
import streamlit as st
import pandas as pd
from datetime import datetime

def render_header(is_running: bool = False, page_title: str = "Safety Monitoring Dashboard"):
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"<h1 style='margin-bottom:0;'>🛡️ {page_title}</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:1.05rem; opacity:0.8;'>Industrial Workforce Intelligence Platform | Real-time Safety Monitoring</p>", unsafe_allow_html=True)
    with col2:
        badge = "<span class='status-badge'>🟢 LIVE</span>" if is_running else "<span class='status-badge-offline'>⏸️ OFFLINE</span>"
        st.markdown(f"<br><div style='text-align:right;'>{badge}</div>", unsafe_allow_html=True)
    st.markdown("---")


def render_stat_cards(total, violations, compliance, vertical=False):
    if not vertical:
        c1, c2, c3 = st.columns(3)
    else:
        c1, c2, c3 = st.container(), st.container(), st.container()
        
    with c1:
        st.markdown(f"""
            <div class='glass-card kpi-blue' style='margin-bottom: {"10px" if vertical else "16px"} !important;'>
                <div class='kpi-label'>👷 Total Workers</div>
                <div class='kpi-value' style='font-size: {"2.2rem" if vertical else "2.8rem"};'>{total}</div>
                <div class='kpi-sub'>Active in zone</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class='glass-card kpi-red' style='margin-bottom: {"10px" if vertical else "16px"} !important;'>
                <div class='kpi-label'>⚠️ Active Violations</div>
                <div class='kpi-value' style='font-size: {"2.2rem" if vertical else "2.8rem"};'>{violations}</div>
                <div class='kpi-sub'>Action required</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class='glass-card kpi-green' style='margin-bottom: {"10px" if vertical else "16px"} !important;'>
                <div class='kpi-label'>✅ Compliance Rate</div>
                <div class='kpi-value' style='font-size: {"2.2rem" if vertical else "2.8rem"};'>{compliance}%</div>
                <div class='kpi-sub'>Standards met</div>
            </div>
        """, unsafe_allow_html=True)

def render_worker_intelligence():
    st.markdown("<div class='sec-head'>🧬 Worker Intelligence Feed</div>", unsafe_allow_html=True)
    workers = [
        {"id": "W-1024", "status": "ACTIVE", "risk": "LOW", "ppe": "100%", "zone": "A-1"},
        {"id": "W-1089", "status": "IDLE", "risk": "MED", "ppe": "50%", "zone": "B-4"},
        {"id": "W-2045", "status": "ACTIVE", "risk": "LOW", "ppe": "100%", "zone": "A-2"},
        {"id": "W-0982", "status": "HIGH RISK", "risk": "CRIT", "ppe": "0%", "zone": "RESTRICTED"},
    ]
    
    for w in workers:
        color = "#4ADE80" if w['risk'] == "LOW" else ("#FBBF24" if w['risk'] == "MED" else "#FB7185")
        st.markdown(f"""
            <div class='glass-card' style='padding:12px 15px !important; margin-bottom:10px !important;'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <span style='font-family:Space Grotesk; font-weight:800; color:#38BDF8;'>{w['id']}</span>
                        <span style='font-size:0.7rem; margin-left:10px; opacity:0.6;'>ZONE: {w['zone']}</span>
                    </div>
                    <span style='font-size:0.7rem; font-weight:800; color:{color}; border:1px solid {color}44; padding:2px 8px; border-radius:4px;'>{w['status']}</span>
                </div>
                <div style='margin-top:12px; height:8px; background:rgba(255,255,255,0.1); border-radius:4px;'>
                    <div style='width:{w['ppe']}; height:100%; background:{color}; border-radius:4px; box-shadow:0 0 10px {color}88;'></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

def render_attendance_table():
    st.markdown("<div class='sec-head'>📅 Shift Attendance Log</div>", unsafe_allow_html=True)
    data = {
        "Worker ID": ["W-1024", "W-1089", "W-2045", "W-0982", "W-1156", "W-3021"],
        "Entry Time": ["08:00 AM", "08:15 AM", "08:30 AM", "09:12 AM", "09:45 AM", "10:05 AM"],
        "Shift": ["MORNING", "MORNING", "MORNING", "MORNING", "MID", "MID"],
        "PPE Score": ["100%", "85%", "100%", "40%", "95%", "100%"],
        "Status": ["ON-SITE", "ON-SITE", "ON-SITE", "FLAGGED", "ON-SITE", "BREAK"]
    }
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

def render_emergency_banner(active=False, key_id=""):
    if active:
        cols = st.columns([0.9, 0.1])
        with cols[0]:
            st.markdown("""
                <div class='pill-fallen' style='margin-bottom:20px;'>
                    <div style='font-size:1.5rem;'>🚨</div>
                    <div>
                        <div style='font-weight:900; font-size:1.2rem; letter-spacing:0.05em;'>CRITICAL EMERGENCY DETECTED</div>
                        <div style='font-size:0.8rem; opacity:0.9;'>Automated lockdown procedures initiated. Response team dispatched.</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            # Use unique key to avoid Streamlit Duplicate Key error
            if st.button("✖️", key=f"dismiss_fall_{key_id}", help="Dismiss Alert"):
                return True
    return False

def render_alerts(container, alerts, workers):
    with container.container():
        if alerts:
            for msg in alerts:
                cls = "pill-danger" if "🚨" in msg or "⚠️" in msg else "pill-success"
                st.markdown(f"<div class='{cls}'>{msg}</div>", unsafe_allow_html=True)
        elif workers > 0:
            st.markdown("<div class='pill-success'>✅ All visible workers are PPE-compliant</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center;padding:40px 10px;opacity:0.5;'>Scanning area… no workers detected.</div>", unsafe_allow_html=True)


def render_offline_video(container):
    container.markdown("<div class='feed-container' style='height:480px; display:flex; align-items:center; justify-content:center;'><div><div style='font-size:4rem; text-align:center; opacity:0.2;'>📷</div><div style='opacity:0.5; font-weight:700;'>SYSTEM STANDBY - ACTIVATE MONITORING</div></div></div>", unsafe_allow_html=True)


def render_logs(container, logs):
    with container.container():
        st.markdown("<div class='sec-head'>🕒 Incident Timeline</div>", unsafe_allow_html=True)
        if not logs:
            st.markdown("<div style='text-align:center;padding:20px;opacity:0.45;'>No events in timeline.</div>", unsafe_allow_html=True)
            return
        for entry in reversed(logs[-15:]):
            icon = "🔴" if entry.get("type") == "violation" else "🟢"
            color = "#FB7185" if entry.get("type") == "violation" else "#4ADE80"
            st.markdown(f"""
                <div class='log-row'>
                    <span class='log-ts'>{entry['time']}</span>
                    <span style='color:{color};'>{icon} {entry['msg']}</span>
                </div>
            """, unsafe_allow_html=True)

def render_safety_analytics():
    import plotly.graph_objects as go
    st.markdown("<div class='sec-head'>📊 Safety Compliance Analytics</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<p style='font-size:0.9rem; opacity:0.7;'>PPE Compliance Trends</p>", unsafe_allow_html=True)
        fig = go.Figure(go.Bar(x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], y=[92, 88, 95, 85, 98, 100, 97], marker_color='#38BDF8'))
        fig.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#F8FAFC", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("<p style='font-size:0.9rem; opacity:0.7;'>Incident Distribution</p>", unsafe_allow_html=True)
        fig = go.Figure(go.Pie(labels=['Hardhat', 'Vest', 'Gloves', 'Unauthorized'], values=[45, 25, 20, 10], hole=.6, marker=dict(colors=['#38BDF8', '#818CF8', '#A78BFA', '#FB7185'])))
        fig.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', font_color="#F8FAFC", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

def render_threat_detection():
    st.markdown("<div class='sec-head'>🛡️ Real-time Threat Analysis</div>", unsafe_allow_html=True)
    threats = [
        {"name": "Heat Stress Risk", "level": "MEDIUM", "zone": "Foundry A", "color": "#FBBF24"},
        {"name": "Unsafe Scaffolding", "level": "CRITICAL", "zone": "Zone C-2", "color": "#FB7185"},
        {"name": "Toxic Gas Leak (Simulated)", "level": "LOW", "zone": "Storage 4", "color": "#4ADE80"},
    ]
    for t in threats:
        st.markdown(f"""
            <div class='glass-card' style='border-left: 5px solid {t['color']} !important; margin-bottom:10px !important;'>
                <div style='display:flex; justify-content:space-between;'>
                    <div style='font-weight:700;'>{t['name']}</div>
                    <div style='color:{t['color']}; font-weight:800; font-size:0.8rem;'>{t['level']}</div>
                </div>
                <div style='font-size:0.8rem; opacity:0.6; margin-top:5px;'>Location: {t['zone']}</div>
            </div>
        """, unsafe_allow_html=True)

def render_compliance_center():
    st.markdown("<div class='sec-head'>📋 Regulatory Compliance Center</div>", unsafe_allow_html=True)
    st.info("Currently monitoring OSHA Standard 1910.132 (Personal Protective Equipment)")
    checks = [
        {"task": "Hardhat Verification (Computer Vision)", "status": "PASS"},
        {"task": "High-Visibility Vest Check", "status": "PASS"},
        {"task": "Safety Boot Recognition", "status": "PENDING"},
        {"task": "Restricted Zone Authorization", "status": "FAIL"},
    ]
    for c in checks:
        icon = "✅" if c['status'] == "PASS" else ("⏳" if c['status'] == "PENDING" else "❌")
        st.markdown(f"""
            <div style='display:flex; justify-content:space-between; padding:10px; border-bottom:1px solid rgba(255,255,255,0.05);'>
                <div style='opacity:0.8;'>{c['task']}</div>
                <div style='font-weight:700;'>{icon} {c['status']}</div>
            </div>
        """, unsafe_allow_html=True)

def render_environmental_sensors():
    st.markdown("<div class='sec-head'>🌡️ Environmental Sensor Array</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Temperature", "24.5°C", "0.2°C")
    c2.metric("Humidity", "42%", "-1%")
    c3.metric("Air Quality", "AQI 32", "Good")
    st.markdown("<br>", unsafe_allow_html=True)
    st.image("https://img.freepik.com/free-vector/industrial-heat-map-infographic_23-2148821430.jpg?w=800", caption="Facility Heatmap (Mock Data)")

def render_restricted_zones():
    st.markdown("<div class='sec-head'>🚫 Restricted Zone Management</div>", unsafe_allow_html=True)
    zones = [
        {"id": "RZ-1", "name": "Main Transformer", "status": "SECURED", "access": "LVL 4"},
        {"id": "RZ-2", "name": "Chemical Storage", "status": "ACTIVE BREACH", "access": "LVL 5"},
        {"id": "RZ-3", "name": "Roof Maintenance", "status": "LOCKED", "access": "LVL 2"},
    ]
    for z in zones:
        color = "#FB7185" if "BREACH" in z['status'] else "#4ADE80"
        st.markdown(f"""
            <div class='glass-card' style='margin-bottom:10px;'>
                <div style='display:flex; justify-content:space-between;'>
                    <div style='font-weight:800; color:#38BDF8;'>{z['id']}: {z['name']}</div>
                    <div style='color:{color}; font-size:0.8rem; font-weight:900;'>{z['status']}</div>
                </div>
                <div style='font-size:0.7rem; opacity:0.5; margin-top:5px;'>REQUIRED CLEARANCE: {z['access']}</div>
            </div>
        """, unsafe_allow_html=True)

def render_predictive_insights():
    st.markdown("<div class='sec-head'>🔮 AI Predictive Safety Insights</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class='glass-card' style='background: linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(56, 189, 248, 0.1)) !important; border: 1px solid rgba(168, 85, 247, 0.3) !important;'>
            <div style='font-size:1.1rem; font-weight:700; color:#A855F7;'>Neural Net Forecast</div>
            <p style='margin-top:10px; font-size:0.9rem;'>Based on historical trends and current humidity levels, there is a <b>24% increased risk</b> of slip-and-fall incidents in <b>Zone B-4</b> over the next 4 hours.</p>
            <div style='margin-top:15px; font-size:0.8rem; font-weight:700; color:#38BDF8;'>RECOMMENDATION: Deploy anti-slip mats & increase supervisor presence.</div>
        </div>
    """, unsafe_allow_html=True)

def render_system_control():
    st.markdown("<div class='sec-head'>⚙️ System & Hardware Control</div>", unsafe_allow_html=True)
    stats = {
        "AI Model": "YOLOv8x-Safety-Custom",
        "Framework": "PyTorch 2.2.1 + CUDA 12.1",
        "GPU Load": "42%",
        "VRAM Usage": "4.2GB / 12GB",
        "Camera Feed": "Active (1/1)",
        "Database": "Synchronized"
    }
    for k, v in stats.items():
        st.markdown(f"""
            <div style='display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.05);'>
                <div style='opacity:0.6; font-size:0.9rem;'>{k}</div>
                <div style='font-weight:600; font-size:0.9rem; color:#38BDF8;'>{v}</div>
            </div>
        """, unsafe_allow_html=True)

def render_surveillance_modes():
    st.markdown("<div class='sec-head'>🛰️ Advanced Surveillance Configuration</div>", unsafe_allow_html=True)
    modes = [
        {"name": "Standard Monitoring", "desc": "RGB analysis for PPE and falls.", "active": True},
        {"name": "Thermal Overlay", "desc": "Heat signature mapping for personnel.", "active": False},
        {"name": "Hazard Identification", "desc": "Neural detection of fire/smoke/leaks.", "active": False},
        {"name": "Biometric Tracking", "desc": "Identify authorized personnel via gait/face.", "active": False},
    ]
    for m in modes:
        status = "🟢 ACTIVE" if m['active'] else "⚪ STANDBY"
        st.markdown(f"""
            <div class='glass-card' style='margin-bottom:10px;'>
                <div style='display:flex; justify-content:space-between;'>
                    <div style='font-weight:700;'>{m['name']}</div>
                    <div style='font-size:0.7rem; opacity:0.8;'>{status}</div>
                </div>
                <div style='font-size:0.8rem; opacity:0.6; margin-top:5px;'>{m['desc']}</div>
            </div>
        """, unsafe_allow_html=True)
