#!/usr/bin/env python3
import serial
import csv
import time
import re
import os
import json
import mqtt
import datetime as datetime

SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200
CONFIG_FILE = 'headers.csv'

def load_sensor_headers(file_path):
    """Opens the CSV file and maps Sensor IDs to their respective header list."""
    sensor_map = {}
    if not os.path.exists(file_path):
        print(f"Error: Configuration file '{file_path}' not found!")
        return sensor_map

    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:  # Skip empty lines
                sensor_id = row[0].strip()
                headers = [h.strip() for h in row[1:]]  # Everything after the ID
                sensor_map[sensor_id] = headers
    return sensor_map

print("Initializing Sensor Metadata Lookup Engine...")
sensor_headers = load_sensor_headers(CONFIG_FILE)
print(f"Loaded configurations for Sensor IDs: {list(sensor_headers.keys())}")

try:
    time.sleep(10)
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Stability pause
    print(f"Listening for unified Pico packets on {SERIAL_PORT}...")

    while True:
        if ser.in_waiting > 0:
            # 1. Read the combined byte-stream line sent by the Pico
            json_packet = ser.readline()
            print("readline:", json_packet)
            try:
                json_payload = json.loads(json_packet)
            except:
                print(json_packet)
                continue
            try:
                #json_payload = json.loads(json_packet)
                data_string = json_payload["raw_sdi12_string"]
                print(data_string)
           # line_text = raw_line_bytes.decode('utf-8').strip()

                if len(data_string) > 8:
                    match = re.search(r'[+-]', data_string)
                    # 2. Extract the Sensor ID (the very first character, e.g., '0')
                    if match:
                        split_index = match.start()
                        sensor_id = data_string[:split_index]
                        raw_values = data_string[split_index:]

                    # 3. Parse out all the floats from the rest of the stream
                    parsed_numbers = re.findall(r'[+-]\d*\.\d+|[+-]\d+', raw_values)
                    float_values = [float(val) for val in parsed_numbers]

                    print(f"\n[{time.strftime('%H:%M:%S')}] Packet Received for ID: '{sensor_id}'")

                    # 4. Retrieve the matching header row from our dictionary lookup
                    if sensor_id in sensor_headers:
                        matched_headers = sensor_headers[sensor_id]

                        # 5. Zip and match the header labels with the parsed floats
                        # This builds a clean dictionary: {'temperature_c': 23.45, 'moisture_pct': 12.8}
                        if len(matched_headers) == len(float_values):
                            paired_data = {}
                            #paired_data["sensor_id"] = sensor_id
                            paired_data = dict(zip(matched_headers, float_values))
                            paired_data["Sensor_id"] = sensor_id
                            paired_data["Timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            try:
                                mqtt.send_message(paired_data)

                            except Exception as e:
                                print("Mqtt Error:", e)

                            print(f"  ✅ SUCCESS: Match found for Sensor {sensor_id}")
                            for metric, value in paired_data.items():
                                print(f"    -> {metric}: {value}")
                        else:
                            print(f"  ⚠️ WARNING: Length mismatch for Sensor {sensor_id}!")
                            print(f"    Expected headers ({len(matched_headers)}): {matched_headers}")
                            print(f"    Received values  ({len(float_values)}): {float_values}")
                    else:
                        print(f"  ❌ ERROR: No header profile found in {CONFIG_FILE} for Sensor ID '{sensor_id}'")
                        print(f"    Raw unmapped numeric data: {float_values}")

                    print("-" * 50)
            except json.JSONDecodeError:
                print(f"Warning: corrupted or non-json packet dropped:", datetime.datetime.now(), json_packet)
            except UnicodeDecodeError:
                print(f"Failed to decode bytes")

        time.sleep(0.1)

except serial.SerialException:
    print("USB Connection lost. Is the Pico unplugged?")
except KeyboardInterrupt:
    print("\nExiting Telemetry Engine.")
    if 'ser' in locals() and ser.is_open:
        ser.close()
