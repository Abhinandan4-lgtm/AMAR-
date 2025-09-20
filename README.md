AMAR - AI Med Assistance Robot
AMAR is a smart, AI-powered system designed to ensure medication adherence, enhance patient safety, and provide real-time peace of mind for guardians and caregivers.

This project integrates a physical dispensing robot controlled by a Raspberry Pi with a professional web-based dashboard. It addresses the critical challenges of medication non-adherence, delayed emergency responses, and the need for remote patient monitoring in a single, cohesive solution.

✨ Key Features
Automated & Reliable Dispensing: A dual-servo motor mechanism accurately dispenses pills from multiple compartments based on a remotely managed schedule.

Professional Web Dashboard: A clean, responsive, and intuitive web interface for guardians to manage schedules, monitor adherence, and view activity logs.

Instant Emergency Alerts: A one-touch physical button on the device triggers immediate SMS and voice call alerts to a guardian via a dedicated GSM module.

Live Video Monitoring: During an emergency, caregivers can view a live, low-latency video stream from the Pi Camera directly on the web dashboard.

AI-Powered Assistance (Gemini API):

AI Assistant: Ask questions about medications and wellness.

Log Analysis: Get AI-driven insights into adherence patterns.

Schedule Summaries: Generate easy-to-read summaries of complex schedules.

Real-Time Two-Way Communication: A robust WebSocket connection ensures the hardware and web dashboard are always perfectly in sync, providing instant updates.

🚀 Live Demo & Visuals
Here's a look at the AMAR system in action, showcasing the professional guardian dashboard and the physical hardware prototype.

Guardian Web Dashboard:

AMAR Hardware Prototype:

🛠️ Technology Stack
Category

Technologies Used

Hardware

Raspberry Pi 4, Servo Motors, Pi Camera, SIM800L GSM Module

Backend

Python, Flask, Flask-SocketIO, APScheduler

Frontend

HTML5, CSS3, JavaScript, Bootstrap

Communication

REST API, WebSockets

AI Services

Google Gemini API

Libraries

gpiozero, pyserial, opencv-python-headless, Chart.js

📂 Setup and Installation Guide
This guide provides the steps to set up the software on your Raspberry Pi to run the AMAR backend server.

1. Initial Raspberry Pi Configuration
Install Raspberry Pi OS: Start with a fresh installation of Raspberry Pi OS (formerly Raspbian) Lite (for servers) or with Desktop.

Enable Interfaces: Run sudo raspi-config in the terminal and enable the following interfaces:

SSH: For remote access.

I2C: If you have I2C sensors.

Serial Port: Crucial for the GSM module. Ensure the login shell over serial is disabled and the serial port hardware is enabled.

Camera: Enable the legacy camera interface if using a Pi Camera module.

Update System: Run the following commands to make sure your system is up to date:

sudo apt update
sudo apt full-upgrade

2. Hardware Wiring (GPIO Pins)
Connect your components to the Raspberry Pi's GPIO pins. The Python code (hardware_controller.py) is configured for these pins. If you use different pins, you must update the code.

Rotation Servo: GPIO 17

Dispense Servo: GPIO 27

Emergency Button: GPIO 2 (and a ground pin)

SIM800L GSM Module:

VCC to Pi 5V

GND to Pi GND

TXD to Pi RXD (GPIO 15)

RXD to Pi TXD (GPIO 14)

3. Software Installation
Clone/Copy Files: Transfer all project files (Python backend and HTML/CSS/JS frontend) into a new directory on your Pi (e.g., /home/pi/amar_robot).

Install Dependencies: Open a terminal, navigate to your project directory, and install all the required Python libraries using pip.

cd /home/pi/amar_robot
sudo apt install python3-pip
pip install -r requirements.txt

Note: opencv-python-headless can take some time to install.

4. Running the Server
Navigate to Directory: Make sure you are in the amar_robot directory in your terminal.

Run the Main Application: Execute the main Python script. Using sudo is often necessary for GPIO access.

sudo python3 app.py

Check the Output: You should see log messages indicating that the server has started, the hardware has been initialized, and it is listening on port 5000.

5. Connecting the Web App
Find Your Pi's IP Address: In the Pi's terminal, type hostname -I. This will give you its local IP address (e.g., 192.168.1.XX).

Update script.js: In your script.js file, update the API and WebSocket URLs to point to your Pi's IP address.

Access the UI: Open the index.html file on a computer connected to the same Wi-Fi network as your Raspberry Pi. The web interface should now be able to communicate with the AMAR device.

📈 Future Work
Conducting clinical trials with real patients and caregivers to gather feedback.

Integration of more health sensors (e.g., heart rate, temperature) for comprehensive vitals monitoring.

Miniaturization of the hardware for a sleeker, more commercially viable design.

Developing a dedicated mobile application for iOS and Android for enhanced notifications and accessibility.
