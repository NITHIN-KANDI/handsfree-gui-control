# 👁️ VISION-ALS: Low-Cost Eye-Gaze Control Interface

## 📘 Overview

**VISION-ALS** is a hardware-independent, computer-vision-based eye-gaze control system designed for hands-free interaction with graphical user interfaces. Built for accessibility and ease-of-use, it enables users to control the mouse pointer and interface elements using just their eye movements.

---

## 🚀 Key Features

- 👁️ Eye-gaze tracking using **MediaPipe Face Mesh**
- 🎯 9-point **calibration** interface with **PyQt5**
- 🖱️ **Dwell-time-based auto-clicking** (2-second focus triggers mouse click)
- 🧭 **Real-time cursor control** with **OpenCV + PyAutoGUI**
- ⚙️ **Smooth movement algorithm** for jitter-free tracking
- 🧩 Modular design with accessibility-first screens for:
  - Food
  - Water
  - Emergency requests

---

## 🧰 Technologies Used

- Python  
- MediaPipe (Face Mesh)  
- OpenCV  
- PyAutoGUI  
- PyQt5

---

## 📂 Project Structure
├── screens/ # Accessibility screens (Food, Water, Emergency)
├── calibration_data/ # Saved data for 9-point calibration
├── calibration_ui/ # PyQt5-based calibration interface
├── evaluation_summary/ # Results from system usability testing
├── gaze_tracker/ # Gaze detection logic and smoothing algorithm
├── main_interface/ # Main navigation and interaction screen
├── requirements.txt # Python dependencies
├── README.md # Project documentation

---

## 🖥️ How to Run

1. **Install dependencies**:
```bash
pip install -r requirements.txt
python calibration_ui.py
python main_interface.py
