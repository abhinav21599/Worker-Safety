import streamlit as st
import cv2
import numpy as np
import time
import pandas as pd
from datetime import datetime
from ultralytics import YOLO

# ─────────────────────────────────────────────
# PAGE CONFIG  (must be first st call)
# ─────────────────────────────────────────────
st.set_page_config(page_title="PPE Safety Monitor", layout="wide", page_icon="🦺")

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
def _init(key, val):
    if key not in st.session_state:
        st.session_state[key] = val

_init("running",       False)
_init("dark_mode",     False)
_init("confidence",    0.45)
_init("cam_index",     0)
_init("logs",          [])
_init("chart_data",    pd.DataFrame(columns=["Time", "Workers", "Violations"]))
_init("page",          "dashboard")
_init("session_start", datetime.now())
_init("total_frames",  0)
_init("total_workers", 0)
_init("total_viols",   0)

# ─────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────
if st.session_state.dark_mode:
    BG          = "#0D1117"
    SURFACE     = "#161B22"
    SURFACE2    = "#21262D"
    BORDER      = "#30363D"
    TEXT        = "#E6EDF3"
    TEXT2       = "#8B949E"
    BLUE        = "#58A6FF"
    GREEN       = "#3FB950"
    RED         = "#F85149"
    AMBER       = "#D29922"
    SIDEBAR_BG  = "#161B22"
else:
    BG          = "#F0F4F8"
    SURFACE     = "#FFFFFF"
    SURFACE2    = "#F6F8FA"
    BORDER      = "#D0D7DE"
    TEXT        = "#1C2128"
    TEXT2       = "#57606A"
    BLUE        = "#0969DA"
    GREEN       = "#1A7F37"
    RED         = "#CF222E"
    AMBER       = "#9A6700"
    SIDEBAR_BG  = "#FFFFFF"

CHART_COLOR = "#EF4444"

# ─────────────────────────────────────────────
# GLOBAL CSS — injected ONCE, uses Python vars
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; }}

html, body, .stApp {{
    font-family: 'Inter', sans-serif;
    background-color: {BG} !important;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background-color: {SIDEBAR_BG} !important;
    border-right: 1px solid {BORDER} !important;
    padding-top: 0 !important;
}}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {{
    color: {TEXT} !important;
}}

