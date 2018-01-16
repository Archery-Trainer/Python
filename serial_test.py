import serial

# Reading from the serial with 9600 baud rate
#ser = serial.Serial('/dev/ttyACM1',19200)
ser = serial.Serial()
ser.port = '/dev/ttyACM5'
ser.baudrate = 19200
ser.timeout = 1
ser.setDTR(False)
#arduinoSerialData.setRTS(False)
ser.open()
#counter =  0

while True:
	#counter += 1

	#read the serial
	read_serial = ser.readline()

	#print the values
	print("test %s" % read_serial) #read_serial.replace('\r\n',''))
		
