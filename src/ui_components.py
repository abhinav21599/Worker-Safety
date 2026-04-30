"""Reusable Streamlit UI building blocks."""
import streamlit as st


def render_header(is_running: bool = False):
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("<h1 style='margin-bottom:0;'>🛡️ Safety Monitoring Dashboard</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:1.05rem;'>AI-Powered Multi-PPE Detection System</p>", unsafe_allow_html=True)
    with col2:
        badge = "<span class='status-badge'>🟢 LIVE</span>" if is_running else "<span class='status-badge-offline'>⏸️ OFFLINE</span>"
        st.markdown(f"<br><div style='text-align:right;'>{badge}</div>", unsafe_allow_html=True)
    st.markdown("---")


def render_stat_cards(total, violations, compliance):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='stat-card blue'><div class='stat-label'>👷 Total Workers</div><div class='stat-value'>{total}</div><div class='stat-sub'>detected in frame</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='stat-card red'><div class='stat-label'>⚠️ Active Violations</div><div class='stat-value'>{violations}</div><div class='stat-sub'>missing PPE</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='stat-card green'><div class='stat-label'>✅ Compliance</div><div class='stat-value'>{compliance}%</div><div class='stat-sub'>of workforce</div></div>", unsafe_allow_html=True)


def render_alerts(container, alerts, workers):
    with container.container():
        if alerts:
            for msg in alerts:
                st.markdown(f"<div class='alert-danger'>{msg}</div>", unsafe_allow_html=True)
        elif workers > 0:
            st.markdown("<div class='alert-success'>✅ All visible workers are PPE-compliant</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center;padding:40px 10px;opacity:0.5;'>Scanning area… no workers detected.</div>", unsafe_allow_html=True)


def render_offline_video(container):
    container.markdown("<div class='offline-placeholder'>📷&nbsp; Camera offline – click <b>Start Camera</b> to begin</div>", unsafe_allow_html=True)


def render_offline_alerts(container):
    container.markdown("<div class='card' style='height:380px;display:flex;align-items:center;justify-content:center;opacity:0.5;'>Waiting for feed…</div>", unsafe_allow_html=True)


def render_logs(container, logs):
    with container.container():
        if not logs:
            st.markdown("<div style='text-align:center;padding:20px;opacity:0.45;'>No events yet.</div>", unsafe_allow_html=True)
            return
        for entry in reversed(logs[-15:]):
            icon = "🔴" if entry.get("type") == "violation" else "🟢"
            st.markdown(f"<div class='log-entry'><span class='log-time'>{entry['time']}</span>{icon} {entry['msg']}</div>", unsafe_allow_html=True)
