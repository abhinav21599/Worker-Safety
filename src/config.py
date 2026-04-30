import base64
import os

# Helper to load background
def load_bg_b64():
    try:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Prefer optimized background, fallback to original
        for name in ["bg_opt.png", "bg.png"]:
            path = os.path.join(root, "assets", name)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
        return ""
    except:
        return ""

BG_B64 = load_bg_b64()

# ==========================================
# THEME CONFIGURATION
# ==========================================

LIGHT_THEME = {
    "bg": "#f8fafc",
    "surface": "rgba(255, 255, 255, 0.9)",
    "surface2": "#f1f5f9",
    "border": "rgba(148, 163, 184, 0.2)",
    "text": "#0f172a",
    "text2": "#475569",
    "blue": "#0ea5e9",
    "green": "#10b981",
    "red": "#f43f5e",
    "amber": "#f59e0b",
    "purple": "#A855F7",
    "sidebar_bg": "#ffffff",
    "overlay": "rgba(248, 250, 252, 0.85)"
}

DARK_THEME = {
    "bg": "#020617",
    "surface": "rgba(15, 23, 42, 0.95)",
    "surface2": "rgba(30, 41, 59, 0.7)",
    "border": "rgba(56, 189, 248, 0.3)",
    "text": "#F8FAFC",
    "text2": "#94A3B8",
    "blue": "#38BDF8",
    "green": "#4ADE80",
    "red": "#FB7185",
    "amber": "#FBBF24",
    "purple": "#A855F7",
    "sidebar_bg": "#020617",
    "overlay": "rgba(2, 6, 23, 0.85)"
}

def get_css(theme: dict) -> str:
    t = theme
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

/* Hide Streamlit Default UI */
header, footer, .stDeployButton {{
    visibility: hidden;
    height: 0;
    display: none !important;
}}
[data-testid="stHeader"] {{
    display: none !important;
}}

/* Main App Container */
.stApp {{
    font-family: 'Outfit', sans-serif;
    background: transparent !important;
}}

/* Cinematic Background System */
.stApp::before {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: {t['bg']};
    background-image:
        radial-gradient(circle at 20% 30%, {t['blue']}22 0%, transparent 40%),
        radial-gradient(circle at 80% 70%, {t['purple']}11 0%, transparent 40%),
        linear-gradient(180deg, rgba(2, 6, 23, 0.4) 0%, rgba(2, 6, 23, 0.8) 100%),
        url('data:image/png;base64,{BG_B64}');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    z-index: -1;
}}

/* Haze Layer */
.stApp::after {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: radial-gradient(circle at 50% 50%, transparent 0%, {t['bg']} 90%);
    pointer-events: none;
    z-index: -1;
    opacity: 0.6;
    animation: fogPulse 20s infinite alternate ease-in-out;
}}

@keyframes fogPulse {{
    0% {{ opacity: 0.4; transform: scale(1); }}
    100% {{ opacity: 0.7; transform: scale(1.1); }}
}}

/* Layout Tweaks */
.block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 0.5rem !important;
    max-width: 96% !important;
}}

/* Glassmorphism Cards */
.glass-card, .kpi-wrap {{
    background: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(56, 189, 248, 0.2) !important;
    border-radius: 20px !important;
    padding: 18px !important;
    margin-bottom: 16px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
}}

.glass-card:hover {{
    transform: translateY(-8px) scale(1.02);
    border-color: rgba(56, 189, 248, 0.6) !important;
    box-shadow: 0 15px 45px 0 rgba(0, 0, 0, 0.9), 0 0 25px rgba(56, 189, 248, 0.2);
}}

