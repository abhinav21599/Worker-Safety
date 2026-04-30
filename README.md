# 🛡️ Safety AI: Industrial Workforce Intelligence Platform

Safety AI is a state-of-the-art, real-time safety monitoring dashboard designed for industrial environments. Leveraging computer vision, pose estimation, and deep learning, it ensures worker safety by monitoring PPE compliance and detecting critical incidents like falls in high-stakes environments.

![Safety Dashboard](https://img.freepik.com/free-vector/industrial-safety-background-with-flat-design_23-2148158580.jpg?w=1000) *(Note: Application features a custom cinematic Glassmorphism UI)*

---

## 🚀 Key Features

### 1. **Advanced Detection Suite**
*   **Hardhat & Vest Monitoring:** Real-time verification of essential safety gear using custom-trained YOLOv8 models.
*   **Hybrid Analysis:** Intelligent fallback to HSV (Hue, Saturation, Value) color analysis when lighting or occlusion affects deep learning accuracy.
*   **Pose-Based Fall Detection:** Analyzes 17 keypoints per person to detect horizontal profiles, rapid height changes, and post-fall stasis.
*   **Temporal Smoothing:** A sophisticated hysteresis-based logic (90% consistency to mark as "Safe", 75% to maintain status) minimizes false positives from motion blur or brief occlusions.

### 2. **Cinematic Command Center**
*   **Glassmorphism UI:** A sleek, modern "Cyber-Industrial" interface featuring backdrop blurs, scanning laser animations, and responsive card layouts.
*   **Dynamic Background System:** Procedurally generated haze layers and radial gradients that react to system status.
*   **13 Specialized Modules:** A comprehensive suite of tools ranging from live surveillance to predictive neural forecasting.

### 3. **Real-time Intelligence**
*   **Incident Timeline:** A live-updating chronological log of every safety event, violation, and compliance resolution.
*   **Emergency Lockdown Protocol:** Automated visual alerts and "Emergency Scan" UI modes triggered upon detection of worker distress.
*   **Worker Analytics:** Integrated Plotly-powered charts for compliance trends and incident distribution.

---

## 🛰️ Modular Command Center

The dashboard is partitioned into specialized modules for comprehensive facility management:

| Module | Description |
| :--- | :--- |
| **Executive Dashboard** | High-level KPIs, predictive trends, and worker intelligence feed. |
| **Live Monitoring** | Real-time AI video processing with multi-mode surveillance overlays. |
| **Worker Intelligence** | Deep-dive profiles, risk scoring, and zone-specific tracking. |
| **Attendance Tracking** | Computer-vision assisted shift logging and PPE compliance scoring. |
| **Safety Analytics** | Historical data visualization and incident frequency mapping. |
| **Threat Detection** | Neural detection of environmental hazards (leaks, unauthorized access). |
| **Compliance Center** | Regulatory monitoring (e.g., OSHA 1910.132) and verification status. |
| **Restricted Zones** | Virtual geofencing and real-time breach detection. |
| **Predictive Insights** | AI-driven forecasting of risk levels based on environmental factors. |
| **System Control** | Hardware utilization tracking (GPU/VRAM) and AI model configuration. |

---

## 🛠️ Technical Architecture

### **Core Stack**
- **Frontend:** [Streamlit](https://streamlit.io/) with custom Vanilla CSS & CSS3 Animations.
- **Engine:** [PyTorch](https://pytorch.org/) & [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics).
- **Processing:** [OpenCV](https://opencv.org/) for multi-threaded video stream management.
- **Analytics:** [Plotly.js](https://plotly.com/) & [Pandas](https://pandas.pydata.org/).

### **Architecture Flow**
1.  **VideoStream (Threaded):** Capture frames in a dedicated background thread to prevent UI lag.
2.  **Inference Engine:** Process frames through a cascaded model pipe (Pose -> PPE -> HSV Fallback).
3.  **Hysteresis Processor:** Smoothes detections over a 30-frame window for stability.
4.  **UI Bridge:** Renders frames with custom CSS overlays and updates the global session state.

---

## 📦 Installation & Setup

### **Prerequisites**
- Python 3.9+
- NVIDIA GPU with CUDA 11.8+ (Recommended for >30 FPS)
- Web Camera or RTSP Stream URL

### **1. Environment Setup**
```bash
# Clone the repository
git clone <repository-url>
cd Worker-Safety

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Initialize Models**
Run the setup script to download the optimized weights for person detection and pose estimation:
```bash
python setup_models.py
```

### **4. Launch Platform**
```bash
# Windows Quick-Start
run.bat

# Manual Launch
streamlit run app.py
```

---

## ⚙️ Configuration

- **Themes:** Modify `src/config.py` to adjust colors, fonts, or background assets.
- **Detection Sensitivity:** Adjust `confidence` and `FALL_CONFIRM_FRAMES` in `src/detector.py` for specific environment noise levels.
- **Surveillance Modes:** Standard, Thermal (Simulated), Emergency Scan, and Worker Tracking modes can be toggled via the sidebar.

## 🛡️ Safety Compliance
Currently monitoring **OSHA Standard 1910.132** (Personal Protective Equipment) and related industrial safety guidelines.

---
*Developed for Industrial Workforce Safety Excellence. This project demonstrates the intersection of AI Ethics and Industrial Safety.*
