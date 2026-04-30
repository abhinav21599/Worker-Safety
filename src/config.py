# ==========================================
# THEME CONFIGURATION
# ==========================================

LIGHT_THEME = {
    "bg": "#F4F7FB",
    "card_bg": "rgba(255, 255, 255, 0.85)",
    "card_border": "rgba(255, 255, 255, 0.5)",
    "text_primary": "#0F172A",
    "text_secondary": "#475569",
    "text_muted": "#94A3B8",
    "primary": "#3B82F6",
    "success": "#10B981",
    "danger": "#EF4444",
    "warning": "#F59E0B",
    "divider": "rgba(0, 0, 0, 0.05)",
    "sidebar_bg": "linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%)",
    "input_bg": "#FFFFFF",
    "badge_bg": "linear-gradient(135deg, #10B981, #34D399)",
    "badge_text": "#FFFFFF",
    "badge_border": "transparent",
    "alert_danger_bg": "linear-gradient(135deg, #FEF2F2, #FEE2E2)",
    "alert_danger_text": "#B91C1C",
    "alert_danger_border": "#EF4444",
    "alert_success_bg": "linear-gradient(135deg, #ECFDF5, #D1FAE5)",
    "alert_success_text": "#047857",
    "alert_success_border": "#10B981",
    "metric_value": "#0F172A",
    "shadow": "20px 20px 60px #cfd2d5, -20px -20px 60px #ffffff",
    "card_shadow": "0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)",
    "hover_shadow": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
    "chart_color": "url(#colorGradient)",
    "offline_bg": "rgba(241, 245, 249, 0.7)",
}

DARK_THEME = {
    "bg": "#0B1120",
    "card_bg": "rgba(30, 41, 59, 0.75)",
    "card_border": "rgba(255, 255, 255, 0.05)",
    "text_primary": "#F8FAFC",
    "text_secondary": "#CBD5E1",
    "text_muted": "#64748B",
    "primary": "#60A5FA",
    "success": "#34D399",
    "danger": "#F87171",
    "warning": "#FBBF24",
    "divider": "rgba(255, 255, 255, 0.05)",
    "sidebar_bg": "linear-gradient(180deg, #0F172A 0%, #0B1120 100%)",
    "input_bg": "#0F172A",
    "badge_bg": "linear-gradient(135deg, #059669, #10B981)",
    "badge_text": "#FFFFFF",
    "badge_border": "transparent",
    "alert_danger_bg": "linear-gradient(135deg, #450A0A, #7F1D1D)",
    "alert_danger_text": "#FECACA",
    "alert_danger_border": "#EF4444",
    "alert_success_bg": "linear-gradient(135deg, #064E3B, #065F46)",
    "alert_success_text": "#A7F3D0",
    "alert_success_border": "#10B981",
    "metric_value": "#FFFFFF",
    "shadow": "20px 20px 60px #090e1b, -20px -20px 60px #0d1425",
    "card_shadow": "0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.4)",
    "hover_shadow": "0 25px 50px -12px rgba(0, 0, 0, 0.8)",
    "chart_color": "#F87171",
    "offline_bg": "rgba(15, 23, 42, 0.6)",
}


