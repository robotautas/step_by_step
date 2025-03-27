# -*- coding: utf-8 -*-
import sys
import time
import tkinter as tk
from tkinter import ttk
import serial

class Commander:
    def __init__(self):
        # Try different possible UART device names
        uart_devices = ['/dev/serial0', '/dev/ttyAMA0', '/dev/ttyS0']
        self.uart = None

        for device in uart_devices:
            try:
                self.uart = serial.Serial(device, 125000, timeout=1)
                print("UART initialized on", device)
                break
            except serial.SerialException:
                print("Failed to open", device)

        if self.uart is None:
            print("Could not find a valid UART device!")

    def send_command(self, command):
        if self.uart and self.uart.is_open:
            self.uart.write(command.encode())
            print("Sent command:", command)


class StepperApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.commander = Commander()
        self.title("Stepper Control")
        self.geometry("400x300")

        # Create main container frame
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill='both', expand=True)

        # Step Size group using LabelFrame
        step_frame = ttk.LabelFrame(main_frame, text="Step Size")
        step_frame.pack(fill='x', padx=5, pady=5)

        # Tkinter variable to store the selected step (values: 1,2,3,4 corresponding to step sizes "1", "10", "100", "1000")
        self.step_var = tk.IntVar(value=1)
        steps = [("0.5", 1), ("1", 2), ("2", 3), ("4", 4)]
        for text, value in steps:
            rb = ttk.Radiobutton(step_frame, text=text, variable=self.step_var, value=value)
            rb.pack(side='left', padx=5, pady=5)

        # Direction Control group using LabelFrame and grid layout
        direction_frame = ttk.LabelFrame(main_frame, text="Direction Control")
        direction_frame.pack(padx=5, pady=5)

        # Mapping of button labels to their corresponding command codes
        # The first character of each code is used to form the command
        self.direction_codes = {
            "↖": "QUP_LEFT",
            "↑": "UP",
            "↗": "EUP_RIGHT",
            "←": "LEFT",
            "⌂": "HOME",
            "→": "RIGHT",
            "↙": "ZDOWN_LEFT",
            "↓": "DOWN",
            "↘": "CDOWN_RIGHT"
        }

        # Layout direction buttons in a 3x3 grid
        buttons = [
            ("↖", 0, 0), ("↑", 0, 1), ("↗", 0, 2),
            ("←", 1, 0), ("⌂", 1, 1), ("→", 1, 2),
            ("↙", 2, 0), ("↓", 2, 1), ("↘", 2, 2)
        ]

        for (label, row, col) in buttons:
            btn = ttk.Button(direction_frame, text=label, command=lambda l=label: self.on_direction_clicked(l))
            btn.grid(row=row, column=col, padx=5, pady=5, ipadx=10, ipady=10)

    def on_direction_clicked(self, direction):
        """Handle direction button clicks"""
        step_size = self.step_var.get()  # This is already the step index (1, 2, 3, or 4)
        print("Moving", direction, ", Step size:", step_size)

        direction_code = self.direction_codes.get(direction, "")
        if not direction_code:
            print("No code defined for direction", direction)
            return

        # Send "<ST>" command before movement
        self.commander.send_command("<ST>")
        time.sleep(0.05)  # Small delay to ensure <ST> is processed
        # Build command using the first character of the direction code and the selected step number
        command = f'<{direction_code[0]}{step_size}>'
        self.commander.send_command(command)


if __name__ == "__main__":
    app = StepperApp()
    app.mainloop()