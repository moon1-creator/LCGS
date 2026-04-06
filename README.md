# 🤖Live Co-ordinate Gesture-Controlled Bot

## 📌 Overview
This project showcases a gesture-controlled bot that interprets hand gestures to execute directional movements and perform shooting actions. The system uses computer vision to detect hand gestures and sends corresponding commands to an Pico W, which controls multiple servos for precise and responsive movements.

## 🎥 Demo Video

[![Watch Demo](https://img.youtube.com/vi/watch?v=c_3ePEDTMoI)](https://www.youtube.com/watch?v=c_3ePEDTMoI)

## 🚀 Features
- ✋ Real-time hand gesture recognition
- 🎯 Directional movement control (forward, backward, left, right)
- 🔫 Shooting action triggered by specific gestures
- ⚡ Low-latency communication between vision system and hardware
- 🎛️ Multi-servo control using Arduino

## 🧠 How It Works
1. A camera captures live video input.
2. The vision system processes frames to detect hand gestures.
3. Each gesture is mapped to a specific command.
4. Commands are transmitted to the Pico W over Wifi using HTTP.
5. Arduino controls servos to execute movement or shooting actions.

## 🛠️ Tech Stack
- **Computer Vision:** OpenCV / MediaPipe (or similar)
- **Programming Language:** Python 3.X (for gesture recognition) & MicroPython for Pico W
- **Hardware:** Raspberry Pi Pico
- **Communication:** Serial Communication (USB/UART) & Wifi
- **Actuators:** Servo Motors

## 🔌 Hardware Requirements
- Raspberry Pi Pico W
- Servo Motors
- USB Cable / Power Supply
- Camera (Webcam or Laptop Camera)