/* Sidebar brand header */
.sb-brand {{
    background: linear-gradient(135deg, {BLUE}, #6D28D9);
    margin: -1rem -1rem 1.2rem -1rem;
    padding: 24px 20px 20px;
    border-radius: 0 0 16px 16px;
}}
.sb-brand-title {{
    font-size: 1.15rem; font-weight: 800;
    color: #fff; margin-bottom: 2px;
}}
.sb-brand-sub {{
    font-size: .72rem; color: rgba(255,255,255,.7);
    letter-spacing: .04em;
}}

/* Sidebar section label */
.sb-section {{
    font-size: .68rem; font-weight: 700; letter-spacing: .1em;
    text-transform: uppercase; color: {TEXT2};
    margin: 16px 0 6px; padding-left: 2px;
}}

/* System status row */
.sb-status-row {{
    display: flex; align-items: center; justify-content: space-between;
    background: {SURFACE2}; border: 1px solid {BORDER};
    border-radius: 10px; padding: 10px 14px; margin-bottom: 6px;
}}
.sb-status-label {{ font-size: .82rem; color: {TEXT2}; font-weight: 500; }}
.sb-status-val   {{ font-size: .82rem; color: {TEXT};  font-weight: 700; }}
.sb-dot-green {{ display:inline-block; width:8px; height:8px; border-radius:50%; background:{GREEN}; margin-right:6px; animation: glow 2s infinite; }}
.sb-dot-red   {{ display:inline-block; width:8px; height:8px; border-radius:50%; background:{RED};   margin-right:6px; }}

/* Session summary mini cards */
.sb-mini-grid {{
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 8px; margin-bottom: 4px;
}}
.sb-mini {{
    background: {SURFACE2}; border: 1px solid {BORDER};
    border-radius: 10px; padding: 12px 10px;
    text-align: center;
}}
.sb-mini-val {{
    font-size: 1.4rem; font-weight: 800; color: {TEXT};
    line-height: 1; margin-bottom: 2px;
}}
.sb-mini-lbl {{
    font-size: .65rem; font-weight: 600; color: {TEXT2};
    text-transform: uppercase; letter-spacing: .05em;
}}

/* PPE rule pill */
.ppe-rule {{
    display: flex; align-items: center; gap: 8px;
    background: {SURFACE2}; border: 1px solid {BORDER};
    border-radius: 8px; padding: 9px 12px; margin-bottom: 6px;
    font-size: .83rem; color: {TEXT}; font-weight: 500;
}}
.ppe-rule-icon {{ font-size: 1.1rem; }}

/* Sidebar footer */
.sb-footer {{
    font-size: .7rem; color: {TEXT2}; text-align: center;
    padding-top: 12px; border-top: 1px solid {BORDER};
    line-height: 1.8;
}}

/* ── General text ── */
.stApp p, .stApp span, .stApp div, .stApp label {{ color: {TEXT2}; }}
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {{ color: {TEXT} !important; font-weight: 700; }}
hr {{ border-color: {BORDER} !important; margin: 1rem 0; }}

/* ── KPI cards (stat boxes) ── */
.kpi-wrap {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 24px 20px 20px;
    position: relative;
    overflow: hidden;
    transition: transform .25s ease, box-shadow .25s ease;
    box-shadow: 0 1px 3px rgba(0,0,0,.08), 0 4px 8px rgba(0,0,0,.04);
}}
.kpi-wrap:hover {{
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,.12);
}}
.kpi-accent {{
    position: absolute; top: 0; left: 0; right: 0; height: 4px; border-radius: 12px 12px 0 0;
}}
.kpi-icon {{
    font-size: 1.6rem; margin-bottom: 8px; display: block;
}}
.kpi-label {{
    font-size: .72rem; font-weight: 700; letter-spacing: .08em;
    text-transform: uppercase; color: {TEXT2}; margin-bottom: 6px;
}}
.kpi-value {{
    font-size: 2.6rem; font-weight: 900; color: {TEXT}; line-height: 1;
    margin-bottom: 4px;
}}
.kpi-sub {{
    font-size: .78rem; color: {TEXT2};
}}

/* ── Section header ── */
.sec-head {{
    display: flex; align-items: center; gap: 10px;
    font-size: 1rem; font-weight: 700; color: {TEXT};
    margin-bottom: 14px; padding-bottom: 10px;
    border-bottom: 2px solid {BLUE};
    width: fit-content;
}}

/* ── Camera frame wrapper ── */
.cam-wrap {{
    background: {SURFACE}; border: 1px solid {BORDER};
    border-radius: 12px; overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,.08);
}}

/* ── Alert pills ── */
.pill-danger {{
    background: #FEE2E2; color: #991B1B;
    border-left: 5px solid {RED};
    padding: 12px 16px; border-radius: 8px; margin-bottom: 8px;
    font-size: .92rem; font-weight: 600;
    animation: slideIn .3s ease;
}}
.pill-success {{
    background: #DCFCE7; color: #166534;
    border-left: 5px solid {GREEN};
    padding: 12px 16px; border-radius: 8px; margin-bottom: 8px;
    font-size: .92rem; font-weight: 600;
    animation: slideIn .3s ease;
}}
.pill-fallen {{
    background: #FFF7ED; color: #9A3412;
    border-left: 5px solid #F97316;
    padding: 14px 16px; border-radius: 8px; margin-bottom: 8px;
    font-size: .95rem; font-weight: 800;
    animation: flashPulse 1s infinite;
    box-shadow: 0 0 0 3px #FED7AA;
}}
.pill-idle {{
    background: {SURFACE2}; color: {TEXT2};
    border: 1px dashed {BORDER};
    padding: 20px 16px; border-radius: 8px;
    font-size: .9rem; text-align: center;
}}

