import serial.tools.list_ports

#list_ports.comports()
ports=[comport.device for comport in serial.tools.list_ports.comports()]
print(ports[0])
