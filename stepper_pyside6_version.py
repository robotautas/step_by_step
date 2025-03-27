import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QRadioButton, QPushButton, QButtonGroup,
                              QGridLayout, QGroupBox)
from PySide6.QtCore import Qt
import serial
import serial.tools.list_ports
import time

class Commander:
    def __init__(self):
        # Try different possible UART device names
        uart_devices = ['/dev/serial0', '/dev/ttyAMA0', '/dev/ttyS0']
        # uart_devices = ['/dev/ttyAMA0', '/dev/ttyS0']
        self.uart = None
        
        for device in uart_devices:
            try:
                self.uart = serial.Serial(device, 125000, timeout=1)
                print(f"UART initialized on {device}")
                break
            except serial.SerialException:
                print(f"Failed to open {device}")
        
        if self.uart is None:
            print("Could not find a valid UART device!")

    def send_command(self, command):
        if self.uart and self.uart.is_open:
            self.uart.write(command.encode())
            print(f"Sent command: {command}")

            
class StepperApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.commander = Commander()
        
        self.setWindowTitle("Stepper Control")
        self.setGeometry(100, 100, 400, 300)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)
        
        # Radio buttons for step size
        step_group_box = QGroupBox("Step Size")
        step_layout = QHBoxLayout()
        
        # Create radio button group
        self.step_group = QButtonGroup(self)
        
        # Step sizes
        steps = ["1", "10", "100", "1000"]
        for i, step in enumerate(steps):
            radio = QRadioButton(step)
            if i == 0:  # Default to "1"
                radio.setChecked(True)
            self.step_group.addButton(radio, i)
            step_layout.addWidget(radio)

        self.step_map = {'1': '1', '10': '2', '100': '3', '1000': '4'}
        
        step_group_box.setLayout(step_layout)
        main_layout.addWidget(step_group_box)
        
        # Direction buttons
        direction_group_box = QGroupBox("Direction Control")
        direction_layout = QGridLayout()
        
        # Button labels and their positions
        buttons = [
            ("↖", 0, 0), ("↑", 0, 1), ("↗", 0, 2),
            ("←", 1, 0), ("⌂", 1, 1), ("→", 1, 2),
            ("↙", 2, 0), ("↓", 2, 1), ("↘", 2, 2)
        ]
        
        # Create buttons and connect signals
        self.direction_buttons = {}
        for label, row, col in buttons:
            button = QPushButton(label)
            button.setMinimumSize(50, 50)  # Make buttons larger

                # Add a direction code property to each button
            if label == "↖":
                button.code = "QUP_LEFT"
            elif label == "↑":
                button.code = "UP"
            elif label == "↗":
                button.code = "EUP_RIGHT"
            elif label == "←":
                button.code = "LEFT"
            elif label == "⌂":
                button.code = "HOME"
            elif label == "→":
                button.code = "RIGHT"  
            elif label == "↙":
                button.code = "ZDOWN_LEFT"
            elif label == "↓":
                button.code = "DOWN"
            elif label == "↘":
                button.code = "CDOWN_RIGHT"

            button.clicked.connect(lambda checked, l=label: self.on_direction_clicked(l))
            self.direction_buttons[label] = button
            direction_layout.addWidget(button, row, col)
        
        direction_group_box.setLayout(direction_layout)
        main_layout.addWidget(direction_group_box)
    
    def on_direction_clicked(self, direction):
        """Handle direction button clicks"""
        step_size = self.step_group.checkedButton().text()
        print(f"Moving {direction}, Step size: {step_size}")

        direction_code = self.direction_buttons[direction].code
        selected_step = self.step_group.checkedId() + 1

        self.commander.send_command('<ST>')  # Send <ST> before movement
        time.sleep(0.05)  # Small delay to ensure <ST> is processed
        self.commander.send_command(f'<{direction_code[0]}{selected_step}>')

        # Here you would add your code to control the stepper motor
        # based on direction and step size

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StepperApp()
    window.show()
    sys.exit(app.exec())