def get_css(theme: dict) -> str:
    """Generate the full CSS string based on the active theme dictionary."""
    t = theme
    return f"""
<style>
    /* ================================================
       GLOBAL / APP
       ================================================ */
    .stApp {{
        background-color: {t['bg']} !important;
        background-image: radial-gradient(circle at 15% 50%, rgba(59, 130, 246, 0.05), transparent 25%),
                          radial-gradient(circle at 85% 30%, rgba(16, 185, 129, 0.05), transparent 25%);
    }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: {t['sidebar_bg']} !important;
        border-right: 1px solid {t['card_border']} !important;
        backdrop-filter: blur(10px);
    }}
    section[data-testid="stSidebar"] * {{
        color: {t['text_primary']} !important;
    }}

    /* All Streamlit text elements */
    .stApp p, .stApp span, .stApp label, .stApp div {{
        color: {t['text_secondary']};
    }}
    .stApp h1, .stApp h2, .stApp h3 {{
        color: {t['text_primary']} !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    hr {{
        border-color: {t['divider']} !important;
    }}

    /* ================================================
       PREMIUM 3D CARDS
       ================================================ */
    .card {{
        background: {t['card_bg']};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 24px;
        box-shadow: {t['card_shadow']};
        margin-bottom: 24px;
        border: 1px solid {t['card_border']};
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }}
    .card::before {{
        content: '';
        position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        transform: rotate(45deg);
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.5s;
    }}
    .card:hover {{
        transform: translateY(-8px) scale(1.02);
        box-shadow: {t['hover_shadow']};
    }}
    .card:hover::before {{ opacity: 1; }}

    /* 3D Stat card specialization */
    .stat-card {{
        background: {t['card_bg']};
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 30px 24px;
        box-shadow: {t['card_shadow']};
        border: 1px solid {t['card_border']};
        text-align: center;
        transition: all 0.5s cubic-bezier(0.25, 0.8, 0.25, 1);
        position: relative;
        overflow: hidden;
        transform-style: preserve-3d;
        perspective: 1000px;
    }}
    .stat-card::before {{
        content: '';
        position: absolute; top: 0; left: 0; right: 0; bottom: 0;
        border-radius: 20px;
        padding: 4px;
        background: linear-gradient(135deg, transparent, rgba(255,255,255,0.2));
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events: none;
    }}
    .stat-card:hover {{
        transform: translateY(-10px) rotateX(5deg) rotateY(-5deg) scale(1.03);
        box-shadow: {t['hover_shadow']};
    }}
    
    /* Accents for Stat Cards */
    .stat-card .accent-bar {{
        position: absolute; top: 0; left: 0; right: 0; height: 6px;
        border-radius: 20px 20px 0 0;
        opacity: 0.9;
    }}
    .stat-card.blue .accent-bar  {{ background: linear-gradient(90deg, #3B82F6, #60A5FA, #93C5FD); }}
    .stat-card.red .accent-bar   {{ background: linear-gradient(90deg, #EF4444, #F87171, #FCA5A5); }}
    .stat-card.green .accent-bar {{ background: linear-gradient(90deg, #10B981, #34D399, #6EE7B7); }}

    .stat-label {{
        font-size: 0.9rem;
        font-weight: 800;
        color: {t['text_muted']};
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
        transform: translateZ(20px);
    }}
    .stat-value {{
        font-size: 3.2rem;
        font-weight: 900;
        color: {t['metric_value']};
        line-height: 1.1;
        margin-bottom: 4px;
        background: linear-gradient(to right, {t['metric_value']}, {t['primary']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        transform: translateZ(40px);
        text-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }}
    .stat-sub {{
        font-size: 0.85rem;
        color: {t['text_muted']};
        transform: translateZ(15px);
    }}

    /* ================================================
       ALERTS WITH 3D POP
       ================================================ */
    .alert-danger {{
        background: {t['alert_danger_bg']};
        color: {t['alert_danger_text']};
        border-left: 8px solid {t['alert_danger_border']};
        padding: 16px 20px;
        border-radius: 12px;
        margin-bottom: 12px;
        font-weight: 700;
        font-size: 1rem;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2);
        animation: bounceInRight 0.6s cubic-bezier(0.215, 0.61, 0.355, 1);
        transition: transform 0.2s;
    }}
    .alert-danger:hover {{ transform: scale(1.02); }}

    .alert-success {{
        background: {t['alert_success_bg']};
        color: {t['alert_success_text']};
        border-left: 8px solid {t['alert_success_border']};
        padding: 16px 20px;
        border-radius: 12px;
        margin-bottom: 12px;
        font-weight: 700;
        font-size: 1rem;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
        animation: bounceInRight 0.6s cubic-bezier(0.215, 0.61, 0.355, 1);
        transition: transform 0.2s;
    }}
    .alert-success:hover {{ transform: scale(1.02); }}

    /* ================================================
       HEADER STATUS BADGE (GLOWING)
       ================================================ */
    .status-badge {{
        background: {t['badge_bg']};
        color: {t['badge_text']};
        padding: 8px 22px;
        border-radius: 30px;
        font-weight: 800;
        font-size: 0.9rem;
        display: inline-block;
        border: 1px solid {t['badge_border']};
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.5);
        animation: pulse-glow 2s infinite;
        letter-spacing: 1px;
    }}
    .status-badge-offline {{
        background: {t['alert_danger_bg']};
        color: {t['alert_danger_text']};
        padding: 8px 22px;
        border-radius: 30px;
        font-weight: 800;
        font-size: 0.9rem;
        display: inline-block;
        border: 1px solid {t['alert_danger_border']};
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        letter-spacing: 1px;
    }}

    /* ================================================
       STREAMLIT METRIC OVERRIDES
       ================================================ */
    [data-testid="stMetricValue"] {{
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        color: {t['metric_value']} !important;
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: {t['text_muted']} !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}
    [data-testid="stMetricDelta"] {{ display: none; }}

    /* ================================================
       ANIMATIONS
       ================================================ */
    @keyframes bounceInRight {{
        0% {{ opacity: 0; transform: translate3d(3000px, 0, 0); }}
        60% {{ opacity: 1; transform: translate3d(-25px, 0, 0); }}
        75% {{ transform: translate3d(10px, 0, 0); }}
        90% {{ transform: translate3d(-5px, 0, 0); }}
        100% {{ transform: none; }}
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes pulse-glow {{
        0% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
        70% {{ box-shadow: 0 0 0 15px rgba(16, 185, 129, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
    }}

    /* Section titles */
    .section-title {{
        color: {t['text_primary']};
        font-weight: 800;
        font-size: 1.3rem;
        margin-bottom: 16px;
        display: inline-block;
        position: relative;
    }}
    .section-title::after {{
        content: '';
        position: absolute; width: 40px; height: 4px;
        background: {t['primary']};
        bottom: -6px; left: 0;
        border-radius: 2px;
    }}

    /* Offline placeholder */
    .offline-placeholder {{
        background: {t['offline_bg']};
        backdrop-filter: blur(8px);
        height: 400px;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: {t['text_muted']};
        font-size: 1.25rem;
        font-weight: 600;
        border: 2px dashed {t['card_border']};
        box-shadow: inset 0 0 20px rgba(0,0,0,0.05);
    }}

    /* Log entry */
    .log-entry {{
        background: {t['card_bg']};
        border: 1px solid {t['card_border']};
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
        font-size: 0.95rem;
        color: {t['text_secondary']};
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        animation: fadeIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        transition: transform 0.2s;
    }}
    .log-entry:hover {{
        transform: scale(1.02) translateX(5px);
        border-left: 4px solid {t['danger']};
    }}
    .log-time {{
        color: {t['text_muted']};
        font-size: 0.85rem;
        margin-right: 12px;
        font-weight: 600;
        background: {t['divider']};
        padding: 2px 8px;
        border-radius: 12px;
    }}

    /* Settings panel card */
    .settings-card {{
        background: {t['card_bg']};
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 32px;
        box-shadow: {t['card_shadow']};
        border: 1px solid {t['card_border']};
        margin-bottom: 24px;
        transition: all 0.3s;
    }}
    .settings-card:hover {{
        box-shadow: {t['hover_shadow']};
        transform: translateY(-5px);
    }}
</style>
"""


# ==========================================
# PAGE CONFIG
# ==========================================
PAGE_CONFIG = {
    "page_title": "Safety Monitoring Dashboard",
    "layout": "wide",
    "page_icon": "🛡️",
}