/* Scanning Laser Effect */
.glass-card::after {{
    content: "";
    position: absolute;
    top: -100%;
    left: -100%;
    width: 300%;
    height: 300%;
    background: linear-gradient(
        45deg,
        transparent 45%,
        rgba(56, 189, 248, 0.05) 48%,
        rgba(56, 189, 248, 0.2) 50%,
        rgba(56, 189, 248, 0.05) 52%,
        transparent 55%
    );
    animation: scan-glow 6s infinite linear;
    pointer-events: none;
}}
@keyframes scan-glow {{
    0% {{ transform: translate(-30%, -30%) rotate(0deg); }}
    100% {{ transform: translate(30%, 30%) rotate(360deg); }}
}}
.sec-head {{
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 0.85rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.25em;
    color: #38BDF8 !important;
    margin-bottom: 20px;
    font-family: 'Space Grotesk', sans-serif;
    border-bottom: 1px solid rgba(56, 189, 248, 0.1);
    position: relative;
}}

.sec-head::after {{
    content: "";
    position: absolute;
    bottom: -1px;
    left: 0;
    width: 40px;
    height: 2px;
    background: #38BDF8;
    box-shadow: 0 0 10px #38BDF8;
}}
/* KPI Cards */
.kpi-wrap {{
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 140px !important;
    background: linear-gradient(135deg, {t['surface']}, {t['bg']}66) !important;
}}

.kpi-icon {{
    font-size: 2rem;
    margin-bottom: 6px;
    filter: drop-shadow(0 0 10px rgba(0,0,0,0.5));
    transition: transform 0.3s ease;
}}

.kpi-wrap:hover .kpi-icon {{
    transform: scale(1.2) rotate(5deg);
}}

.kpi-label {{
    font-size: 0.75rem;
    color: {t['text2']};
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 4px;
}}

.kpi-value {{
    font-size: 2.8rem;
    font-weight: 900;
    margin: 4px 0;
    font-family: 'Space Grotesk', sans-serif;
    line-height: 1;
    letter-spacing: -1px;
}}

.kpi-sub {{
    font-size: 0.75rem;
    color: {t['text2']};
    font-weight: 500;
    opacity: 0.7;
}}

/* KPI Status Colors */
.kpi-blue .kpi-value {{ color: {t['blue']}; text-shadow: 0 0 30px {t['blue']}55; }}
.kpi-red .kpi-value {{ color: {t['red']}; text-shadow: 0 0 30px {t['red']}55; }}
.kpi-green .kpi-value {{ color: {t['green']}; text-shadow: 0 0 30px {t['green']}55; }}
.kpi-purple .kpi-value {{ color: {t['purple']}; text-shadow: 0 0 30px {t['purple']}55; }}

/* Sidebar Styling */
[data-testid="stSidebar"] {{
    background-color: rgba(2, 6, 23, 0.8) !important;
    backdrop-filter: blur(20px);
    border-right: 1px solid {t['border']} !important;
}}

.sb-header {{
    background: linear-gradient(135deg, {t['bg']}, {t['blue']}33);
    padding: 40px 20px;
    text-align: center;
    border-bottom: 1px solid {t['border']};
    margin: -60px -20px 20px -20px;
    position: relative;
    overflow: hidden;
}}

.sb-header::after {{
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, {t['blue']}, transparent);
    animation: scanline 3s infinite;
}}

@keyframes scanline {{
    0% {{ transform: translateX(-100%); }}
    100% {{ transform: translateX(100%); }}
}}

.sb-logo {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.6rem;
    font-weight: 900;
    letter-spacing: 0.1em;
    color: white;
    text-shadow: 0 0 20px {t['blue']}88;
}}

/* Buttons */
.stButton > button {{
    border-radius: 12px !important;
    background: {t['surface2']} !important;
    border: 1px solid {t['border']} !important;
    color: {t['text']} !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    font-size: 0.8rem !important;
    padding: 0.6rem 1rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}}

.stButton > button:hover {{
    background: linear-gradient(90deg, {t['blue']}, {t['purple']}) !important;
    color: white !important;
    border-color: transparent !important;
    transform: translateY(-3px);
    box-shadow: 0 8px 24px {t['blue']}44;
}}

