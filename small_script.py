import serial

ser = serial.Serial("/dev/serial0", 125000, timeout=1)
ser.write("<ST>".encode())
# print(ser.readline().decode())
ser.close()