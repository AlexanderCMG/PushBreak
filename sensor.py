from bluepy.btle import Scanner, DefaultDelegate, Peripheral, UUID
import struct
import serial
import time
from datetime import datetime, timedelta

# =============================================================================
# EASY CONFIGURATION SETTINGS - ADJUST THESE AS NEEDED
# =============================================================================

# BLE Device Settings
MAC_ADDRESS = "c1:08:00:01:26:3d"
BASE_UUID = "99DB{:04X}-AC2D-11E3-A5E2-0800200C9A66"

# Arduino Settings
ARDUINO_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600

# Activity Detection Settings
SITTING_DETECTION_TIME = 30  # seconds - how long to monitor for sitting detection
STEPS_THRESHOLD = 5          # minimum steps needed to be considered "active"
WALKING_DETECTION_TIME = 60  # seconds - how long of walking before motor goes down (1 minute default)
WALKING_STEPS_THRESHOLD = 10 # minimum steps per detection window to be considered "walking"

# Motor Control Settings
SITTING_TIMEOUT = 5 * 60     # seconds - how long of sitting before motor starts (5 minutes)
MOTOR_ACTIVATION_DURATION = 10  # seconds - how long motor stays on when activated
MOTOR_REPEAT_INTERVAL = 2 * 60  # seconds - how often motor activates while still sitting (2 minutes)

# =============================================================================

# BLE UUIDs
ACTIVITY_SERVICE_UUID = UUID(BASE_UUID.format(0x2100))
ACTIVITY_DATA_UUID = UUID(BASE_UUID.format(0x2101))

