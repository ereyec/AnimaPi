
#!/usr/bin/env python3
"""
Read temperature and humidity from DFRobot SEN0137 (DHT22 module) on Raspberry Pi.
Uses Adafruit_DHT library inside a virtual environment.

- Sensor: SEN0137 (DHT22-based)
- Connection: DATA line to a Raspberry Pi GPIO (BCM numbering)
"""

import time
import adafruit_dht  # Installed in your .venv

# Correct sensor type: DHT22 for SEN0137
SENSOR = adafruit_dht.DHT22

# BCM GPIO number where the DATA pin of SEN0137 is connected
DHT_PIN = 4  # You said you're using GPIO4 (physical pin 7)


def read_sensor():
    """
    Read from DHT22 sensor and return (humidity, temperature_celsius).

    Returns:
        (humidity, temperature_c) where:
        - humidity is in %RH
        - temperature_c is in °C
        If the read fails, both values may be None.
    """
    humidity, temperature_c = adafruit_dht.read_retry(SENSOR, DHT_PIN)
    return humidity, temperature_c


def main():
    print("Starting SEN0137 (DHT22) reader. Press Ctrl+C to stop.\n")

    while True:
        humidity, temperature_c = read_sensor()

        if humidity is None or temperature_c is None:
            print("Failed to get reading. Trying again...")
        else:
            temperature_f = temperature_c * 9 / 5 + 32
            print(
                f"Temp: {temperature_c:5.1f} °C / {temperature_f:5.1f} °F  |  "
                f"Humidity: {humidity:5.1f} %RH"
            )

        time.sleep(2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