/* ── Log row ── */
.log-row {{
    background: {SURFACE}; border: 1px solid {BORDER};
    border-radius: 8px; padding: 10px 14px; margin-bottom: 6px;
    font-size: .85rem; color: {TEXT};
    display: flex; align-items: center; gap: 10px;
}}
.log-ts {{
    font-size: .75rem; color: {TEXT2}; white-space: nowrap;
    background: {SURFACE2}; padding: 2px 7px; border-radius: 20px;
}}

/* ── Status badge ── */
.badge-live {{
    display: inline-flex; align-items: center; gap: 6px;
    background: {GREEN}22; color: {GREEN};
    border: 1px solid {GREEN}55; border-radius: 20px;
    padding: 5px 14px; font-size: .82rem; font-weight: 700;
    animation: glow 2s infinite;
}}
.badge-offline {{
    display: inline-flex; align-items: center; gap: 6px;
    background: {TEXT2}22; color: {TEXT2};
    border: 1px solid {BORDER}; border-radius: 20px;
    padding: 5px 14px; font-size: .82rem; font-weight: 700;
}}

/* ── Offline camera placeholder ── */
.cam-offline {{
    background: {SURFACE2}; border: 2px dashed {BORDER};
    border-radius: 12px; height: 380px;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    color: {TEXT2}; font-size: 1rem; gap: 12px;
}}

/* ── Settings card ── */
.s-card {{
    background: {SURFACE}; border: 1px solid {BORDER};
    border-radius: 12px; padding: 28px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
}}

