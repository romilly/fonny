```python
import serial

# Open a serial port
ser = serial.Serial('/dev/ttyUSB0', 9600)  # Adjust port name and baud rate as needed

# Write data
ser.write(b'Hello, Arduino!')

# Read data
data = ser.readline()

# Close the port
ser.close()
```
