from bluepy.btle import Scanner, DefaultDelegate, Peripheral, UUID
import struct
import serial
import time

# Constants from the spec
BASE_UUID = "99DB{:04X}-AC2D-11E3-A5E2-0800200C9A66"
ACTIVITY_SERVICE_UUID = UUID(BASE_UUID.format(0x2100))
ACTIVITY_DATA_UUID = UUID(BASE_UUID.format(0x2101))
MAC_ADDRESS = "c1:08:00:01:26:3d"

arduino_port = "/dev/ttyACM0"
baud_rate = 9600

ser = serial.Serial(arduino_port, baud_rate)
print("Conntect to Arduino")

class NotificationDelegate(DefaultDelegate):
	def __init__(self):
		super().__init__()
		self.activity = []
		self.MAX_ACTIVITY = 10
		self.timer = 0
		self.MAX_TIMER = 3

	def handleNotification(self, cHandle, data):
		steps = int.from_bytes(data[0:2], byteorder='little')
		
		self.activity.append(steps)
		if len(self.activity) > self.MAX_ACTIVITY:
			self.activity.pop(0)
			
		print(f"Notification - Activity: {self.activity}")
		if is_sitting(self.activity, self.MAX_ACTIVITY) and not self.timer:
			command = "1"
			self.timer += 1
		elif is_sitting(self.activity, self.MAX_ACTIVITY) :
			self.timer += 1
			command = "0"
			if self.timer == self.MAX_TIMER:
				self.timer = 0
		else:
			command = "2"
			
		ser.write(command.encode())

def connect_and_check(addr):
	print(f"Connecting to {addr}...")
	dev = Peripheral(addr, addrType="random")
	dev.setDelegate(NotificationDelegate())

	# Discover services
	print("Discovering services...")
	dev_services = dev.getServices()

	# Enable notifications
	print("Enabling notifications...")
	activity_data_char = dev.getCharacteristics(uuid=ACTIVITY_DATA_UUID)[0]
	handle = activity_data_char.getHandle() + 1
	dev.writeCharacteristic(handle, b'\x01\x00', withResponse=True)

	print("Waiting for notifications... Press Ctrl+C to stop.")
	try:
		while True:
			if dev.waitForNotifications(5.0):
				continue
			print("Waiting...")
	except KeyboardInterrupt:
		print("Disconnecting...")
	finally:
		dev.disconnect()
		ser.write("0".encode())
		
def is_sitting(activity, max_activity):
	if len(activity) < max_activity:
		return False

	step_diff = activity[-1] - activity[0]
	
	if step_diff < 5:
		return True
	return False

# Main
if __name__ == "__main__":	
	scanner = Scanner()
	devices = scanner.scan(5.0)
	
	for dev in devices:
		print(dev.addr, dev.rssi)
	
	connect_and_check(MAC_ADDRESS)
