import serial
import time
from datetime import datetime

# =============================================================================
# EASY CONFIGURATION SETTINGS - ADJUST THESE AS NEEDED
# =============================================================================

# Arduino Settings
ARDUINO_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600

# =============================================================================

def connect_to_arduino():
    """Connect to Arduino with retry logic"""
    ser = None
    while ser is None:
        try:
            print(f"Connecting to Arduino on {ARDUINO_PORT}...")
            ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
            time.sleep(2)  # Allow Arduino to initialize
            print(f"✓ Connected to Arduino on {ARDUINO_PORT}")
            return ser
        except Exception as e:
            print(f"✗ Failed to connect to Arduino: {e}")
            print("Retrying in 3 seconds...")
            time.sleep(3)

def lower_motor(ser):
    """Send command to lower the motor"""
    try:
        ser.write(b'2')  # Send motor ON/lower command
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] ✓ Motor lowered")
        return True
    except Exception as e:
        print(f"✗ Failed to lower motor: {e}")
        return False

def stop_motor(ser):
    """Send command to stop the motor"""
    try:
        ser.write(b'0')  # Send motor OFF command
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] ✓ Motor stopped")
        return True
    except Exception as e:
        print(f"✗ Failed to stop motor: {e}")
        return False

def main():
    """Main function"""
    print("Simple Motor Controller")
    print("=" * 30)
    print("• Motor will lower when program starts")
    print("• Press Ctrl+C to stop the motor and exit")
    print("=" * 30)
    
    ser = None
    
    try:
        # Connect to Arduino
        ser = connect_to_arduino()
        
        # Lower the motor
        print("\nLowering motor...")
        if lower_motor(ser):
            print("Motor is now lowered.")
            print("\nPress Ctrl+C to stop the motor and exit the program.")

            # Keep the program running until Ctrl+C
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\nCtrl+C detected - stopping motor...")

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        # Always try to stop the motor and close connection
        if ser:
            try:
                stop_motor(ser)
                ser.close()
                print("✓ Disconnected from Arduino")
            except Exception as e:
                print(f"Error during cleanup: {e}")

        print("Program ended.")

if __name__ == "__main__":
    main()
