import serial
import time
arduino_port = "/dev/ttyACM0"
baud_rate = 9600

try:
	ser = serial.Serial(arduino_port, baud_rate)
	print("Conntect to Arduino")
	
	while True:
		command = input()		
		if command in ["0", "1", "2"]:
			ser.write(command.encode())
			print(f"Sent command: {command}")
		else:
			ser.write("0".encode())
			print("exiting")
			ser.close()
			break

except serial.SerialException as e:
	print(f"Error: {e}")
	
