import serial
import time
import sys

def open_valve(player):
    #return None
    arduino_port = "COM3"
    baud_rate = 9600

    try:
        ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    except serial.SerialException:
        print("SerialException")
        sys.exit(1)

    if player == 1:
        ser.write(b"OPEN1\n")
    else:
        ser.write(b"OPEN2\n")

    ser.close()

def close_valve(player):
    #return None
    arduino_port = "COM3"
    baud_rate = 9600

    try:
        ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    except serial.SerialException:
        print("SerialException")
        sys.exit(1)

    if player == 1:
        ser.write(b"CLOSE1\n")
    else:
        ser.write(b"CLOSE2\n")

    ser.close()