class ActivityMonitor(DefaultDelegate):
    def __init__(self, serial_connection):
        super().__init__()
        self.ser = serial_connection
        
        # Activity tracking
        self.step_readings = []
        self.sitting_start_time = None
        self.last_activity_time = time.time()
        
        # Walking detection
        self.walking_start_time = None
        self.motor_lowered = False  # Track if motor has been lowered due to walking
        
        # Motor control
        self.motor_active = False
        self.motor_start_time = None
        self.last_motor_activation = None
        
        print("=== Activity Monitor Started ===")
        print(f"Sitting timeout: {SITTING_TIMEOUT/60:.1f} minutes")
        print(f"Walking detection time: {WALKING_DETECTION_TIME} seconds")
        print(f"Motor activation duration: {MOTOR_ACTIVATION_DURATION} seconds")
        print(f"Motor repeat interval: {MOTOR_REPEAT_INTERVAL/60:.1f} minutes")
        print("=" * 35)

    def handleNotification(self, cHandle, data):
        current_time = time.time()
        steps = int.from_bytes(data[0:2], byteorder='little')
        
        # Store step reading with timestamp
        self.step_readings.append({
            'steps': steps,
            'timestamp': current_time
        })
        
        # Keep only recent readings (last max of sitting/walking detection time)
        max_detection_time = max(SITTING_DETECTION_TIME, WALKING_DETECTION_TIME)
        cutoff_time = current_time - max_detection_time
        self.step_readings = [r for r in self.step_readings if r['timestamp'] > cutoff_time]
        
        # Check activity states
        is_currently_sitting = self._is_sitting()
        is_currently_walking = self._is_walking()
        
        if is_currently_walking:
            self._handle_walking_detected(current_time)
        elif is_currently_sitting:
            self._handle_sitting_detected(current_time)
        else:
            self._handle_general_activity_detected(current_time)
        
        # Update motor state
        self._update_motor_state(current_time)
        
        # Print status
        self._print_status(steps, is_currently_sitting, is_currently_walking)

    def _is_sitting(self):
        """Determine if user is sitting based on recent step data"""
        if len(self.step_readings) < 2:
            return False
        
        # Get readings from the sitting detection window
        cutoff_time = time.time() - SITTING_DETECTION_TIME
        sitting_readings = [r for r in self.step_readings if r['timestamp'] > cutoff_time]
        
        if len(sitting_readings) < 2:
            return False
        
        # Calculate step difference over the monitoring period
        oldest_reading = min(sitting_readings, key=lambda x: x['timestamp'])
        newest_reading = max(sitting_readings, key=lambda x: x['timestamp'])
        
        step_difference = newest_reading['steps'] - oldest_reading['steps']
        time_difference = newest_reading['timestamp'] - oldest_reading['timestamp']
        
        # Only consider it sitting if we have enough data and low step count
        if time_difference >= SITTING_DETECTION_TIME * 0.8:  # At least 80% of monitoring window
            return step_difference < STEPS_THRESHOLD
        
        return False

    def _is_walking(self):
        """Determine if user is walking based on recent step data"""
        if len(self.step_readings) < 2:
            return False
        
        # Get readings from the walking detection window
        cutoff_time = time.time() - WALKING_DETECTION_TIME
        walking_readings = [r for r in self.step_readings if r['timestamp'] > cutoff_time]
        
        if len(walking_readings) < 2:
            return False
        
        # Calculate step difference over the walking monitoring period
        oldest_reading = min(walking_readings, key=lambda x: x['timestamp'])
        newest_reading = max(walking_readings, key=lambda x: x['timestamp'])
        
        step_difference = newest_reading['steps'] - oldest_reading['steps']
        time_difference = newest_reading['timestamp'] - oldest_reading['timestamp']
        
        # Consider it walking if we have enough data and sufficient step count
        if time_difference >= WALKING_DETECTION_TIME * 0.8:  # At least 80% of monitoring window
            return step_difference >= WALKING_STEPS_THRESHOLD
        
        return False

    def _handle_walking_detected(self, current_time):
        """Handle when walking is detected"""
        if self.walking_start_time is None:
            self.walking_start_time = current_time
            print(f"Walking detected at {datetime.now().strftime('%H:%M:%S')}")
        
        # Reset sitting state if we were sitting
        if self.sitting_start_time is not None:
            sitting_duration = current_time - self.sitting_start_time
            print(f"Walking started! Was sitting for {sitting_duration/60:.1f} minutes")
            self.sitting_start_time = None
        
        self.last_activity_time = current_time
        
        # Stop motor if it's currently running
        if self.motor_active:
            self._stop_motor()
        
        # Check if we should lower the motor due to sustained walking
        if not self.motor_lowered:
            walking_duration = current_time - self.walking_start_time
            if walking_duration >= WALKING_DETECTION_TIME:
                self._lower_motor()

    def _handle_sitting_detected(self, current_time):
        """Handle when sitting is detected"""
        # Reset walking state
        if self.walking_start_time is not None:
            walking_duration = current_time - self.walking_start_time
            print(f"Stopped walking after {walking_duration/60:.1f} minutes")
            self.walking_start_time = None
        
        if self.sitting_start_time is None:
            self.sitting_start_time = current_time
            print(f"Sitting detected at {datetime.now().strftime('%H:%M:%S')}")

    def _handle_general_activity_detected(self, current_time):
        """Handle when general activity (not sitting, not sustained walking) is detected"""
        # Reset sitting state
        if self.sitting_start_time is not None:
            sitting_duration = current_time - self.sitting_start_time
            print(f"Activity detected! Was sitting for {sitting_duration/60:.1f} minutes")
            self.sitting_start_time = None
        
        # Reset walking state if not enough for sustained walking
        if self.walking_start_time is not None:
            walking_duration = current_time - self.walking_start_time
            if walking_duration < WALKING_DETECTION_TIME:
                self.walking_start_time = None
        
        self.last_activity_time = current_time
        
        # Stop motor if it's currently running
        if self.motor_active:
            self._stop_motor()

    def _update_motor_state(self, current_time):
        """Update motor state based on sitting duration and timing"""
        
        # If motor is currently active, check if it should stop
        if self.motor_active:
            if current_time - self.motor_start_time >= MOTOR_ACTIVATION_DURATION:
                self._stop_motor()
            return
        
        # Check if we should start the motor (only when sitting)
        if self.sitting_start_time is not None:
            sitting_duration = current_time - self.sitting_start_time
            
            # Start motor if sitting too long
            if sitting_duration >= SITTING_TIMEOUT:
                # Check if enough time has passed since last activation
                if (self.last_motor_activation is None or 
                    current_time - self.last_motor_activation >= MOTOR_REPEAT_INTERVAL):
                    self._start_motor(current_time)

    def _start_motor(self, current_time):
        """Start the motor (raise)"""
        self.motor_active = True
        self.motor_start_time = current_time
        self.last_motor_activation = current_time
        self.motor_lowered = False  # Reset lowered state when raising
        self.ser.write(b'1')  # Send motor UP command
        print(f"MOTOR ACTIVATED (UP) at {datetime.now().strftime('%H:%M:%S')}")

    def _stop_motor(self):
        """Stop the motor"""
        self.motor_active = False
        self.motor_start_time = None
        self.ser.write(b'0')  # Send motor STOP command
        print(f"Motor stopped at {datetime.now().strftime('%H:%M:%S')}")

    def _lower_motor(self):
        """Lower the motor due to sustained walking"""
        self.motor_lowered = True
        self.ser.write(b'2')  # Send motor DOWN command
        print(f"MOTOR LOWERED (DOWN) due to walking at {datetime.now().strftime('%H:%M:%S')}")
        
        # Reset walking timer to prevent repeated lowering
        self.walking_start_time = time.time()

    def _print_status(self, current_steps, is_sitting, is_walking):
        """Print current status"""
        current_time = time.time()
        status_time = datetime.now().strftime('%H:%M:%S')
        
        if is_walking and self.walking_start_time:
            walking_duration = current_time - self.walking_start_time
            walking_mins = walking_duration / 60
            
            if walking_duration >= WALKING_DETECTION_TIME:
                status = f"WALKING ({walking_mins:.1f} min)"
            else:
                remaining = (WALKING_DETECTION_TIME - walking_duration)
                status = f"Walking ({walking_duration:.0f}s, {remaining:.0f}s until motor down)"
        elif is_sitting and self.sitting_start_time:
            sitting_duration = current_time - self.sitting_start_time
            sitting_mins = sitting_duration / 60
            
            if sitting_duration >= SITTING_TIMEOUT:
                status = f"SITTING TOO LONG ({sitting_mins:.1f} min)"
            else:
                remaining = (SITTING_TIMEOUT - sitting_duration) / 60
                status = f"Sitting ({sitting_mins:.1f} min, {remaining:.1f} min until motor)"
        else:
            status = "Active"
        
        motor_status = "UP" if self.motor_active else ("DOWN" if self.motor_lowered else "OFF")
        print(f"[{status_time}] Steps: {current_steps:4d} | {status} | Motor: {motor_status}")

    def cleanup(self):
        """Clean up when disconnecting"""
        if self.motor_active:
            self._stop_motor()
        print("Activity monitor cleaned up")

