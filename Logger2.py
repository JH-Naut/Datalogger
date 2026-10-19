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

def change_sensor_settings(ser):

    try:
        PD1,PD2,PD3,PD4 = input("Brightnesses (e.g. 1000 1000 0 0): ").split()
        Brightcom = f"!Brightness {PD1} {PD2} {PD3} {PD4}\r\n"
        ser.write(Brightcom.encode('utf-8'))
        ser.flush()
        print(Brightcom)
        time.sleep(1)

        T= input("Heater temperature: ")
        Tempcom = f"!SetTargetTemp 0 {T} 0 0\r\n"
        ser.write(Tempcom.encode('utf-8'))
        ser.flush()
        print(Tempcom)
        time.sleep(1)

        Honoff = input("Heater on? (Y/N): ")
        if Honoff.upper() == "Y":
            Hcom = "!HeaterState 0 1 0 0\r\n"
            ser.write(Hcom.encode('utf-8'))

        else:
            Hcom = "!HeaterState 0 0 0 0\r\n"

        ser.flush()
        print(Hcom)
        time.sleep(1)

        MRPM = input("Motor RPM: ")
        MRPMcom = f"!SetMotor1Speed 1 {MRPM}\r\n"
        ser.write(MRPMcom.encode('utf-8'))
        ser.flush()
        print(MRPMcom)
        time.sleep(1)

        Monoff = input("Motor on? (Y/N): ")
        if Monoff.upper() == "Y":
            Mcom = f"!Motor1Enable 1 {MRPM}\r\n"
            ser.write(Mcom.encode('utf-8'))
            
        else:
            Mcom = f"!Motor1Disable\r\n"

        ser.flush()
        print(Mcom)
        time.sleep(1)

    except Exception as e:
        print(f"Error during initialisation: {e}")
   
def logger(ser):
    buffer = []
    flush_interval = 1

    try:
        while True:
            line = ser.readline().decode('utf-8').strip() #Defines the line from the serial port
            if  "MESSAGE" in line: #Filters out lines that don't contain the keyword "MESSAGE"
                linecut = line.removeprefix("{MESSAGE:All_Data|DATA|").removesuffix("}") #Strips prefix and suffix from line
                timestamp = datetime.now().isoformat()
                print(f"{timestamp}: {linecut}")

                buffer.append(f"{timestamp},{linecut}\n") #Adds line to buffer with timestamp

                if len(buffer) >= flush_interval: #Checks if buffer has reached the flush interval
                    with open('data.csv', 'a') as f:
                        f.writelines(buffer)
                    buffer = []

    except KeyboardInterrupt:
        print("Logging stopped. Flushing remaining data to file.")
        if buffer:
            with open('data.csv', 'a') as f:
                f.writelines(buffer)

    except serial.SerialException:
        print("Connection lost. Exiting...")
        time.sleep(1)

def main():
    port = find_device()
    if port is None:
        print("Device not found. Exiting...")
        return

    try:
        print(f"Connecting to {port}")
        ser = serial.Serial(port, 9600, timeout=1)

        # Set initial conditions
        Init_prompt = input("Change sensor settings? (Y/N): ")
        if Init_prompt.upper() == "Y":
            change_sensor_settings(ser)
        else:
            print("Skipping initial conditions.")

        # Prompt to start logging
        start_logging_prompt = input("Start logging? (Y/N): ")
        if start_logging_prompt.upper() == "Y":
            logger(ser)
        else:
            print("Exiting without logging.")

    except serial.SerialException:
        print("Connection error. Exiting...")

    finally:
        try:
            ser.close()
        except:
            pass

if __name__ == "__main__":
    main()