/* Alerts */
.pill-danger, .pill-success, .pill-idle, .pill-fallen {{
    padding: 16px 20px;
    border-radius: 16px;
    margin-bottom: 12px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 12px;
    border: 1px solid transparent;
    animation: alertSlide 0.5s ease-out;
    backdrop-filter: blur(10px);
}}

@keyframes alertSlide {{
    from {{ transform: translateX(20px); opacity: 0; }}
    to {{ transform: translateX(0); opacity: 1; }}
}}

.pill-danger {{ background: {t['red']}22; color: {t['red']}; border-color: {t['red']}44; box-shadow: 0 4px 15px {t['red']}22; }}
.pill-success {{ background: {t['green']}22; color: {t['green']}; border-color: {t['green']}44; box-shadow: 0 4px 15px {t['green']}22; }}
.pill-idle {{ background: rgba(148, 163, 184, 0.1); color: {t['text2']}; border-color: {t['border']}; opacity: 0.6; }}
.pill-fallen {{ 
    background: linear-gradient(90deg, {t['red']}, #ff8095); 
    color: white; 
    border-color: rgba(255,255,255,0.4);
    box-shadow: 0 10px 30px {t['red']}66;
    animation: criticalPulse 1.5s infinite;
}}

@keyframes criticalPulse {{
    0% {{ transform: scale(1); box-shadow: 0 0 20px {t['red']}66; }}
    50% {{ transform: scale(1.02); box-shadow: 0 0 40px {t['red']}aa; }}
    100% {{ transform: scale(1); box-shadow: 0 0 20px {t['red']}66; }}
}}

/* Logs */
.log-row {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 15px;
    border-bottom: 1px solid {t['border']}33;
    font-size: 0.85rem;
    color: {t['text']};
    animation: fadeIn 0.5s ease-in;
}}

.log-ts {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: {t['blue']};
    opacity: 0.8;
    background: {t['blue']}11;
    padding: 2px 6px;
    border-radius: 4px;
}}

/* Video Feed Overlay */
.feed-container {{
    border: 1px solid {t['border']};
    border-radius: 20px;
    overflow: hidden;
    background: #000;
    position: relative;
    box-shadow: 0 0 40px rgba(0,0,0,0.5);
}}

/* Sidebar Status & Metrics */
.sb-section {{
    font-size: 0.75rem;
    font-weight: 800;
    color: {t['blue']};
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin: 25px 0 12px 0;
    opacity: 0.9;
    font-family: 'Space Grotesk', sans-serif;
}}

.sb-status-row {{
    display: flex;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid {t['border']}33;
}}

.sb-status-label {{ font-size: 0.8rem; color: {t['text2']}; }}
.sb-status-val {{ font-size: 0.8rem; color: {t['text']}; font-weight: 700; }}

.sb-mini-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 15px;
}}

.sb-mini {{
    padding: 15px 10px;
    border-radius: 16px;
    background: {t['surface2']}44;
    border: 1px solid {t['border']};
    text-align: center;
    backdrop-filter: blur(5px);
    transition: all 0.3s ease;
}}

.sb-mini:hover {{
    background: {t['blue']}22;
    border-color: {t['blue']}66;
    transform: translateY(-2px);
}}

.sb-mini-val {{ 
    font-size: 1.4rem; 
    font-weight: 900; 
    color: {t['text']}; 
    font-family: 'Space Grotesk', sans-serif;
    line-height: 1;
}}

.sb-mini-lbl {{ 
    font-size: 0.6rem; 
    color: {t['text2']}; 
    text-transform: uppercase; 
    letter-spacing: 0.1em;
    margin-top: 4px;
    font-weight: 700;
}}

.sb-footer {{
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid {t['border']}33;
    font-size: 0.7rem;
    color: {t['text2']};
    text-align: center;
    opacity: 0.6;
}}

@keyframes fadeIn {{
    from {{ opacity: 0; }}
    to {{ opacity: 1; }}
}}
</style>
"""

PAGE_CONFIG = {
    "page_title": "Safety AI Dashboard",
    "layout": "wide",
    "page_icon": "🛡️",
}
