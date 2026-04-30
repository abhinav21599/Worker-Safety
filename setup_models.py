import os
from ultralytics import YOLO

def setup():
    print("🚀 Initializing Worker-Safety Model Suite...")
    
    # 1. Base Detection Model (Person)
    print("\n📦 Fetching YOLOv8n (Base)...")
    YOLO("yolov8n.pt")
    
    # 2. Pose Model (Fall Detection)
    print("\n📦 Fetching YOLOv8n-Pose (Fall Detection)...")
    YOLO("yolov8n-pose.pt")
    
    # 3. Check for existing PPE models
    ppe_models = ["ppe_amirt.pt", "ppe_hardhat.pt"]
    found = [m for m in ppe_models if os.path.exists(m)]
    
    if found:
        print(f"\n✅ Found local PPE models: {found}")
    else:
        print("\n⚠️ No local PPE models found. The system will use hybrid HSV detection as fallback.")
        print("💡 Tip: Place 'ppe_amirt.pt' in this directory for better accuracy.")

    print("\n✨ Setup Complete! You can now run 'streamlit run app.py'")

if __name__ == "__main__":
    setup()
