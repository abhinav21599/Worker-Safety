import cv2
import numpy as np
import os
from ultralytics import YOLO

class WorkerSafetyDetector:
    """
    V6-STABLE: Industrial Grade Detector
    1. Robust Fall Detection: Uses nose-to-hip vertical distance and body angle.
    2. Precision PPE: Model + Broad Color Check (White, Blue, Yellow, Orange, Green).
    3. Spatial ROI: Only checks colors in the dead-center of the head/torso.
    """

    def __init__(self, conf=0.35):
        self.conf = conf
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        import torch
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        self.pose_model = YOLO(os.path.join(root, "yolov8n-pose.pt")).to(self.device)
        self.ppe_model = None
        for p_name in ["ppe_amirt.pt", "ppe_hardhat.pt"]:
            p = os.path.join(root, p_name)
            if os.path.exists(p):
                try:
                    self.ppe_model = YOLO(p).to(self.device)
                    print(f"✅ PPE LOADED: {p_name}")
                    break
                except: continue
        
        self.person_states = {}
        self.FALL_CONFIRM_FRAMES = 6
        self.PPE_WINDOW = 12
        self.DETECTION_COOLDOWN = 60
        self.STARTUP_SILENCE = 15
        self.frame_count = 0

    def reset(self):
        """Reset all tracking states and counters."""
        self.person_states = {}
        self.frame_count = 0

    def _check_color_broad(self, roi, mode="vest"):
        if roi is None or roi.size == 0: return False
        # Use center 60% of ROI to avoid background bleed
        h, w = roi.shape[:2]
        roi = roi[int(h*0.2):int(h*0.8), int(w*0.2):int(w*0.8)]
        if roi.size == 0: return False
        
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        if mode == "vest":
            # Neon, Orange, Red (Common vest colors)
            m1 = cv2.inRange(hsv, (25, 60, 60), (85, 255, 255))  # Neon
            m2 = cv2.inRange(hsv, (0, 100, 100), (15, 255, 255)) # Orange/Red
            mask = cv2.bitwise_or(m1, m2)
            thresh = 0.15
        else: # helmet
            # Yellow, White, Blue, Orange
            m1 = cv2.inRange(hsv, (18, 50, 50), (35, 255, 255))  # Yellow
            m2 = cv2.inRange(hsv, (0, 0, 180), (180, 40, 255))   # White
            m3 = cv2.inRange(hsv, (100, 80, 80), (130, 255, 255)) # Blue
            mask = cv2.bitwise_or(cv2.bitwise_or(m1, m2), m3)
            thresh = 0.12
        
        return (np.sum(mask > 0) / mask.size) > thresh

    def _classify_ppe(self, name):
        n = name.lower()
        if "no" in n: return "no_h" if ("helmet" in n or "hardhat" in n) else "no_v"
        if "helmet" in n or "hardhat" in n: return "h"
        if "vest" in n: return "v"
        return "u"

    def _get_ppe_status(self, frame, p_boxes):
        if not self.ppe_model or not p_boxes: return {}
        res = self.ppe_model(frame, verbose=False, conf=0.25, imgsz=640)
        
        dets = []
        for r in res:
            for b in r.boxes:
                cat = self._classify_ppe(self.ppe_model.names[int(b.cls[0])])
                if cat != "u": dets.append({"c": cat, "conf": float(b.conf[0]), "b": b.xyxy[0].cpu().numpy()})

        results = {}
        for pid, (x1, y1, x2, y2) in p_boxes.items():
            h_s, h_n, v_s, v_n = 0.0, 0.0, 0.0, 0.0
            ph = max(y2 - y1, 1)
            
            for d in dets:
                db = d["b"]
                ix1, iy1, ix2, iy2 = max(x1, db[0]), max(y1, db[1]), min(x2, db[2]), min(y2, db[3])
                if ix1 < ix2 and iy1 < iy2:
                    cy = (db[1] + db[3]) / 2
                    if d["c"] in ("h", "no_h") and cy > (y1 + ph * 0.35): continue
                    if d["c"] in ("v", "no_v") and (cy < (y1 + ph * 0.15) or cy > (y1 + ph * 0.8)): continue
                    if d["c"] == "h": h_s = max(h_s, d["conf"])
                    elif d["c"] == "no_h": h_n = max(h_n, d["conf"])
                    elif d["c"] == "v": v_s = max(v_s, d["conf"])
                    elif d["c"] == "no_v": v_n = max(v_n, d["conf"])
            
            h_roi = frame[max(0,y1):min(frame.shape[0],y1+int(ph*0.3)), max(0,x1):min(frame.shape[1],x2)]
            v_roi = frame[max(0,y1+int(ph*0.2)):min(frame.shape[0],y1+int(ph*0.7)), max(0,x1):min(frame.shape[1],x2)]
            
            h_color = self._check_color_broad(h_roi, "helmet")
            v_color = self._check_color_broad(v_roi, "vest")
            
            # SAFE only if (Model says yes AND Color confirms) OR (Model is VERY sure > 0.8)
            # This allows detection of non-standard colors if the model is certain.
            has_h = (h_s > 0.45 and h_s > h_n and h_color) or (h_s > 0.80)
            has_v = (v_s > 0.45 and v_s > v_n and v_color) or (v_s > 0.80)
            
            results[pid] = (has_h, has_v)
        return results

    def _check_fall(self, kpts, box, fH):
        x1, y1, x2, y2 = box
        w, h = x2 - x1, max(y2 - y1, 1)
        aspect = w / h
        if aspect < 1.2 or y1 < (fH * 0.1): return False
        try:
            if kpts is None or len(kpts) < 17: return aspect > 2.0
            def is_v(kp): return kp[0] > 1 and kp[1] > 1
            sh_pts = [kpts[i] for i in [5, 6] if is_v(kpts[i])]
            hp_pts = [kpts[i] for i in [11, 12] if is_v(kpts[i])]
            if sh_pts and hp_pts:
                mid_sh = np.mean(sh_pts, axis=0)
                mid_hp = np.mean(hp_pts, axis=0)
                dx, dy = abs(mid_sh[0] - mid_hp[0]), abs(mid_sh[1] - mid_hp[1])
                angle = np.degrees(np.arctan2(dx, max(dy, 1)))
                # A fall is horizontal aspect AND large body angle
                return aspect > 1.3 and angle > 55
            return aspect > 2.0
        except: return aspect > 2.0

    def process_frame(self, frame):
        self.frame_count += 1
        fH, fW = frame.shape[:2]
        res = self.pose_model.track(frame, persist=True, verbose=False, conf=self.conf, classes=[0])
        
        workers, violations, falls, alerts = 0, 0, 0, []
        p_boxes = {}
        for r in res:
            if r.boxes is None or r.boxes.id is None: continue
            ids, boxes = r.boxes.id.int().cpu().tolist(), r.boxes.xyxy.int().cpu().tolist()
            for i, tid in enumerate(ids): p_boxes[tid] = boxes[i]

        ppe_map = self._get_ppe_status(frame, p_boxes)

        for r in res:
            if r.boxes is None or r.boxes.id is None: continue
            ids, boxes = r.boxes.id.int().cpu().tolist(), r.boxes.xyxy.int().cpu().tolist()
            kpts_all = r.keypoints.xy.cpu().numpy() if r.keypoints is not None else [None] * len(ids)

            for i, tid in enumerate(ids):
                x1, y1, x2, y2 = boxes[i]
                workers += 1
                if tid not in self.person_states:
                    self.person_states[tid] = {"f": 0, "h": [], "v": [], "cd": 0, "safe": False}
                
                s = self.person_states[tid]
                if s["cd"] > 0: s["cd"] -= 1

                h_now, v_now = ppe_map.get(tid, (False, False))
                s["h"].append(h_now); s["v"].append(v_now)
                s["h"], s["v"] = s["h"][-self.PPE_WINDOW:], s["v"][-self.PPE_WINDOW:]
                
                # Compliance logic: must be consistent over the window
                h_ok, v_ok = (sum(s["h"])/len(s["h"]) >= 0.7), (sum(s["v"])/len(s["v"]) >= 0.7)
                safe = h_ok and v_ok

                fallen = self._check_fall(kpts_all[i], (x1,y1,x2,y2), fH)
                s["f"] = (s["f"] + 1) if fallen else max(0, s["f"] - 1)
                is_fallen = s["f"] >= self.FALL_CONFIRM_FRAMES

                if is_fallen:
                    falls += 1; violations += 1; color, label = (0, 130, 255), f"ID:{tid} FALLEN!"
                    if s["cd"] == 0: alerts.append(f"🚨 EMERGENCY: Worker {tid} fell!"); s["cd"] = 60
                elif not safe:
                    violations += 1; missing = []
                    if not h_ok: missing.append("Helmet")
                    if not v_ok: missing.append("Vest")
                    color, label = (0, 0, 220), f"ID:{tid} NO {' & '.join(missing).upper()}"
                    if s["cd"] == 0:
                        alerts.append(f"⚠️ Worker {tid} missing: {' & '.join(missing)}")
                        s["cd"] = 60; s["safe"] = False
                else:
                    color, label = (0, 200, 0), f"ID:{tid} SAFE"
                    if not s["safe"]: alerts.append(f"✅ Worker {tid} compliant"); s["safe"] = True

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        cv2.putText(frame, "V6-STABLE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        return frame, workers, violations, alerts, falls
