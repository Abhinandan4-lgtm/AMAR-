# AMAR - AI Med Assistance Robot
# Hardware Control Module (hardware_controller.py)
# This module abstracts all direct interactions with the GPIO pins.

from gpiozero import Servo, Button
from time import sleep
import logging

# --- CONFIGURATION ---
# IMPORTANT: Adjust these GPIO pin numbers based on your actual wiring.
ROTATION_SERVO_PIN = 17  # Servo for rotating the pill carousel
DISPENSE_SERVO_PIN = 27  # Servo for pushing the pill out
EMERGENCY_BUTTON_PIN = 2  # Physical button for emergency alerts

# Servo positions (adjust these values via calibration)
# A value of -1 is full left, 0 is middle, 1 is full right.
DISPENSE_GATE_CLOSED = -0.9
DISPENSE_GATE_OPEN = 0

# --- INITIALIZATION ---
try:
    # Use with_fixed_pulses=True for more standard servo behavior if needed
    rotation_servo = Servo(ROTATION_SERVO_PIN)
    dispense_servo = Servo(DISPENSE_SERVO_PIN)
    emergency_button = Button(EMERGENCY_BUTTON_PIN, pull_up=True) # Assuming button connects GPIO to GND
except Exception as e:
    logging.error(f"Failed to initialize GPIO components: {e}. Is the GPIO library installed and are pins correct?")
    # Create dummy objects if running on a non-Pi machine for testing
    class DummyServo:
        def value(self, v): pass
    class DummyButton:
        when_pressed = None
    rotation_servo = DummyServo()
    dispense_servo = DummyServo()
    emergency_button = DummyButton()


def setup_hardware(emergency_callback_func):
    """
    Initializes hardware components and sets up callbacks.
    """
    logging.info("Setting up hardware...")
    
    # Set initial servo positions
    dispense_servo.value = DISPENSE_GATE_CLOSED
    rotation_servo.min() # Start at the 'home' position
    sleep(1)
    rotation_servo.detach() # Detach to prevent jitter
    
    # Assign the callback function to the button press event
    emergency_button.when_pressed = emergency_callback_func
    logging.info("Hardware setup complete. Emergency button is active.")

def rotate_to_compartment(compartment_number):
    """
    Rotates the carousel to the specified compartment number (1-7).
    This requires calibration to map numbers to servo angles.
    """
    # This is a placeholder mapping. You MUST calibrate this for your specific setup.
    # The angle (value between -1 and 1) will depend on your servo and mechanism.
    compartment_map = {
        1: -1.0,   # Position for compartment 1
        2: -0.66,  # Position for compartment 2
        3: -0.33,
        4: 0.0,
        5: 0.33,
        6: 0.66,
        7: 1.0,    # Position for compartment 7
    }
    
    target_position = compartment_map.get(compartment_number)
    
    if target_position is None:
        logging.error(f"Invalid compartment number: {compartment_number}")
        return

    logging.info(f"Rotating carousel to compartment {compartment_number}...")
    rotation_servo.value = target_position
    sleep(1.5) # Wait for the servo to reach the position
    rotation_servo.detach() # Detach to save power and prevent jitter
    logging.info("Rotation complete.")

def dispense_pill(compartment_number):
    """
    Executes a full dispense cycle: rotate, open gate, close gate.
    """
    logging.info(f"Starting dispense cycle for compartment {compartment_number}...")
    
    # 1. Rotate to the correct compartment
    rotate_to_compartment(compartment_number)
    
    # 2. Open the dispensing gate
    logging.info("Opening dispense gate...")
    dispense_servo.value = DISPENSE_GATE_OPEN
    sleep(1)
    
    # 3. Close the dispensing gate
    logging.info("Closing dispense gate...")
    dispense_servo.value = DISPENSE_GATE_CLOSED
    sleep(1)
    
    logging.info("Dispense hardware cycle finished.")

def cleanup():
    """
    Cleans up GPIO resources on script exit.
    """
    logging.info("Cleaning up GPIO resources.")
    if hasattr(rotation_servo, 'close'):
        rotation_servo.close()
    if hasattr(dispense_servo, 'close'):
        dispense_servo.close()
    if hasattr(emergency_button, 'close'):
        emergency_button.close()
