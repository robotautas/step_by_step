import serial

ser = serial.Serial("/dev/ttyAMA0", 125000, timeout=1)
print(ser.is_open)
ser.write(b"<ST>")
# print(ser.readline().decode())
ser.close()