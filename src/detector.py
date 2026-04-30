import cv2
import numpy as np
from ultralytics import YOLO


class PPEDetector:
    """
    PPE Detection using YOLOv8 + OpenCV colour analysis.

    Strategy (hybrid – works with the generic yolov8n model):
      1. YOLO detects 'person' bounding boxes.
      2. For each person we crop the **head region** (top ~22 %) and analyse
         colours to decide if a hard-hat is present.
      3. We crop the **torso region** (middle 40 %) and look for high-vis
         vest colours (bright yellow / lime-green / orange).

    This gives much better results than the old hash-based simulation and
    works on a standard COCO-pretrained model without any fine-tuning.
    """

    # HSV ranges for common hard-hat colours
    HELMET_HSV_RANGES = [
        # White helmets
        {"lower": np.array([0, 0, 180]),   "upper": np.array([180, 50, 255])},
        # Yellow helmets
        {"lower": np.array([18, 80, 150]), "upper": np.array([35, 255, 255])},
        # Orange helmets
        {"lower": np.array([5, 100, 150]), "upper": np.array([18, 255, 255])},
        # Red helmets (low hue)
        {"lower": np.array([0, 100, 120]), "upper": np.array([5, 255, 255])},
        # Red helmets (high hue)
        {"lower": np.array([170, 100, 120]), "upper": np.array([180, 255, 255])},
        # Blue helmets
        {"lower": np.array([100, 80, 100]), "upper": np.array([130, 255, 255])},
    ]

    # HSV ranges for high-vis vest colours
    VEST_HSV_RANGES = [
        # Bright yellow / lime
        {"lower": np.array([18, 80, 140]),  "upper": np.array([42, 255, 255])},
        # Orange / fluorescent orange
        {"lower": np.array([5, 100, 150]),  "upper": np.array([18, 255, 255])},
        # Lime green
        {"lower": np.array([42, 60, 120]),  "upper": np.array([80, 255, 255])},
    ]

    # Minimum percentage of the cropped region that must match to count
    HELMET_THRESHOLD = 0.12  # 12 % of head region
    VEST_THRESHOLD   = 0.10  # 10 % of torso region

    def __init__(self, model_path: str = "yolov8n.pt",
                 confidence: float = 0.45):
        self.model = YOLO(model_path)
        self.confidence = confidence

    # ------------------------------------------------------------------
    # Colour helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _colour_ratio(hsv_crop, ranges) -> float:
        """Return the fraction of pixels that fall inside *any* of the given HSV ranges."""
        if hsv_crop.size == 0:
            return 0.0
        combined_mask = np.zeros(hsv_crop.shape[:2], dtype=np.uint8)
        for r in ranges:
            mask = cv2.inRange(hsv_crop, r["lower"], r["upper"])
            combined_mask = cv2.bitwise_or(combined_mask, mask)
        return np.count_nonzero(combined_mask) / combined_mask.size

    def _has_helmet(self, frame_hsv, x1, y1, x2, y2) -> bool:
        head_h = int((y2 - y1) * 0.22)
        head_crop = frame_hsv[max(y1 - head_h // 2, 0): y1 + head_h, x1:x2]
        return self._colour_ratio(head_crop, self.HELMET_HSV_RANGES) >= self.HELMET_THRESHOLD

    def _has_vest(self, frame_hsv, x1, y1, x2, y2) -> bool:
        h = y2 - y1
        torso_top = y1 + int(h * 0.20)
        torso_bot = y1 + int(h * 0.60)
        torso_crop = frame_hsv[torso_top:torso_bot, x1:x2]
        return self._colour_ratio(torso_crop, self.VEST_HSV_RANGES) >= self.VEST_THRESHOLD

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------
    def process_frame(self, frame):
        """
        Run detection on a single BGR frame.

        Returns
        -------
        annotated_frame, total_persons, violations, alert_messages
        """
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        results = self.model(frame, stream=True, verbose=False, conf=self.confidence)

        total_persons = 0
        violations = 0
        alert_messages: list[str] = []

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])

                if cls != 0:  # only 'person'
                    continue
                total_persons += 1
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                helmet = self._has_helmet(frame_hsv, x1, y1, x2, y2)
                vest   = self._has_vest(frame_hsv, x1, y1, x2, y2)

                missing = []
                if not helmet:
                    missing.append("Helmet")
                if not vest:
                    missing.append("Safety Vest")

                if missing:
                    violations += 1
                    colour = (0, 0, 220)   # red
                    label = "VIOLATION"
                    alert_messages.append(
                        f"⚠️ Worker #{total_persons} – Missing: {' & '.join(missing)}"
                    )
                else:
                    colour = (0, 200, 0)   # green
                    label = "COMPLIANT"

                # --- Draw ---
                cv2.rectangle(frame, (x1, y1), (x2, y2), colour, 2)
                # Label background
                (tw, th), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2
                )
                cv2.rectangle(
                    frame, (x1, y1 - th - 10), (x1 + tw + 6, y1), colour, -1
                )
                cv2.putText(
                    frame, label, (x1 + 3, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2,
                )

                # Confidence text below box
                conf_text = f"{conf:.0%}"
                cv2.putText(
                    frame, conf_text, (x1, y2 + 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, colour, 1,
                )

        return frame, total_persons, violations, alert_messages