def connect_and_monitor(mac_address):
    """Connect to BLE device and start monitoring with retry logic"""
    print(f"Connecting to {mac_address}...")
    
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
    
    dev = None
    monitor = None
    
    # Keep trying to connect to BLE device until successful
    while dev is None:
        try:
            print(f"Attempting to connect to BLE device {mac_address}...")
            dev = Peripheral(mac_address, addrType="random")
            monitor = ActivityMonitor(ser)
            dev.setDelegate(monitor)
            
            print("Discovering services...")
            dev.getServices()
            
            # Enable notifications
            print("Enabling notifications...")
            activity_char = dev.getCharacteristics(uuid=ACTIVITY_DATA_UUID)[0]
            handle = activity_char.getHandle() + 1
            dev.writeCharacteristic(handle, b'\x01\x00', withResponse=True)
            
            print("Connected and monitoring! Press Ctrl+C to stop.")
            print("-" * 50)
            
        except Exception as e:
            print(f"BLE connection failed: {e}")
            print("Retrying BLE connection in 10 seconds...")
            if dev:
                try:
                    dev.disconnect()
                except:
                    pass
                dev = None
            time.sleep(10)
    
    # Main monitoring loop with reconnection logic
    try:
        while True:
            try:
                if dev.waitForNotifications(5.0):
                    continue
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Waiting for data...")
            except Exception as e:
                print(f"Connection lost: {e}")
                print("Attempting to reconnect...")
                try:
                    dev.disconnect()
                except:
                    pass
                
                # Try to reconnect
                dev = None
                while dev is None:
                    try:
                        print(f"Reconnecting to {mac_address}...")
                        dev = Peripheral(mac_address, addrType="random")
                        dev.setDelegate(monitor)
                        
                        # Re-enable notifications
                        activity_char = dev.getCharacteristics(uuid=ACTIVITY_DATA_UUID)[0]
                        handle = activity_char.getHandle() + 1
                        dev.writeCharacteristic(handle, b'\x01\x00', withResponse=True)
                        print("Reconnected successfully!")
                        
                    except Exception as reconnect_error:
                        print(f"Reconnection failed: {reconnect_error}")
                        print("Retrying in 10 seconds...")
                        if dev:
                            try:
                                dev.disconnect()
                            except:
                                pass
                            dev = None
                        time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nStopping monitor...")
    finally:
        try:
            if monitor:
                monitor.cleanup()
            if dev:
                dev.disconnect()
            ser.close()
            print("Disconnected from all devices")
        except:
            pass

def scan_devices():
    """Scan for available BLE devices"""
    print("Scanning for BLE devices...")
    scanner = Scanner()
    devices = scanner.scan(5.0)
    
    print(f"Found {len(devices)} devices:")
    for dev in devices:
        print(f"  {dev.addr} (RSSI: {dev.rssi} dBm)")
    print("-" * 30)

# Main execution
if __name__ == "__main__":
    print("BLE Step Counter & Motor Controller with Walking Detection")
    print("=" * 55)
    
    # Show current configuration
    print("Current Settings:")
    print(f"  • Sitting detection window: {SITTING_DETECTION_TIME} seconds")
    print(f"  • Sitting timeout: {SITTING_TIMEOUT/60:.1f} minutes")
    print(f"  • Walking detection time: {WALKING_DETECTION_TIME} seconds")
    print(f"  • Walking steps threshold: {WALKING_STEPS_THRESHOLD} steps")
    print(f"  • Motor duration: {MOTOR_ACTIVATION_DURATION} seconds")
    print(f"  • Motor repeat interval: {MOTOR_REPEAT_INTERVAL/60:.1f} minutes")
    print(f"  • Steps threshold: {STEPS_THRESHOLD} steps")
    print("=" * 55)
    
    # Scan for devices first
    scan_devices()
    
    # Start monitoring
    connect_and_monitor(MAC_ADDRESS)