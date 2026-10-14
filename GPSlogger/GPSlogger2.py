#!/usr/bin/env python
# coding: utf-8

# In[12]:


import serial
import serial.tools.list_ports
import time
from datetime import datetime

VID = 0x2341
PID = 0x8054

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
                
                line = ser.readline().decode('utf-8').strip()
                if line:

                    timestamp = datetime.now().isoformat()
                    print(f"{timestamp}: {line}")

                    f.write(f"{timestamp},{line}\n")
                    f.flush()

        except serial.SerialException:
            print("Connection lost. Reconnecting...")
            time.sleep(2)

        finally:
            try:
                ser.close()
            except:
                pass


# In[ ]:




