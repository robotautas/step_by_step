import PySimpleGUI as sg
import serial
import serial.tools.list_ports
import time

# Global variables
ser = None  # Serial connection
selected_step = '1'  # Default step count
step_map = {'1': '1', '10': '2', '100': '3', '1000': '4'}  # Step mapping

# Function to list available serial ports
def get_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# Function to send serial command
def send_command(command):
    if ser and ser.is_open:
        ser.write(command.encode())

# Function to handle movement commands
def move(direction):
    global selected_step
    send_command('<ST>')  # Send <ST> before movement
    time.sleep(0.05)  # Small delay to ensure <ST> is processed
    send_command(f'<{direction}{step_map[selected_step]}>')

# Function to select step size
def select_step(step, window):
    global selected_step
    selected_step = step
    # Update button highlights
    for i, step_value in enumerate(['1', '10', '100', '1000']):
        window[f'STEP_{i+1}'].update(button_color=('white', 'blue' if step == step_value else 'black'))

# Function to connect to selected serial port
def connect_serial(port, window):
    global ser
    try:
        ser = serial.Serial(port, 125000, timeout=1)
        window['CONNECT'].update(disabled=True)
        window['PORTS'].update(disabled=True)
    except Exception as e:
        sg.popup_error(f"Error connecting to {port}\n{e}")

# Layout definition
layout = [
    [sg.Text("Select Step Count:")],
    [sg.Button("0.5", size=(5, 1), key='STEP_1'),
     sg.Button("1", size=(5, 1), key='STEP_2'),
     sg.Button("2", size=(5, 1), key='STEP_3'),
     sg.Button("4", size=(5, 1), key='STEP_4')],

    [sg.Text("", size=(12, 1))],
    [sg.Button("↖", size=(4, 2), key="QUP_LEFT"), sg.Button("↑", size=(4, 2), key="UP"), sg.Button("↗", size=(4, 2), key="EUP_RIGHT")],
    [sg.Button("←", size=(4, 2), key="LEFT"), sg.Button("Home", size=(4, 2), key="HOME"), sg.Button("→", size=(4, 2), key="RIGHT")],
    [sg.Button("↙", size=(4, 2), key="ZDOWN_LEFT"), sg.Button("↓", size=(4, 2), key="DOWN"), sg.Button("↘", size=(4, 2), key="CDOWN_RIGHT")],

    [sg.Text("Serial Port:"), sg.Combo(get_serial_ports(), key="PORTS", size=(10, 1)), 
     sg.Button("Connect", key="CONNECT")],
]

# Create window
window = sg.Window("Stepper Motor Controller", layout, finalize=True)

# Main event loop
while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        if ser:
            ser.close()
        break

    if event == "CONNECT":
        connect_serial(values["PORTS"], window)

    if event in ["UP", "DOWN", "LEFT", "RIGHT", "QUP_LEFT", "EUP_RIGHT", "ZDOWN_LEFT", "CDOWN_RIGHT"]:
        move(event[0])

    if event == "HOME": 
        move("H") # Send the home command

    if event.startswith("STEP_"):
        step_index = int(event[-1]) - 1
        select_step(['1', '10', '100', '1000'][step_index], window)

window.close()
