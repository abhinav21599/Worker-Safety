import cv2
import numpy as np
import os
from ultralytics import YOLO

class WorkerSafetyDetector:
    """
    Advanced Worker Safety Detector featuring:
    1. Pose-based Fall Detection (Advanced Angle Analysis)
    2. Deep Learning PPE Detection (Vest & Helmet)
    3. Hybrid HSV Color Analysis (Fallback)
    """

    def __init__(self, conf=0.35):
        self.conf = conf
        # Load models with optimization
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Determine device
        import torch
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.half = self.device == 'cuda'
        
        # 1. Pose Model (Fall Detection)
        self.pose_model = YOLO(os.path.join(root, "yolov8n-pose.pt")).to(self.device)
        if self.half: self.pose_model.half()
        
        # 2. PPE model priority: amirt > hardhat > yolov8n (hybrid)
        self.ppe_model = None
        for p_name in ["ppe_amirt.pt", "ppe_hardhat.pt"]:
            p = os.path.join(root, p_name)
            if os.path.exists(p):
                try:
                    self.ppe_model = YOLO(p).to(self.device)
                    if self.half: self.ppe_model.half()
                    print(f"✅ Loaded PPE Model: {p} on {self.device}")
                    break
                except Exception as e:
                    print(f"❌ Failed to load {p}: {e}")
                    continue
        
        # State tracking for temporal smoothing
        self.person_states = {}  # {track_id: {"ppe": {"helmet": [], "vest": []}}}
        
        self.FALL_CONFIRM_FRAMES = 5 # Faster detection for demo (approx 0.25s)
        self.PPE_WINDOW = 30 # Increased window for much better stability (approx 1-1.5s)
        self.DETECTION_COOLDOWN = 60 
        self.MOVE_THRESHOLD = 3 # Stricter movement threshold

    def _check_fall(self, keypoints, box_coords, state):
        """
        Robust Fall/Lying Down Detection:
        - Detects fall even with partial pose data.
        - Uses aspect ratio, torso angle, and vertical profile.
        - Improved sensitivity for various lying down postures.
        """
        bx1, by1, bx2, by2 = box_coords
        w, h = bx2 - bx1, by2 - by1
        aspect = w / max(h, 1)
        
        # 1. Extreme Horizontal Case: Almost certainly a fall/lying down
        if aspect > 1.4: # Lowered from 1.6 for faster detection of lying down
            return True

        # 2. Moderate Horizontal Case: Requires pose confirmation
        if aspect < 0.9: # Lowered from 1.05: Standing/sitting is strictly vertical
            return False
            
        try:
            if keypoints is None or len(keypoints) < 5: # Lowered from 17
                return aspect > 1.4 # Without enough pose, be slightly conservative
            
            # YOLO returns [0,0] if keypoint not detected
            def is_v(kp): return kp is not None and len(kp) >= 2 and kp[0] > 1 and kp[1] > 1

            # Keypoints
            nose = keypoints[0] if len(keypoints) > 0 else None
            ls, rs = keypoints[5] if len(keypoints) > 5 else None, keypoints[6] if len(keypoints) > 6 else None
            lh, rh = keypoints[11] if len(keypoints) > 11 else None, keypoints[12] if len(keypoints) > 12 else None
            la, ra = keypoints[15] if len(keypoints) > 15 else None, keypoints[16] if len(keypoints) > 16 else None
            
            # Torso Angle Logic (from vertical)
            sh_pts = [p for p in [ls, rs] if is_v(p)]
            hp_pts = [p for p in [lh, rh] if is_v(p)]
            
            angle = 0
            if sh_pts and hp_pts:
                mid_sh = np.mean(sh_pts, axis=0)
                mid_hp = np.mean(hp_pts, axis=0)
                dx, dy = mid_sh[0] - mid_hp[0], mid_sh[1] - mid_hp[1]
                angle = np.degrees(np.arctan2(abs(dx), max(abs(dy), 1)))

            # Vertical Profile: Lying down means nose, hips, and ankles are at similar Y
            y_diff_nose_hip = 1000
            if is_v(nose) and hp_pts:
                mid_hp_y = np.mean(hp_pts, axis=0)[1]
                y_diff_nose_hip = abs(nose[1] - mid_hp_y)
            
            y_diff_nose_ankle = 1000
            ak_pts = [p for p in [la, ra] if is_v(p)]
            if is_v(nose) and ak_pts:
                mid_ak_y = np.mean(ak_pts, axis=0)[1]
                y_diff_nose_ankle = abs(nose[1] - mid_ak_y)

            # Balanced Fallen Criteria:
            is_tilted = angle > 40 # Lowered from 45
            is_flat = y_diff_nose_hip < (h * 0.7) or y_diff_nose_ankle < (h * 0.7) # Relaxed from 0.6
            
            # Higher sensitivity if aspect ratio is already high
            if aspect > 1.2:
                return is_tilted or is_flat or (angle > 30)
            
            return aspect > 0.9 and is_tilted and is_flat
            
        except Exception:
            return aspect > 1.4

    def _check_ppe_color(self, roi, item_type):
        if roi is None or roi.size == 0: return False
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        if item_type == "helmet":
            # 1. Yellow Helmets
            mask_yellow = cv2.inRange(hsv, (15, 100, 100), (35, 255, 255))
            # 2. White Helmets (High brightness, low saturation)
            mask_white  = cv2.inRange(hsv, (0, 0, 200), (180, 40, 255))
            # 3. Orange/Red Helmets
            mask_orange = cv2.inRange(hsv, (5, 100, 100), (15, 255, 255))
            mask_red1   = cv2.inRange(hsv, (0, 100, 100), (5, 255, 255))
            mask_red2   = cv2.inRange(hsv, (160, 100, 100), (180, 255, 255))
            # 4. Green Helmets (Safety Green)
            mask_green  = cv2.inRange(hsv, (35, 80, 80), (85, 255, 255))
            # 5. Blue Helmets (Engineering/Safety Blue)
            mask_blue   = cv2.inRange(hsv, (100, 100, 100), (130, 255, 255))
            
            mask = cv2.bitwise_or(mask_yellow, mask_white)
            mask = cv2.bitwise_or(mask, mask_orange)
            mask = cv2.bitwise_or(mask, mask_red1)
            mask = cv2.bitwise_or(mask, mask_red2)
            mask = cv2.bitwise_or(mask, mask_green)
            mask = cv2.bitwise_or(mask, mask_blue)
        else: # vest (High-vis green/yellow or Orange)
            # 1. Neon Green / High-Vis Yellow Vests (Widened range)
            mask_neon   = cv2.inRange(hsv, (20, 50, 50), (95, 255, 255))
            # 2. High-Vis Orange Vests (Widened range)
            mask_orange = cv2.inRange(hsv, (0, 50, 50), (25, 255, 255))
            mask_red_v  = cv2.inRange(hsv, (160, 50, 50), (180, 255, 255))
            mask = cv2.bitwise_or(mask_neon, mask_orange)
            mask = cv2.bitwise_or(mask, mask_red_v)

        ratio = np.sum(mask > 0) / max(mask.size, 1)
        # Lowered from 0.18 to 0.12 for better sensitivity in fallback mode
        return ratio > 0.12 # Optimized threshold for fallback detection stability

    def process_frame(self, frame):
        fH, fW = frame.shape[:2]
        results = self.pose_model.track(frame, persist=True, verbose=False, conf=self.conf, classes=[0])
        
        workers = 0
        violations = 0
        alerts = []
        fall_count = 0
        
        for r in results:
            if r.boxes is None or r.boxes.id is None: continue
            
            track_ids = r.boxes.id.int().cpu().tolist()
            xyxy = r.boxes.xyxy.int().cpu().tolist()
            kpts_all = r.keypoints.xy.cpu().numpy() if r.keypoints is not None else [None] * len(track_ids)
            
            for i, track_id in enumerate(track_ids):
                x1, y1, x2, y2 = xyxy[i]
                kpts = kpts_all[i]
                
                workers += 1
                
                if track_id not in self.person_states:
                    self.person_states[track_id] = {
                        "fall_frames": 0,
                        "ppe": {"helmet": [], "vest": []},
                        "alert_cooldown": 0,
                        "compliant_logged": False
                    }
                
                state = self.person_states[track_id]
                if state["alert_cooldown"] > 0:
                    state["alert_cooldown"] -= 1
                
                # 1. Fall Detection
                is_down = self._check_fall(kpts, (x1, y1, x2, y2), state)
                state["fall_frames"] = (state["fall_frames"] + 1) if is_down else max(0, state["fall_frames"] - 1)
                
                has_fallen = state["fall_frames"] >= self.FALL_CONFIRM_FRAMES
                
                if has_fallen:
                    fall_count += 1
                    violations += 1
                    color = (0, 130, 255) # Orange
                    label = f"ID:{track_id} FALLEN!"
                    if state["alert_cooldown"] == 0:
                        alerts.append(f"🚨 EMERGENCY: Worker ID {track_id} has fallen!")
                        state["alert_cooldown"] = self.DETECTION_COOLDOWN
                        state["compliant_logged"] = False
                else:
                    # 2. PPE Detection - Crop based
                    has_helmet = False
                    has_vest = False
                    
                    if self.ppe_model:
                        pad = 50 # Increased padding for better context and precision
                        cx1, cy1 = max(0, x1-pad), max(0, y1-pad)
                        cx2, cy2 = min(fW, x2+pad), min(fH, y2+pad)
                        crop = frame[cy1:cy2, cx1:cx2]
                        
                        if crop.size > 0:
                            # Lowered confidence from 0.8 to 0.4 for better sensitivity
                            # Increased imgsz from 160 to 320 for better detail recognition
                            p_res = self.ppe_model(crop, verbose=False, conf=0.4, imgsz=320, half=self.half)
                            for pr in p_res:
                                for pbox in pr.boxes:
                                    cls = self.ppe_model.names[int(pbox.cls[0])].lower()
                                    if "helmet" in cls or "hardhat" in cls: has_helmet = True
                                    if "vest" in cls: has_vest = True
                    
                    if not has_helmet or not has_vest:
                        # Improved ROI selection for color fallback
                        h_h = (y2-y1)//3
                        helmet_roi = frame[max(0, y1-20):y1+h_h, x1:x2] # Wider head ROI
                        vest_roi = frame[y1+h_h//2:y2-h_h, x1:x2] # Better torso ROI
                        if not has_helmet: has_helmet = self._check_ppe_color(helmet_roi, "helmet")
                        if not has_vest: has_vest = self._check_ppe_color(vest_roi, "vest")
                    
                    # Temporal smoothing with hysteresis for maximum stability
                    ph = state["ppe"]
                    ph["helmet"].append(has_helmet)
                    ph["vest"].append(has_vest)
                    ph["helmet"] = ph["helmet"][-self.PPE_WINDOW:]
                    ph["vest"] = ph["vest"][-self.PPE_WINDOW:]
                    
                    # Hysteresis Logic:
                    # To BECOME safe: Need >80% consistency (relaxed from 90%)
                    # To STAY safe: Need >65% consistency (relaxed from 75%)
                    was_safe = state.get("is_safe", False)
                    h_rate = sum(ph["helmet"]) / len(ph["helmet"])
                    v_rate = sum(ph["vest"]) / len(ph["vest"])
                    
                    if was_safe:
                        smooth_helmet = h_rate > 0.65
                        smooth_vest = v_rate > 0.65
                    else:
                        smooth_helmet = h_rate > 0.80
                        smooth_vest = v_rate > 0.80
                        
                    state["is_safe"] = smooth_helmet and smooth_vest
                    
                    missing = []
                    if not smooth_helmet: missing.append("Helmet")
                    if not smooth_vest: missing.append("Vest")
                    
                    if missing:
                        violations += 1
                        color = (0, 0, 220) # Red
                        # Specific missing item label
                        missing_label = " & ".join(missing)
                        label = f"ID:{track_id} NO {missing_label.upper()}"
                        if state["alert_cooldown"] == 0:
                            alerts.append(f"⚠️ Worker ID {track_id} missing: {missing_label}")
                            state["alert_cooldown"] = self.DETECTION_COOLDOWN
                            state["compliant_logged"] = False
                    else:
                        color = (0, 200, 0) # Green
                        label = f"ID:{track_id} SAFE"
                        if not state["compliant_logged"]:
                            alerts.append(f"✅ Worker ID {track_id} is now fully compliant")
                            state["compliant_logged"] = True
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2 if not has_fallen else 4)
                tw, th = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                cv2.rectangle(frame, (x1, y1-th-10), (x1+tw, y1), color, -1)
                cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

        return frame, workers, violations, alerts, fall_count
