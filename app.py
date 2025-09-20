# AMAR - AI Med Assistance Robot
# Main Server Application (app.py)
# This Flask application is the core of the AMAR device. It handles:
# - Serving the web interface (for development, though it's a separate app)
# - Providing a REST API for commands from the web UI.
# - Running a WebSocket server for real-time, bi-directional communication.
# - Integrating all hardware and software modules.

from flask import Flask, jsonify, request, Response
from flask_socketio import SocketIO
from flask_cors import CORS
import logging

# Import AMAR-specific modules
import hardware_controller as hw
import gsm_controller as gsm
import scheduler_manager as sm
from camera_stream import CameraStream

# --- INITIALIZATION ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app) # Enable Cross-Origin Resource Sharing for the web app
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize the camera stream
camera = CameraStream()

# --- CORE FUNCTIONS ---
def trigger_dispense(schedule_id, compartment, pill_name):
    """
    The main function called by the scheduler to perform a dispense cycle.
    """
    logging.info(f"Scheduler triggered: Dispensing '{pill_name}' from compartment {compartment}.")
    
    # 1. Hardware Action: Dispense the pill
    hw.dispense_pill(int(compartment))
    
    # 2. Visual Confirmation (Placeholder)
    # In a real implementation, you would use OpenCV here to check the image from the camera
    pill_detected = True # Placeholder
    logging.info(f"Pill dispensed, visual confirmation: {pill_detected}")

    # 3. Real-time Update to Web UI
    # Emit a WebSocket event to all connected clients
    socketio.emit('update', {
        'event': 'dispense_success',
        'schedule_id': schedule_id,
        'compartment': compartment,
        'pill_name': pill_name,
        'timestamp': sm.get_current_time_str()
    })
    
    # 4. Guardian Alert (if not taken in time - to be implemented with sensors)
    # This is a placeholder for future functionality
    logging.info("Dispense cycle complete.")

def emergency_callback(channel):
    """
    Callback function executed when the physical emergency button is pressed.
    """
    logging.warning("EMERGENCY BUTTON PRESSED!")
    
    # 1. Emit WebSocket event to immediately alert the web UI
    socketio.emit('emergency', {'timestamp': sm.get_current_time_str()})
    
    # 2. Use GSM to send SMS and make a call
    guardian_phone = "+1234567890"  # IMPORTANT: Replace with the actual guardian's number
    gsm.send_sms(guardian_phone, "Emergency button on AMAR device has been pressed!")
    gsm.make_call(guardian_phone)

# --- REST API ENDPOINTS ---
# These are called by the web application to send commands to the Pi.

@app.route('/api/schedule', methods=['POST'])
def add_schedule():
    """
    API endpoint to add a new medication schedule.
    Receives JSON data from the web UI.
    """
    data = request.json
    logging.info(f"Received new schedule via API: {data}")
    
    if not all(k in data for k in ['name', 'time', 'compartment']):
        return jsonify({'status': 'error', 'message': 'Missing data'}), 400
        
    # Add the job to the scheduler
    sm.add_dispense_job(
        schedule_id=data.get('id', sm.get_current_time_str()), # Use provided ID or generate one
        compartment=data['compartment'],
        pill_name=data['name'],
        time_str=data['time'],
        callback=trigger_dispense
    )
    
    return jsonify({'status': 'success', 'message': 'Schedule added'})

@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    """API endpoint to get the list of current schedules."""
    return jsonify(sm.get_all_jobs())

@app.route('/api/dispense/manual', methods=['POST'])
def manual_dispense():
    """API endpoint for immediate manual dispensing from the web UI."""
    data = request.json
    compartment = data.get('compartment')
    logging.info(f"Manual dispense triggered for compartment {compartment} via API.")
    
    if not compartment:
        return jsonify({'status': 'error', 'message': 'Compartment not specified'}), 400

    # We run this in a separate thread to avoid blocking the API response
    socketio.start_background_task(trigger_dispense, 'manual', compartment, 'Manual Dispense')
    
    return jsonify({'status': 'success', 'message': 'Manual dispense initiated'})

# --- VIDEO STREAMING ---

def gen(camera_stream):
    """Video streaming generator function."""
    while True:
        frame = camera_stream.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# --- WEBSOCKET EVENTS ---
# For real-time communication between Pi and web UI.

@socketio.on('connect')
def handle_connect():
    logging.info('Web client connected to WebSocket.')

@socketio.on('disconnect')
def handle_disconnect():
    logging.info('Web client disconnected from WebSocket.')
    
# --- MAIN EXECUTION ---
if __name__ == '__main__':
    try:
        logging.info("Starting AMAR Server...")
        
        # Initialize hardware
        hw.setup_hardware(emergency_callback)
        
        # Start the scheduler
        sm.start_scheduler()
        
        # Run the Flask-SocketIO server
        # use host='0.0.0.0' to make it accessible on your network
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        logging.info("Shutting down AMAR Server.")
    finally:
        hw.cleanup()
        sm.stop_scheduler()
        camera.release() # Release camera resources
