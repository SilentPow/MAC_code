import serial
import time
import keyboard  # pip install keyboard
import sys

def main():
    # Update this to match your Arduino's serial port name
    # For Windows: e.g. "COM3"
    # For Linux/macOS: e.g. "/dev/ttyACM0" or "/dev/ttyUSB0"
    arduino_port = "COM9"
    baud_rate = 9600

    try:
        ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    except serial.SerialException:
        print(f"Could not open port {arduino_port}. Make sure the port is correct and not in use.")
        sys.exit(1)

    # Give the Arduino time to reset after opening the serial connection
    time.sleep(2)

    print("Press SPACE to send 'SPACE' command to Arduino.")
    print("Press ESC to exit.\n")

    try:
        while True:
            # Check if space is pressed
            if keyboard.is_pressed('space'):
                # Send "SPACE\n" to the Arduino
                ser.write(b"SPACE\n")
                print("Sent 'SPACE' to Arduino.")
                # Brief delay to prevent sending multiple times if space is held
                time.sleep(0.3)

            # Check if ESC is pressed, then exit
            if keyboard.is_pressed('esc'):
                print("ESC pressed. Exiting.")
                break

            # If Arduino sends any data back, read and print it
            while ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"Arduino says: {line}")

            # Small delay to prevent busy-waiting
            time.sleep(0.02)

    except KeyboardInterrupt:
        print("Interrupted by user (Ctrl+C).")

    finally:
        ser.close()
        print("Serial connection closed.")

if __name__ == "__main__":
    main()