/* ── Animations ── */
@keyframes slideIn {{
    from {{ opacity: 0; transform: translateX(20px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
}}
@keyframes glow {{
    0%, 100% {{ box-shadow: 0 0 0 0 {GREEN}44; }}
    50%      {{ box-shadow: 0 0 0 8px transparent; }}
}}
@keyframes flashPulse {{
    0%, 100% {{ opacity: 1; background: #FFF7ED; box-shadow: 0 0 0 3px #FED7AA; }}
    50%      {{ opacity: .85; background: #FED7AA; box-shadow: 0 0 12px #F97316; }}
}}

/* ── Override Streamlit defaults ── */
.stButton > button {{
    border-radius: 8px !important; font-weight: 600 !important;
    transition: all .2s ease !important;
}}
.stButton > button:hover {{ transform: translateY(-1px); }}
div[data-testid="stMetric"] {{ display: none; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DETECTOR  (cached so it loads only once)
# ─────────────────────────────────────────────
@st.cache_resource
def get_detector(conf: float):
    import os
    person_model = YOLO("yolov8x-pose.pt")

    # PPE model: AmirT/ppe-detection-yolov8
    # Classes: {0: 'helmet', 1: 'no-helmet', 2: 'no-vest', 3: 'person', 4: 'vest'}
    ppe_model = None
    for p in ["ppe_amirt.pt", "ppe_hardhat.pt", "ppe_model.pt"]:
        if os.path.isfile(p):
            try:
                ppe_model = YOLO(p)
                break
            except Exception:
                continue

    # Temporal state
    fall_history: dict = {}
    ppe_history:  dict = {}
    FALL_FRAMES  = 5
    PPE_WINDOW   = 5

    def run(frame):
        nonlocal fall_history, ppe_history
        fH, fW = frame.shape[:2]

        # ── Step 1: Find all people and poses ──────────────────────────────
        person_boxes = []
        poses = []
        for r in person_model(frame, stream=True, verbose=False,
                              conf=conf, classes=[0]):
            if r.boxes is not None:
                for i, box in enumerate(r.boxes):
                    bx1, by1, bx2, by2 = map(int, box.xyxy[0])
                    person_boxes.append((bx1, by1, bx2, by2, float(box.conf[0])))
                    if r.keypoints is not None and len(r.keypoints.xy) > i:
                        poses.append(r.keypoints.xy[i].cpu().numpy())
                    else:
                        poses.append(None)

        # ── Step 2: PPE model — find helmets and vests ───────────────────
        hardhat_pts = []       # [(cx, cy, conf)]
        no_hardhat_pts = []    # [(cx, cy, conf)]
        vest_pts = []          # [(cx, cy, conf)]
        no_vest_pts = []       # [(cx, cy, conf)]
        
        if ppe_model is not None:
            try:
                for r in ppe_model(frame, stream=True, verbose=False, conf=0.20):
                    for box in r.boxes:
                        px1, py1, px2, py2 = map(int, box.xyxy[0])
                        cls = ppe_model.names[int(box.cls[0])].lower()
                        pc  = float(box.conf[0])
                        pcx, pcy = (px1+px2)//2, (py1+py2)//2
                        
                        # Categorize detections
                        if cls in ["helmet", "hardhat"]:
                            hardhat_pts.append((pcx, pcy, pc))
                        elif cls in ["no-helmet", "no_helmet"]:
                            no_hardhat_pts.append((pcx, pcy, pc))
                        elif cls in ["vest", "safety-vest"]:
                            vest_pts.append((pcx, pcy, pc))
                        elif cls in ["no-vest", "no_vest"]:
                            no_vest_pts.append((pcx, pcy, pc))
            except Exception:
                pass

        workers = violations = 0
        alerts: list = []

        for idx, (x1, y1, x2, y2, det_conf) in enumerate(person_boxes):
            W, H = x2 - x1, y2 - y1
            if W < 40 or H < 50:
                continue
            workers += 1

            cx, cy   = (x1+x2)//2, (y1+y2)//2
            grid_key = (cx//100, cy//100)

            # ── Fall detection ────────────────────────────────────────
            kpts = poses[idx]
            is_horiz_pose = False
            if kpts is not None and len(kpts) >= 13:
                # 5: left shoulder, 6: right shoulder, 11: left hip, 12: right hip
                sh_y = (kpts[5][1] + kpts[6][1]) / 2 if (kpts[5][1] > 0 and kpts[6][1] > 0) else 0
                hp_y = (kpts[11][1] + kpts[12][1]) / 2 if (kpts[11][1] > 0 and kpts[12][1] > 0) else 0
                sh_x = (kpts[5][0] + kpts[6][0]) / 2 if (kpts[5][0] > 0 and kpts[6][0] > 0) else 0
                hp_x = (kpts[11][0] + kpts[12][0]) / 2 if (kpts[11][0] > 0 and kpts[12][0] > 0) else 0
                
                if sh_y > 0 and hp_y > 0:
                    dy = abs(hp_y - sh_y)
                    dx = abs(hp_x - sh_x)
                    if dy < dx or sh_y > hp_y:
                        is_horiz_pose = True

            aspect   = W / max(H, 1)
            ht_frac  = H / max(fH, 1)
            horiz_box = (aspect >= 1.30) and (ht_frac < 0.45)
            
            horiz = is_horiz_pose or horiz_box
            
            prev = fall_history.get(grid_key, 0)
            fall_history[grid_key] = (prev+1) if horiz else max(0, prev-1)
            fallen = fall_history[grid_key] >= FALL_FRAMES

            if fallen:
                violations += 1
                col = (0, 130, 255)
                lbl = "FALLEN!"
                alerts.append(f"🚨 Worker #{workers} fallen! [AR={aspect:.2f}]")
            else:
                # ── Helmet: center-point matching ─────────────────────
                head_t, head_b = y1, y1 + int(H * 0.40)
                has_helmet = False
                explicit_no_helmet = False

                if ppe_model is not None:
                    for (hcx, hcy, _) in hardhat_pts:
                        if x1 <= hcx <= x2 and head_t <= hcy <= head_b:
                            has_helmet = True
                            break
                    for (ncx, ncy, _) in no_hardhat_pts:
                        if x1 <= ncx <= x2 and head_t <= ncy <= head_b:
                            explicit_no_helmet = True
                            break
                    if explicit_no_helmet:
                        has_helmet = False

                # ── Vest: center-point matching ─────────────────────
                torso_t, torso_b = y1 + int(H * 0.15), y1 + int(H * 0.85)
                has_vest = False
                explicit_no_vest = False

                if ppe_model is not None:
                    for (vcx, vcy, _) in vest_pts:
                        if x1 <= vcx <= x2 and torso_t <= vcy <= torso_b:
                            has_vest = True
                            break
                    for (nvcx, nvcy, _) in no_vest_pts:
                        if x1 <= nvcx <= x2 and torso_t <= nvcy <= torso_b:
                            explicit_no_vest = True
                            break
                    if explicit_no_vest:
                        has_vest = False

                # ── Temporal smoothing ────────────────────────────────
                ph = ppe_history.setdefault(grid_key,
                                            {"helmet": [], "vest": []})
                ph["helmet"].append(has_helmet)
                ph["vest"].append(has_vest)
                ph["helmet"] = ph["helmet"][-PPE_WINDOW:]
                ph["vest"]   = ph["vest"][-PPE_WINDOW:]

                f_helmet = sum(ph["helmet"]) > len(ph["helmet"]) // 2
                f_vest   = sum(ph["vest"])   > len(ph["vest"])   // 2

                missing = []
                if not f_helmet:
                    missing.append("Helmet")
                if not f_vest:
                    missing.append("Vest")

                if missing:
                    violations += 1
                    col = (0, 0, 210)
                    lbl = "VIOLATION"
                    alerts.append(
                        f"⚠️ Worker #{workers} missing "
                        f"{' & '.join(missing)} [{det_conf:.0%}]")
                else:
                    col = (34, 197, 94)
                    lbl = "COMPLIANT"

            # ── Draw ─────────────────────────────────────────────────
            thick = 3 if fallen else 2
            cv2.rectangle(frame, (x1,y1), (x2,y2), col, thick)
            (tw, th2), _ = cv2.getTextSize(lbl, cv2.FONT_HERSHEY_SIMPLEX, .6, 2)
            cv2.rectangle(frame, (x1, y1-th2-12), (x1+tw+8, y1), col, -1)
            cv2.putText(frame, lbl, (x1+4, y1-5),
                        cv2.FONT_HERSHEY_SIMPLEX, .6, (255,255,255), 2)
            dbg = f"{det_conf:.0%}"
            cv2.putText(frame, dbg, (x1, y2+16),
                        cv2.FONT_HERSHEY_SIMPLEX, .38, col, 1)

        # ── Overlay ──────────────────────────────────────────────────
        mode = "ML PPE-Model" if ppe_model else "Disabled"
        info = f" H:{len(hardhat_pts)} V:{len(vest_pts)}" if ppe_model else ""
        cv2.putText(frame, f"{mode}{info}", (8, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 255, 200), 2)
        return frame, workers, violations, alerts

    return run


detector = get_detector(st.session_state.confidence)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    # ── Brand Header ──────────────────────────────
    st.markdown(f"""
    <div class="sb-brand">
        <div style="font-size:1.8rem;margin-bottom:6px">🦺</div>
        <div class="sb-brand-title">PPE Safety Monitor</div>
        <div class="sb-brand-sub">INDUSTRIAL AI · REAL-TIME DETECTION</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Navigation ────────────────────────────────
    st.markdown("<div class='sb-section'>Navigation</div>", unsafe_allow_html=True)
    nav = st.radio("nav", ["📊  Dashboard", "⚙️  Settings"],
                   label_visibility="collapsed", key="nav_radio")

    # ── System Status ─────────────────────────────
    st.markdown("<div class='sb-section'>System Status</div>", unsafe_allow_html=True)
    now = datetime.now()
    elapsed = now - st.session_state.session_start
    h, m, s = int(elapsed.seconds//3600), int((elapsed.seconds%3600)//60), int(elapsed.seconds%60)
    uptime_str = f"{h:02d}:{m:02d}:{s:02d}"

    live_dot = "<span class='sb-dot-green'></span>" if st.session_state.running else "<span class='sb-dot-red'></span>"
    live_label = "LIVE" if st.session_state.running else "OFFLINE"

    st.markdown(f"""
    <div class="sb-status-row">
        <span class="sb-status-label">Camera</span>
        <span class="sb-status-val">{live_dot}{live_label}</span>
    </div>
    <div class="sb-status-row">
        <span class="sb-status-label">Session Uptime</span>
        <span class="sb-status-val">{uptime_str}</span>
    </div>
    <div class="sb-status-row">
        <span class="sb-status-label">Source</span>
        <span class="sb-status-val">Camera #{st.session_state.cam_index}</span>
    </div>
    <div class="sb-status-row">
        <span class="sb-status-label">Confidence</span>
        <span class="sb-status-val">{st.session_state.confidence:.0%}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Session Summary ───────────────────────────
    st.markdown("<div class='sb-section'>Session Summary</div>", unsafe_allow_html=True)
    total_frames  = st.session_state.total_frames
    total_workers = st.session_state.total_workers
    total_viols   = st.session_state.total_viols
    sess_comp = 100 if total_workers == 0 else int(((total_workers - total_viols) / total_workers) * 100)

    st.markdown(f"""
    <div class="sb-mini-grid">
        <div class="sb-mini">
            <div class="sb-mini-val">{total_frames}</div>
            <div class="sb-mini-lbl">Frames</div>
        </div>
        <div class="sb-mini">
            <div class="sb-mini-val">{total_workers}</div>
            <div class="sb-mini-lbl">Workers</div>
        </div>
        <div class="sb-mini">
            <div class="sb-mini-val" style="color:{RED if total_viols>0 else GREEN}">{total_viols}</div>
            <div class="sb-mini-lbl">Violations</div>
        </div>
        <div class="sb-mini">
            <div class="sb-mini-val" style="color:{GREEN if sess_comp==100 else RED}">{sess_comp}%</div>
            <div class="sb-mini-lbl">Compliance</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── PPE Rules Active ─────────────────────────
    st.markdown("<div class='sb-section'>PPE Rules Active</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="ppe-rule"><span class="ppe-rule-icon">⛑️</span> Hard Hat / Helmet</div>
    <div class="ppe-rule"><span class="ppe-rule-icon">🦺</span> Safety Vest</div>
    <div class="ppe-rule"><span class="ppe-rule-icon">👤</span> Worker Detection</div>
    """, unsafe_allow_html=True)

    # ── Quick Actions ─────────────────────────────
    st.markdown("<div class='sb-section'>Quick Actions</div>", unsafe_allow_html=True)
    qa1, qa2 = st.columns(2)
    with qa1:
        if st.button("▶ Start" if not st.session_state.running else "⏹ Stop",
                     type="primary" if not st.session_state.running else "secondary",
                     use_container_width=True):
            st.session_state.running = not st.session_state.running
            if st.session_state.running:
                st.session_state.session_start = datetime.now()
            st.rerun()
    with qa2:
        if st.button("🗑 Clear", use_container_width=True):
            st.session_state.logs = []
            st.session_state.chart_data = pd.DataFrame(columns=["Time", "Workers", "Violations"])
            st.session_state.total_frames  = 0
            st.session_state.total_workers = 0
            st.session_state.total_viols   = 0
            st.rerun()

    # ── Appearance ───────────────────────────────
    st.markdown("<div class='sb-section'>Appearance</div>", unsafe_allow_html=True)
    dark = st.toggle("🌙  Dark Mode", value=st.session_state.dark_mode)
    if dark != st.session_state.dark_mode:
        st.session_state.dark_mode = dark
        st.rerun()

    # ── Footer ────────────────────────────────────
    st.markdown("""
    <div style='flex:1'></div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sb-footer">
        PPE Safety Monitor v2.0<br>
        {now.strftime('%a, %d %b %Y · %H:%M')}<br>
        Powered by YOLOv8 + OpenCV
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPER: KPI card HTML
# ─────────────────────────────────────────────
def kpi(icon, label, value, sub, accent):
    return f"""
    <div class="kpi-wrap">
      <div class="kpi-accent" style="background:{accent}"></div>
      <span class="kpi-icon">{icon}</span>
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-sub">{sub}</div>
    </div>"""

def sec(icon, title):
    return f'<div class="sec-head"><span>{icon}</span><span>{title}</span></div>'

# ═══════════════════════════════════════════════
# SETTINGS PAGE
# ═══════════════════════════════════════════════
if nav == "⚙️  Settings":
    st.markdown(f"<h2 style='color:{TEXT}'>⚙️ Settings</h2>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(f"<div class='s-card'>", unsafe_allow_html=True)
    st.subheader("🎯 Detection Sensitivity")
    new_conf = st.slider("Confidence threshold", 0.10, 0.90,
                         st.session_state.confidence, 0.05,
                         help="Higher = stricter. Lower = catches more people but may have false positives.")
    st.caption(f"Current: **{new_conf:.0%}** — {'Strict' if new_conf > .6 else 'Balanced' if new_conf > .35 else 'Sensitive'}")
    if new_conf != st.session_state.confidence:
        st.session_state.confidence = new_conf
        get_detector.clear()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='s-card'>", unsafe_allow_html=True)
    st.subheader("📷 Camera Source")
    cam = st.number_input("Camera index (0 = default webcam)", 0, 10, st.session_state.cam_index, 1)
    if cam != st.session_state.cam_index:
        st.session_state.cam_index = int(cam)
    st.caption("Change to 1, 2… if you have multiple cameras.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='s-card'>", unsafe_allow_html=True)
    st.subheader("📋 PPE Detection Logic")
    st.markdown(f"""
    <ul style='color:{TEXT2};line-height:2'>
    <li><b>Person detected</b> via YOLOv8 neural network</li>
    <li><b>Helmet check</b> — scans top 22% of person for hard-hat colours (white, yellow, orange, red, blue)</li>
    <li><b>Vest check</b> — scans torso for high-vis colours (neon yellow, orange, lime green)</li>
    <li>Violation triggered if <b>either item is absent</b></li>
    </ul>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='s-card'>", unsafe_allow_html=True)
    st.subheader("🗑️ Reset Data")
    if st.button("Clear Logs & Chart", type="secondary"):
        st.session_state.logs = []
        st.session_state.chart_data = pd.DataFrame(columns=["Time", "Workers", "Violations"])
        st.success("Cleared.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════
# DASHBOARD PAGE
# ═══════════════════════════════════════════════

# ── Top bar: title + status badge ──────────────
badge = ('<span class="badge-live">🟢 &nbsp;LIVE</span>'
         if st.session_state.running
         else '<span class="badge-offline">⏸ &nbsp;OFFLINE</span>')
col_t, col_b = st.columns([5, 1])
with col_t:
    st.markdown(f"<h1 style='color:{TEXT};margin-bottom:2px'>🦺 Safety Monitoring Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{TEXT2};font-size:.95rem;margin-bottom:0'>AI-Powered PPE Compliance · Real-Time Detection</p>", unsafe_allow_html=True)
with col_b:
    st.markdown(f"<div style='padding-top:18px;text-align:right'>{badge}</div>", unsafe_allow_html=True)

st.markdown("---")

# ── KPI Row ────────────────────────────────────
kpi_ph = st.empty()

def render_kpis(workers, violations, compliance):
    c1, c2, c3 = kpi_ph.columns(3)
    c1.markdown(kpi("👷", "Workers Detected", workers, "in current frame", BLUE), unsafe_allow_html=True)
    c2.markdown(kpi("⚠️", "Active Violations", violations, "missing PPE gear", RED), unsafe_allow_html=True)
    c3.markdown(kpi("✅", "Compliance Rate", f"{compliance}%",
                    "🟢 Safe" if compliance == 100 else "🔴 Action required", GREEN), unsafe_allow_html=True)

render_kpis(0, 0, 100)
st.markdown("<br>", unsafe_allow_html=True)

# ── Main row: feed | alerts ─────────────────────
feed_col, alert_col = st.columns([3, 1.4])

with feed_col:
    st.markdown(sec("📷", "Live Camera Feed"), unsafe_allow_html=True)
    feed_ph = st.empty()
    # camera controls
    b1, b2, b3 = st.columns([1, 1, 4])
    start_pressed = b1.button("▶ Start", type="primary",  use_container_width=True)
    stop_pressed  = b2.button("⏹ Stop",  type="secondary", use_container_width=True)
    if start_pressed:
        st.session_state.running = True
        st.rerun()
    if stop_pressed:
        st.session_state.running = False
        st.rerun()

with alert_col:
    st.markdown(sec("🚨", "Live Alerts"), unsafe_allow_html=True)
    alert_ph = st.empty()

# ── Bottom row: chart | log ─────────────────────
st.markdown("---")
chart_col, log_col = st.columns([2, 1.2])

with chart_col:
    st.markdown(sec("📈", "Violation Timeline"), unsafe_allow_html=True)
    chart_ph = st.empty()

with log_col:
    st.markdown(sec("📋", "Event Log"), unsafe_allow_html=True)
    log_ph = st.empty()

# ── Helpers ────────────────────────────────────
def render_alerts(alerts, workers):
    html = ""
    if alerts:
        for a in alerts:
            if "EMERGENCY" in a or "fallen" in a.lower():
                html += f'<div class="pill-fallen">🚨 {a}</div>'
            else:
                html += f'<div class="pill-danger">⚠️ {a}</div>'
    elif workers > 0:
        html += '<div class="pill-success">✅ All workers fully compliant</div>'
    else:
        html += '<div class="pill-idle">No workers detected in frame</div>'
    alert_ph.markdown(html, unsafe_allow_html=True)

def render_log():
    if not st.session_state.logs:
        log_ph.markdown('<div class="pill-idle">No events recorded yet</div>', unsafe_allow_html=True)
        return
    html = ""
    for entry in reversed(st.session_state.logs[-20:]):
        dot = "🔴" if entry["type"] == "violation" else "🟢"
        html += f'<div class="log-row"><span class="log-ts">{entry["time"]}</span>{dot} {entry["msg"]}</div>'
    log_ph.markdown(html, unsafe_allow_html=True)

def render_chart():
    df = st.session_state.chart_data
    if df.empty:
        chart_ph.markdown('<div class="pill-idle" style="height:180px">Chart data will appear once the camera starts</div>', unsafe_allow_html=True)
    else:
        chart_ph.area_chart(df.set_index("Time")[["Workers", "Violations"]])

# ── Initial offline state ──────────────────────
if not st.session_state.running:
    feed_ph.markdown('<div class="cam-offline">📷<br>Camera offline<br><small>Click ▶ Start to begin monitoring</small></div>', unsafe_allow_html=True)
    render_alerts([], 0)
    render_log()
    render_chart()

# ═══════════════════════════════════════════════
# LIVE CAMERA LOOP
# ═══════════════════════════════════════════════
if st.session_state.running:
    cap = cv2.VideoCapture(st.session_state.cam_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(st.session_state.cam_index)

    if not cap.isOpened():
        feed_ph.error("❌ Camera not found. Go to Settings → Camera Source and change the index.")
        st.session_state.running = False
        st.stop()

    last_chart = time.time()

    while st.session_state.running:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.1)
            continue

        processed, workers, violations, alerts = detector(frame)
        compliance = 100 if workers == 0 else int(((workers - violations) / workers) * 100)

        # Track cumulative session stats (shown in sidebar)
        st.session_state.total_frames  += 1
        st.session_state.total_workers += workers
        st.session_state.total_viols   += violations

        # Video feed
        feed_ph.image(cv2.cvtColor(processed, cv2.COLOR_BGR2RGB), channels="RGB", width="stretch")

        # KPI
        render_kpis(workers, violations, compliance)

        # Alerts
        render_alerts(alerts, workers)

        # Log — only append new violations (avoid log flood)
        ts = datetime.now().strftime("%H:%M:%S")
        for a in alerts:
            if not st.session_state.logs or st.session_state.logs[-1]["msg"] != a:
                st.session_state.logs.append({"time": ts, "msg": a, "type": "violation"})
        render_log()

        # Chart — throttle to 1 Hz
        if time.time() - last_chart >= 1.0:
            row = pd.DataFrame({"Time": [ts], "Workers": [workers], "Violations": [violations]})
            st.session_state.chart_data = pd.concat(
                [st.session_state.chart_data, row], ignore_index=True
            ).tail(50)
            render_chart()
            last_chart = time.time()

        time.sleep(0.03)

    cap.release()
