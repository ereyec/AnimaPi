
#!/usr/bin/env python3
"""
pmon_reader.py — MonkMakes Plant Monitor reader for Raspberry Pi (Zero 2 W friendly)

- Protocol: 9600 baud, 8N1. Send single-letter commands; replies are ASCII lines ending in \n.
  Commands: w (moisture %), t (temp C), h (humidity %), j (JSON of all), L (LED on), l (LED off), v (version)
  Source: MonkMakes Plant Monitor datasheet / Adafruit guide.

Usage examples:
  python3 pmon_reader.py                      # poll every 2s, print to stdout
  python3 pmon_reader.py --period 5 --csv readings.csv
  python3 pmon_reader.py --led on             # turn LED on then start polling
"""

import argparse, json, sys, time
import serial
from serial.serialutil import SerialException

def open_port(port, baud, timeout):
    return serial.Serial(
        port=port, baudrate=baud,
        bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
        timeout=timeout, write_timeout=timeout, xonxoff=False, rtscts=False, dsrdtr=False
    )

def send_cmd(ser, ch):
    # Commands are single letters, no newline required.
    ser.write(ch.encode("ascii"))
    ser.flush()

def read_line(ser):
    line = ser.readline()
    if not line:
        return None
    # Replies end with \n; often include \r\n
    return line.decode("utf-8", errors="replace").strip()

def parse_eq(line, key):
    # expects like 'w=55' or 't=21.37' or 'h=48.5'
    if not line or "=" not in line:
        return None
    k, v = line.split("=", 1)
    if k != key:
        return None
    try:
        return float(v)
    except ValueError:
        return None

def read_all(ser):
    """
    Try JSON first (command 'j'). If that fails, fall back to w/t/h commands.
    Returns dict: {'moisture_pct': float, 'temp_c': float, 'humidity_pct': float}
    """
    # Try JSON one-shot
    send_cmd(ser, "j")
    line = read_line(ser)
    if line:
        try:
            obj = json.loads(line)
            # Datasheet example uses keys 'wetness' (raw), 'humidity', 'temp'
            moisture_pct = None  # not in JSON; use 'w' for % moisture
            temp_c = float(obj.get("temp")) if obj.get("temp") is not None else None
            humidity_pct = float(obj.get("humidity")) if obj.get("humidity") is not None else None
            # Get moisture % separately
            send_cmd(ser, "w")
            wline = read_line(ser)
            w = parse_eq(wline, "w")
            if w is not None:
                moisture_pct = w
            if temp_c is not None and humidity_pct is not None and moisture_pct is not None:
                return {"moisture_pct": moisture_pct, "temp_c": temp_c, "humidity_pct": humidity_pct}
        except json.JSONDecodeError:
            pass

    # Fallback: query individually
    vals = {}
    for key in ("w", "t", "h"):
        send_cmd(ser, key)
        line = read_line(ser)
        val = parse_eq(line, key)
        if val is None:
            return None
        vals[key] = val

    return {"moisture_pct": vals["w"], "temp_c": vals["t"], "humidity_pct": vals["h"]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="/dev/serial0")
    ap.add_argument("--baud", type=int, default=9600)
    ap.add_argument("--timeout", type=float, default=0.5)
    ap.add_argument("--period", type=float, default=2.0, help="Seconds between polls")
    ap.add_argument("--csv", default=None, help="Optional CSV file to append readings")
    ap.add_argument("--led", choices=["on", "off"], default=None, help="Control onboard LED at start")
    args = ap.parse_args()

    ser = None
    try:
        ser = open_port(args.port, args.baud, args.timeout)
        # Clear any stale buffered bytes
        ser.reset_input_buffer(); ser.reset_output_buffer()

        if args.led is not None:
            send_cmd(ser, "L" if args.led == "on" else "l")
            # No response expected

        # Optional: print version
        send_cmd(ser, "v")
        vline = read_line(ser)
        if vline:
            print(f"# Firmware version: {vline}", file=sys.stderr)

        # CSV header
        if args.csv:
            try:
                with open(args.csv, "a", encoding="utf-8") as f:
                    if f.tell() == 0:
                        f.write("timestamp_iso,moisture_pct,temp_c,humidity_pct\n")
            except Exception as e:
                print(f"# CSV open error: {e}", file=sys.stderr)

        while True:
            reading = read_all(ser)
            ts = time.strftime("%Y-%m-%dT%H:%M:%S")
            if reading:
                msg = (f"{ts}  moisture={reading['moisture_pct']:.1f}%  "
                       f"temp={reading['temp_c']:.2f}°C  humidity={reading['humidity_pct']:.2f}%")
                print(msg, flush=True)
                if args.csv:
                    try:
                        with open(args.csv, "a", encoding="utf-8") as f:
                            f.write(f"{ts},{reading['moisture_pct']:.1f},{reading['temp_c']:.2f},{reading['humidity_pct']:.2f}\n")
                    except Exception as e:
                        print(f"# CSV write error: {e}", file=sys.stderr)
            else:
                print(f"{ts}  read error", file=sys.stderr)

            time.sleep(max(0.05, args.period))

    except (SerialException, OSError) as e:
        print(f"# Serial error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    finally:
        if ser and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
