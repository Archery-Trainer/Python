
'''
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''
#format 
#python myFirstIotPublish.py -e <endpoint> -r <rootCAFilePath> -c <certFilePath> -k <privateKeyFilePath>


from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
import serial
import serial.tools.list_ports
import random

AllowedActions = ['both', 'publish', 'subscribe']

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

# utility method to get serial port
def getFirstPort():
   ports=[comport.device for comport in serial.tools.list_ports.comports()]
   return ports[0]   



# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
                    help="Targeted client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="sdk/test/Python", help="Targeted topic")
parser.add_argument("-m", "--mode", action="store", dest="mode", default="both",
                    help="Operation modes: %s"%str(AllowedActions))
parser.add_argument("-M", "--message", action="store", dest="message", default="Archer muscle activation level",
                    help="Message to publish")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
useWebsocket = args.useWebsocket
clientId = args.clientId
topic = args.topic

if args.mode not in AllowedActions:
    parser.error("Unknown --mode option %s. Must be one of %s" % (args.mode, str(AllowedActions)))
    exit(2)

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)

#Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

#Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
#if useWebsocket:
#    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
#    myAWSIoTMQTTClient.configureEndpoint(host, 443)
#    myAWSIoTMQTTClient.configureCredentials(rootCAPath)
#else:
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureEndpoint(host, 8883)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
if args.mode == 'both' or args.mode == 'subscribe':
    myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)
time.sleep(2)

#Read muscle sensor value with 9600 baud rate 
ser=serial.Serial('/dev/ttyACM0',9600) #'/dev/ttyACM1' # tai 19200
ser.close()
ser.open() #closing and opening serial port sets it  correctly (removes garbled msgs)
# Publish to the same topic in a loop forever
loopCount = 0

arduinoMessage =""

while True:

    loopCount += 1
	
    if args.mode == 'both' or args.mode == 'publish':
        
        #arduinon viesti       
        arduinoMessage = ser.readline()

        print arduinoMessage
        # removes /r/n
        arduinoMessage = arduinoMessage.rstrip()
        #erotetaan counter ja eri arvot
        arduinoList = arduinoMessage.split(";",)
       
        print len(arduinoList)

        #sensors is a list of measured sensor values following line is for test purposes  ehkapa 'sensors': ser.readline().decode("utf-8", "ignore") # ingnores garbled chars
        # 14... voisi korvata myohemmin A0... tai jtn

        print arduinoList

        #ignores the first 10 values, could be smaller
        if loopCount < 10:
            del arduinoList[0:7]
            continue

        message = {
        
        'timestamp': int(time.time()),
        'counter': arduinoList[0],  
		
        'sensors': [
            {
                'sensorId': '14', 
                'value': arduinoList[1]
            },
            {
                'sensorId': '15', 
                'value': arduinoList[2]
            }, 
            {
                'sensorId': '16',
                'value': arduinoList[3]
            },
            {
                'sensorId': '17',
                'value': arduinoList[4]
            },
            {
                'sensorId' : '18',
                'value': arduinoList[5]
            },
            {
                'sensorId': '19',
                'value': arduinoList[6]
            }
        ]
        }
        

		#val = ser.readline().decode("utf-8", "ignore") # ingnores garbled chars
	
        print('Muscle sensor: %s\n' % arduinoMessage )
        #message['sensor'] = val.replace('\r\n','')  #loopCount
        


        messageJson = json.dumps(message)
        myAWSIoTMQTTClient.publish(topic, messageJson, 1)
        if args.mode == 'publish':
           print('Published topic %s: %s\n' % (topic, messageJson))
        
        arduinoMessage = ""
        del arduinoList[0:7]
    time.sleep(1)
