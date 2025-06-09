import serial
import time
import csv
import os
from datetime import datetime

# =============================================================================
# EASY CONFIGURATION SETTINGS - ADJUST THESE AS NEEDED
# =============================================================================

# Arduino Settings
ARDUINO_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600

# Motor Control Settings
SITTING_TIMEOUT = 5 * 60 + 30    # seconds - how long of sitting before motor starts (30 seconds for testing)
MOTOR_ACTIVATION_DURATION = 1  # seconds - how long motor stays on when activated
MOTOR_REPEAT_INTERVAL = 1 * 60  # seconds - how often motor activates while still sitting (10 seconds for testing)

# CSV Logging Settings
CSV_DIRECTORY = "activity_logs"  # Directory where CSV files will be saved

# =============================================================================

class ActivityMonitor:
    def __init__(self, serial_connection, csv_writer):
        self.ser = serial_connection
        self.csv_writer = csv_writer

        # Activity tracking - assume sitting from start
        self.sitting_start_time = time.time()
        self.current_state = "Sitting"
        self.state_start_time = time.time()

        # Motor control
        self.motor_active = False
        self.motor_start_time = None
        self.last_motor_activation = None

        print("=== Activity Monitor Started ===")
        print("Assuming user is sitting from start")
        print(f"Sitting timeout: {SITTING_TIMEOUT/60:.1f} minutes")
        print(f"Motor activation duration: {MOTOR_ACTIVATION_DURATION} seconds")
        print(f"Motor repeat interval: {MOTOR_REPEAT_INTERVAL/60:.1f} minutes")
        print("=" * 35)

        # Log initial sitting state
        self._log_state_start()

    def _log_state_start(self):
        """Log the start of sitting state"""
        timestamp = datetime.fromtimestamp(self.state_start_time).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Started sitting at {timestamp}")

    def update_motor_state(self):
        """Update motor state based on sitting duration and timing"""
        current_time = time.time()

        # If motor is currently active, check if it should stop
        if self.motor_active:
            if current_time - self.motor_start_time >= MOTOR_ACTIVATION_DURATION:
                self._stop_motor()
            return

        # Check if we should start the motor (we're always sitting)
        sitting_duration = current_time - self.sitting_start_time

        # Start motor if sitting too long
        if sitting_duration >= SITTING_TIMEOUT:
            # Check if enough time has passed since last activation
            if (self.last_motor_activation is None or
                current_time - self.last_motor_activation >= MOTOR_REPEAT_INTERVAL):
                self._start_motor(current_time)

    def _start_motor(self, current_time):
        """Start the motor"""
        self.motor_active = True
        self.motor_start_time = current_time
        self.last_motor_activation = current_time
        self.ser.write(b'1')  # Send motor ON command
        print(f"MOTOR ACTIVATED at {datetime.now().strftime('%H:%M:%S')}")

    def _stop_motor(self):
        """Stop the motor"""
        self.motor_active = False
        self.motor_start_time = None
        self.ser.write(b'0')  # Send motor OFF command
        print(f"Motor stopped at {datetime.now().strftime('%H:%M:%S')}")

    def print_status(self):
        """Print current status"""
        current_time = time.time()
        status_time = datetime.now().strftime('%H:%M:%S')
        
        sitting_duration = current_time - self.sitting_start_time
        sitting_mins = sitting_duration / 60
        
        if sitting_duration >= SITTING_TIMEOUT:
            status = f"SITTING TOO LONG ({sitting_mins:.1f} min)"
        else:
            remaining = (SITTING_TIMEOUT - sitting_duration) / 60
            status = f"Sitting ({sitting_mins:.1f} min, {remaining:.1f} min until motor)"
        
        motor_status = "ON" if self.motor_active else "OFF"
        print(f"[{status_time}] {status} | Motor: {motor_status}")

    def cleanup(self):
        """Clean up when disconnecting"""
        # Log final state
        current_time = time.time()
        duration_seconds = current_time - self.state_start_time
        duration_minutes = duration_seconds / 60
        
        timestamp = datetime.fromtimestamp(self.state_start_time).strftime('%Y-%m-%d %H:%M:%S')
        end_timestamp = datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')
        
        self.csv_writer.writerow([
            timestamp,
            end_timestamp,
            self.current_state,
            f"{duration_minutes:.2f}",
            f"{duration_seconds:.1f}"
        ])
        print(f"Final CSV LOG: {self.current_state} for {duration_minutes:.2f} minutes")
        
        if self.motor_active:
            self._stop_motor()
        print("Activity monitor cleaned up")

def create_csv_file():
    """Create a new CSV file with timestamp in filename"""
    # Create directory if it doesn't exist
    if not os.path.exists(CSV_DIRECTORY):
        os.makedirs(CSV_DIRECTORY)
    
    # Create filename with current timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{CSV_DIRECTORY}/activity_log_{timestamp}.csv"
    
    # Open CSV file and write header
    csv_file = open(filename, 'w', newline='')
    csv_writer = csv.writer(csv_file)
    
    # Write header row
    csv_writer.writerow([
        'Start Time',
        'End Time', 
        'State',
        'Duration (minutes)',
        'Duration (seconds)'
    ])
    
    print(f"Created CSV log file: {filename}")
    return csv_file, csv_writer

def start_monitoring():
    """Start the simplified monitoring system"""
    print("Starting simplified motor controller...")
    
    # Create CSV file
    csv_file, csv_writer = create_csv_file()
    
    try:
        # Initialize serial connection
        ser = None
        while ser is None:
            try:
                ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
                time.sleep(2)  # Allow Arduino to initialize
                print(f"Connected to Arduino on {ARDUINO_PORT}")
            except Exception as e:
                print(f"Failed to connect to Arduino: {e}")
                print("Retrying Arduino connection in 5 seconds...")
                time.sleep(5)
        
        # Create monitor
        monitor = ActivityMonitor(ser, csv_writer)
        
        print("Monitoring started! Press Ctrl+C to stop.")
        print("Data will be logged to CSV file.")
        print("-" * 50)
        
        # Main monitoring loop
        try:
            while True:
                monitor.update_motor_state()
                monitor.print_status()
                time.sleep(5)  # Update every 5 seconds
                
        except KeyboardInterrupt:
            print("\nStopping monitor...")
        finally:
            try:
                monitor.cleanup()
                ser.close()
                print("Disconnected from Arduino")
            except:
                pass
    
    finally:
        # Always close CSV file
        csv_file.close()
        print("CSV file saved and closed")

# Main execution
if __name__ == "__main__":
    print("Simplified Motor Controller with CSV Logging")
    print("=" * 45)

    # Show current configuration
    print("Current Settings:")
    print(f"  • Sitting timeout: {SITTING_TIMEOUT/60:.1f} minutes")
    print(f"  • Motor duration: {MOTOR_ACTIVATION_DURATION} seconds")
    print(f"  • Motor repeat interval: {MOTOR_REPEAT_INTERVAL/60:.1f} minutes")
    print(f"  • CSV files saved to: {CSV_DIRECTORY}/")
    print("=" * 45)

    # Start monitoring
    start_monitoring()
