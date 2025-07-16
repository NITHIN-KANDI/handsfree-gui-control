import sys
import json
import math
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPixmap, QPalette, QColor
from PyQt5.QtCore import Qt, QTimer
from gaze_tracker import GazeTracker

positions = {
    "Top-Left":     (0.0, 0.0, 'q'),
    "Top":          (0.5, 0.0, 'w'),
    "Top-Right":    (1.0, 0.0, 'e'),
    "Far-Left":     (0.0, 0.5, 'a'),
    "Center":       (0.5, 0.5, 'c'),
    "Far-Right":    (1.0, 0.5, 'd'),
    "Bottom-Left":  (0.0, 1.0, 'z'),
    "Bottom":       (0.5, 1.0, 's'),
    "Bottom-Right": (1.0, 1.0, 'x')
}

class CalibrationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gaze Calibration")
        self.setWindowState(Qt.WindowFullScreen)
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("white"))
        self.setPalette(palette)

        self.gaze_tracker = GazeTracker()
        self.labels = {}
        self.current_step = 0
        self.keys_map = list(positions.items())

        self.instruction_label = QLabel(self)
        self.instruction_label.setStyleSheet("font-size: 32px; color: black; background-color: white;")
        self.instruction_label.setAlignment(Qt.AlignCenter)

        self.init_ui()
        QTimer.singleShot(1000, self.show_next_marker)

    def init_ui(self):
        for name, (x_frac, y_frac, _) in positions.items():
            label = QLabel(self)
            pix = QPixmap("assets/dot.png").scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(pix)
            label.setFixedSize(80, 80)
            label.move(0, 0)
            label.setVisible(False)
            self.labels[name] = label
        self.resize_screen()

    def resize_screen(self):
        screen = QApplication.primaryScreen()
        size = screen.size()
        self.resize(size)
        self.instruction_label.setGeometry(0, self.height() - 100, self.width(), 50)

    def show_next_marker(self):
        if self.current_step >= len(self.keys_map):
            print("✅ Calibration Complete")
            self.instruction_label.setText("Calibration Complete! Starting tracking...")
            self.gaze_tracker.train()

            with open("calibration_data.json", "w") as f:
                json.dump(self.gaze_tracker.calibration_points, f, indent=4)

            print("📁 Calibration data saved to calibration_data.json")
            self.gaze_tracker.start_tracking()

            QTimer.singleShot(1000, self.run_evaluation)
            QTimer.singleShot(4000, self.close)
            return

        name, (x_frac, y_frac, key) = self.keys_map[self.current_step]
        label = self.labels[name]

        screen_w, screen_h = self.width(), self.height()
        dot_w, dot_h = label.width(), label.height()
        x = int(screen_w * x_frac - dot_w // 2)
        y = int(screen_h * y_frac - dot_h // 2)

        x = max(0, min(screen_w - dot_w, x))
        y = max(0, min(screen_h - dot_h, y))

        label.move(x, y)
        label.setVisible(True)

        self.instruction_label.setText(f"Look at '{name}' and press '{key.upper()}' to calibrate.")
        print(f"\n➡️  Step {self.current_step + 1}/{len(self.keys_map)}")
        print(f"   Look at '{name}' and press '{key.upper()}' to calibrate.")

    def keyPressEvent(self, event):
        if self.current_step >= len(self.keys_map):
            return

        key_char = event.text()
        expected_key = self.keys_map[self.current_step][1][2]

        if key_char == expected_key:
            name = self.keys_map[self.current_step][0]
            label = self.labels[name]

            print(f"\n📌 [Step {self.current_step + 1}/{len(self.keys_map)}] Calibrating '{name}'...")
            self.instruction_label.setText(f"Calibrating '{name}'... Please hold gaze.")

            features_before = len(self.gaze_tracker.calibration_data['features'])
            self.gaze_tracker.calibrate_point(name, key_char=key_char)
            features_after = len(self.gaze_tracker.calibration_data['features'])

            frames_captured = features_after - features_before
            dx, dy, w = self.gaze_tracker.calibration_points[name][2:]
            print(f"✅ '{name}' Calibrated\n   ⏺ Frames: {frames_captured}\n   ➤ Avg dx: {dx:.4f}\n   ➤ Avg dy: {dy:.4f}\n   ➤ Avg width: {w:.2f}px")

            label.setVisible(False)
            self.current_step += 1
            QTimer.singleShot(1000, self.show_next_marker)

    def run_evaluation(self):
        print("📊 Running Evaluation...")
        with open("calibration_data.json", "r") as f:
            calib = json.load(f)
    
        predicted, ground_truth = [], []
        screen_w, screen_h = self.width(), self.height()
    
        for name, values in calib.items():
            if len(values) != 5:
                print(f"⚠️ Skipping '{name}': invalid format")
                continue
    
            # Get relative screen position from calibration map
            if name not in positions:
                print(f"⚠️ '{name}' not found in positions map")
                continue
    
            x_frac, y_frac, _ = positions[name]
            gx = x_frac * screen_w
            gy = y_frac * screen_h
    
            dx = values[2]
            dy = values[3]
            w = values[4]
    
            px = gx + dx * w
            py = gy + dy * w
    
            predicted.append((px, py))
            ground_truth.append((gx, gy))
    
        if not predicted:
            print("❌ No valid predictions to evaluate.")
            return
    
        pred = np.array(predicted)
        gt = np.array(ground_truth)
        euclidean = np.linalg.norm(pred - gt, axis=1)
        mean_euc = np.mean(euclidean)
    
        def ang_err(p, g):
            p3 = np.array([p[0], p[1], 1])
            g3 = np.array([g[0], g[1], 1])
            cos = np.clip(np.dot(p3, g3) / (np.linalg.norm(p3) * np.linalg.norm(g3)), -1, 1)
            return math.degrees(math.acos(cos))
    
        angular = [ang_err(p, g) for p, g in zip(pred, gt)]
        mean_ang = np.mean(angular)
        thresholds = [20, 40, 60, 80, 100]
        accuracy = [(euclidean < t).sum() / len(euclidean) for t in thresholds]
    
        # --- Plots ---
        plt.hist(euclidean, bins=10)
        plt.title("Euclidean Distance Error")
        plt.xlabel("Distance (px)")
        plt.ylabel("Frequency")
        plt.savefig("distance_error_hist.png")
        plt.close()
    
        plt.hist(angular, bins=10)
        plt.title("Angular Error")
        plt.xlabel("Angle (degrees)")
        plt.ylabel("Frequency")
        plt.savefig("angular_error_hist.png")
        plt.close()
    
        plt.plot(thresholds, [a * 100 for a in accuracy], marker='o')
        plt.title("Accuracy @ Radius")
        plt.xlabel("Radius (px)")
        plt.ylabel("Accuracy (%)")
        plt.grid(True)
        plt.savefig("accuracy_vs_radius.png")
        plt.close()
    
        heatmap = np.zeros((screen_h, screen_w))
        for x, y in predicted:
            xi = min(screen_w - 1, max(0, int(x)))
            yi = min(screen_h - 1, max(0, int(y)))
            heatmap[yi, xi] += 1
    
        plt.figure(figsize=(10, 6))
        sns.heatmap(heatmap, cmap="Reds")
        plt.title("Gaze Heatmap (Predicted)")
        plt.axis("off")
        plt.savefig("gaze_heatmap.png")
        plt.close()
    
        pred_x, pred_y = zip(*predicted)
        gt_x, gt_y = zip(*ground_truth)
        plt.scatter(gt_x, gt_y, label="Ground Truth", color="green", s=100)
        plt.scatter(pred_x, pred_y, label="Predicted", color="red", s=80)
        plt.title("Ground Truth vs Predicted Gaze")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.legend()
        plt.savefig("gt_vs_pred_scatter.png")
        plt.close()
    
        summary = {
            "mean_euclidean_distance_px": round(mean_euc, 2),
            "mean_angular_error_deg": round(mean_ang, 2),
            "accuracy_thresholds_px": thresholds,
            "accuracy_percentages": [round(a * 100, 2) for a in accuracy]
        }
    
        with open("evaluation_summary.json", "w") as f:
            json.dump(summary, f, indent=4)
    
        print("✅ Evaluation complete. Results saved.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalibrationWindow()
    window.show()
    sys.exit(app.exec_())
