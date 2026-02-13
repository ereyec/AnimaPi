#!/usr/bin/env python3
"""
TSL2591 Lux Sensor Reader for Raspberry Pi (I2C SDA/SCL)
Works great with Qwiic connector (JST-SH) wired to Pi I2C pins.

Reads:
- Lux (calculated by library)
- Raw Full Spectrum
- Raw Infrared
- Visible (Full - IR)

Install:
  pip3 install adafruit-blinka adafruit-circuitpython-tsl2591
Enable I2C:
  sudo raspi-config -> Interface Options -> I2C
"""

import time
import board
import busio
import adafruit_tsl2591

def main():
    # Create I2C bus using Raspberry Pi hardware SDA/SCL (GPIO2/GPIO3)
    i2c = busio.I2C(board.SCL, board.SDA)

    # Create sensor instance
    sensor = adafruit_tsl2591.TSL2591(i2c)

    # Optional tuning:
    # Gain options: LOW, MED, HIGH, MAX
    # Integration time options depend on library; common values are 100ms, 200ms, 300ms, 400ms, 500ms, 600ms
    #
    # If you're measuring bright light, use LOW gain.
    # In dim environments, try HIGH or MAX gain.
    #
    # Uncomment to set:
    # sensor.gain = adafruit_tsl2591.GAIN_LOW
    # sensor.integration_time = adafruit_tsl2591.INTEGRATIONTIME_200MS

    print("TSL2591 detected. Reading... (Ctrl+C to stop)\n")

    while True:
        try:
            lux = sensor.lux
            full = sensor.full_spectrum
            ir = sensor.infrared
            visible = full - ir

            print(f"Lux: {lux:8.2f}  Full: {full:6d}  IR: {ir:6d}  Visible: {visible:6d}")
            time.sleep(1.0)

        except OSError as e:
            # Often indicates I2C bus issue or loose wire
            print(f"I2C read error: {e}. Retrying...")
            time.sleep(1.0)

        except KeyboardInterrupt:
            print("\nStopped.")
            break

if __name__ == "__main__":
    main()