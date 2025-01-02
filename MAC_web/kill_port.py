import psutil
import os
import serial.tools.list_ports

def find_process_using_serial_port(port_name):
    """
    Find the PID of the process using the specified serial port.
    """
    for proc in psutil.process_iter(['pid', 'name', 'open_files']):
        try:
            for file in proc.info['open_files'] or []:
                if port_name in file.path:
                    print(f"Process {proc.info['name']} with PID {proc.info['pid']} is using {port_name}")
                    return proc.info['pid']
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
    return None

def kill_process_using_serial_port(port_name):
    """
    Kill the process using the specified serial port.
    """
    pid = find_process_using_serial_port(port_name)
    if pid:
        try:
            print(f"Killing process with PID {pid} using {port_name}...")
            os.kill(pid, 9)  # Forcefully terminate the process
            print(f"Process {pid} terminated.")
        except Exception as e:
            print(f"Error terminating process {pid}: {e}")
    else:
        print(f"No process found using {port_name}.")

if __name__ == "__main__":
    # Find available serial ports
    ports = serial.tools.list_ports.comports()
    port_names = [port.device for port in ports]

    print("Available serial ports:", port_names)
    target_port = "COM3"

    if target_port in port_names:
        kill_process_using_serial_port(target_port)
    else:
        print(f"{target_port} is not currently available.")
