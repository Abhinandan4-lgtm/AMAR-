# AMAR - AI Med Assistance Robot
# GSM Module Controller (gsm_controller.py)
# Handles all serial communication with the SIM800L/SIM900 module.

import serial
import time
import logging

# --- CONFIGURATION ---
# The serial port your GSM module is connected to on the Raspberry Pi.
# It's often '/dev/ttyS0' for GPIO UART or '/dev/ttyUSB0' for USB-to-serial adapters.
SERIAL_PORT = "/dev/ttyS0" 
BAUD_RATE = 9600

# --- INITIALIZATION ---
ser = None
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    logging.info(f"GSM module connected on {SERIAL_PORT}")
except serial.SerialException as e:
    logging.error(f"Could not open serial port {SERIAL_PORT}: {e}")
    logging.warning("GSM functionality will be disabled.")

def send_at_command(command, expected_response="OK", timeout=2):
    """
    Sends an AT command to the GSM module and waits for a response.
    """
    if not ser or not ser.is_open:
        logging.error("Serial port not available. Cannot send AT command.")
        return False
        
    logging.info(f"Sending AT command: {command}")
    ser.write((command + '\r\n').encode())
    
    start_time = time.time()
    response = ""
    while time.time() - start_time < timeout:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line:
            response += line
            logging.debug(f"GSM Response line: {line}")
            if expected_response in line:
                logging.info(f"Expected response '{expected_response}' received.")
                return True
    
    logging.warning(f"Timeout waiting for '{expected_response}' for command '{command}'. Full response: {response}")
    return False

def send_sms(phone_number, message):
    """
    Sends an SMS message to the specified phone number.
    """
    logging.info(f"Attempting to send SMS to {phone_number}...")
    
    # Set to text mode
    if not send_at_command('AT+CMGF=1'):
        logging.error("Failed to set GSM to text mode.")
        return False
        
    # Set the recipient's phone number
    if not send_at_command(f'AT+CMGS="{phone_number}"', expected_response=">"):
        logging.error("Failed to issue send SMS command.")
        return False
    
    # Send the message content and Ctrl+Z to send
    logging.info(f"Sending message: {message}")
    ser.write(message.encode())
    time.sleep(0.1)
    ser.write(bytes([26])) # ASCII for Ctrl+Z
    
    # Wait for the final OK
    if send_at_command("", expected_response="OK", timeout=10):
        logging.info("SMS sent successfully.")
        return True
    else:
        logging.error("Failed to send SMS.")
        return False

def make_call(phone_number):
    """
    Initiates a voice call to the specified phone number.
    """
    logging.info(f"Attempting to call {phone_number}...")
    
    if not send_at_command(f'ATD{phone_number};'):
        logging.error(f"Failed to dial {phone_number}.")
        return False
    
    logging.info("Dialing command sent successfully.")
    # The call is now initiated. The program can continue.
    # To hang up, you would send 'ATH'.
    return True

# --- Initial check on script load ---
if ser:
    send_at_command("ATE0") # Turn off command echo
    send_at_command("AT")   # Test basic communication
