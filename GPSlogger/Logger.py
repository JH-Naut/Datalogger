#!/usr/bin/env python
# coding: utf-8

# In[12]:


import serial
import serial.tools.list_ports
import time
from datetime import datetime

VID = 0x16C0
PID = 0x0483

def find_device():
    for port in serial.tools.list_ports.comports():
       if port.vid == VID and port.pid == PID:
        return port.device
    return None

with open('data.csv', 'a') as f:

    while True:
        port = find_device()

        if port is None:
            print("Device not found. Retrying...")
            time.sleep(5)
            continue

        try:
            print(f"Connecting to {port}")
            ser = serial.Serial(port, 9600, timeout=1)

            while True:
                
                line = ser.readline().decode('utf-8').strip() #Defines the line from the serial port
                linecut = line.removeprefix("{MESSAGE:All_Data|DATA|").removesuffix("}") #Strips prefix and suffix from line
                
                if  "MESSAGE" in line: #Filters out lines that don't contain the keyword "MESSAGE"

                    if line:

                        timestamp = datetime.now().isoformat()
                        print(f"{timestamp}: {linecut}")

                        f.write(f"{timestamp},{linecut}\n") #Writes line to file with timestamp
                        f.flush()   #Sends data to the file immediately instead of waiting for the buffer to fill up 


        except serial.SerialException:
            print("Connection lost. Reconnecting...")
            time.sleep(2)

        finally:
            try:
                ser.close()
            except:
                pass


# In[ ]: