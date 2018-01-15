import serial

# Reading from the serial with 9600 baud rate
ser = serial.Serial('/dev/ttyACM1',19200)

#counter =  0

while True:
	#counter += 1

	#read the serial
	read_serial = ser.readline()

	#print the values
	print("test %s" % read_serial) #read_serial.replace('\r\n',''))
		
