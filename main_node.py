from sx1262 import SX1262
from machine import UART,Pin
import time
import utime
import machine
import LoRaWANHandler
from LoRaConfig import LoRaConfig
import sys
import json

wake_pin = machine.Pin(28, machine.Pin.IN)

def process_data(raw_sensor_bytes):
    
    print("Pico Raw Byte Data Handler Ready...")
    #raw_sensor_bytes = b'0+23.45+12.80\r\n'
    
    try:
        # 1. Decode the raw bytes into a standard text string
        #decoded_string = raw_sensor_bytes.decode('utf-8')
        
        # 2. Strip out trailing carriage returns (\r) and newlines (\n)
        clean_string = raw_sensor_bytes.strip()
        
        cleaner_string = clean_string[1:]
        
        print(cleaner_string)
        return cleaner_string
            
    except Exception as e:
        
        print("Error", str(e))
           
    time.sleep(5)
    
def measure(data):
    
    print("Begin measure cycle")
    try:
        uart0.write(b'0M!')
        time.sleep(2)
        M_info = uart0.read(uart0.any())
        print(M_info)
        data = data+M_info[:1]
        time.sleep(15)
        
        uart0.write(b'0D0!')
        time.sleep(2)
        data0 = uart0.read(uart0.any())
        data = data+process_data(data0[1:])
        
        uart0.write(b'0D1!')
        time.sleep(2)
        data1 = uart0.read(uart0.any())
        data = data+process_data(data1)
        
        print(data)
        return data
    
    except Exception as e:
        print("No data from sensor and error:", str(e))
        data = b'KN001_0+1.232-234.2+11.09+46.69'
        return data
    
def send_message_usb(data):
    
    try:
        
        final_string = data.decode('utf-8')
        # 3. Pack the cleaned string into your JSON structure
        telemetry_data = {
            "timestamp_ms": time.ticks_ms(),
            "raw_sdi12_string": final_string,
            "status": "OK"
        }
        # 4. Turn the dictionary into a JSON string and push it out the USB link
        json_payload = json.dumps(telemetry_data)
        sys.stdout.write(json_payload + "\n")
        print("Message sent usb")
        
    except Exception as e:
        # Handle cases where corruption happens mid-transmission
        error_payload = json.dumps({"status": "ERROR", "message": str(e)})
        sys.stdout.write(error_payload + "\n")
    
def send_message_lora(data):
    try:
        sx.send(data)
        print("Message sent lora")
        
    except Exception as e:
        print("Lora error:", str(e))    

def send_message_lorawan(data):
    try:
        final_string = data.decode('utf-8')
        lh.send(data, False)
        print("Message sent lorawan")
    
    except Exception as e:
        print("Lorawan error:", str(e))

def wake_pi():
    print("waking up pi 5")
    wake_pin.init(mode=machine.Pin.OUT, value=0)
    time.sleep(0.5)
    wake_pin.init(mode=machine.Pin.IN)
    time.sleep(65)
    

def cb(events):
    if events & SX1262.RX_DONE:
        msg, err = sx.recv()
        if msg:
            error = SX1262.STATUS[err]
            print('Receive: {}, {}'.format(msg, error))
            
            if msg == b'wake':
                #wake_pi()
                print("waking")
            else:
                send_message_usb(msg)
                print("comms with pi zero",msg)
    elif events & SX1262.TX_DONE:
        print('TX done.')

#Block: Protocol
#var = {"A1":5,"M1":5}
print("Intializing UART connections")
uart0 = UART(0,baudrate=9600,tx=Pin(0),rx=Pin(1))
print(uart0)
time.sleep(1)
# uart1 = UART(1,baudrate=9600,tx=Pin(4),rx=Pin(5))
# print(uart1)

uart0.write(b'zI!')
time.sleep(5)
mod_name = uart0.read(uart0.any())
print(mod_name)
if len(mod_name) > 2:
    print("SDI Module detected")

else:
    print("SDI Module error")

time.sleep(5)

print("Intializing Lora connections")

sx = SX1262(spi_bus=1, clk=10, mosi=11, miso=12, cs=3, irq=20, rst=15, gpio=2)

# LoRa
sx.begin(freq=868, bw=500.0, sf=12, cr=8, syncWord=0x12,
         power=-5, currentLimit=60.0, preambleLength=8,
         implicit=False, implicitLen=0xFF,
         crcOn=True, txIq=False, rxIq=False,
         tcxoVoltage=1.7, useRegulatorLDO=False, blocking=True)

sx.setBlockingCallback(False, cb)
#sx.send(b'Header?')
utime.sleep_ms(5000)

#print("Intializing Lorawan connections")
#lh = LoRaWANHandler.LoRaWANHandler(LoRaConfig)
#utime.sleep_ms(5000)
#lh.otaa()

print("Start Loop every 15 minutes")

while(True):
    data = b'KN002_'
    
    data = measure(data)
    
    print("Message Send phase")
    
    send_message_usb(data)
    
    #send_message_lora(data)
    
    #send_message_lorawan(data)
    
    time.sleep(900)
#     timer = Pin(21, Pin.OUT)
#     timer.value(0)
#     time.sleep(5)
#     print("Timer trigger")
#     timer.value(1)
    
