import serial
import time
import sys

arduino_port = "COM4"
baud_rate = 9600
ser = None

def get_serial_connection():
    global ser
    if ser is None or not ser.is_open:
        try:
            ser = serial.Serial(arduino_port, baud_rate, timeout=1)
            print("Serial port opened.")
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            sys.exit(1)
    return ser

def close_serial():
    global ser
    if ser and ser.is_open:
        ser.close()
        print("Serial port closed.")

def open_valve(player):
    arduino_port = "COM4"
    baud_rate = 9600
    ser = get_serial_connection()
    
    print("opening")
    if player == 1:
        ser.write(b"OPEN1\n")
        print("OPEN1\n")
    else:
        ser.write(b"OPEN2\n")
        print("OPEN2\n")

def close_valve(player):
    ser = get_serial_connection()
    print("closing")
    if player == 1:
        ser.write(b"CLOSE1\n")
    else:
        ser.write(b"CLOSE2\n")
