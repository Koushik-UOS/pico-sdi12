from sx1262 import SX1262
from machine import UART,Pin
import time
import utime
import machine
import LoRaWANHandler
from LoRaConfig import LoRaConfig

def process_msg(msg):
    print(msg)
    msg = msg.decode('utf-8')
    m = msg.split(',')
    for i in m:
        print(i)
        i = i.split(":")
        var[i[0]] = float(i[1])
    
def cb(events):
    if events & SX1262.RX_DONE:
        msg, err = sx.recv()
        if msg:
            error = SX1262.STATUS[err]
            print('Receive: {}, {}'.format(msg, error))
            process_msg(msg)
            
            time.sleep(var["M1"])
            uart0.write(b'0M!')
            time.sleep(2)
            M_info = uart0.read(uart0.any())
            print(M_info)
            time.sleep(15)
            
            uart0.write(b'0D0!')
            time.sleep(2)
            data0 = uart0.read(uart0.any())
            
            uart0.write(b'0D1!')
            time.sleep(2)
            data1 = uart0.read(uart0.any())
            
            print(data0,data1)

            sx.send(data0)
            time.sleep(5)
            sx.send(data1)
    elif events & SX1262.TX_DONE:
        print('TX done.')

#Block: Protocol
var = {"A1":5,"M1":5}
uart0 = UART(0,baudrate=9600,tx=Pin(0),rx=Pin(1))
print(uart0)
uart0.write(b'zI!')
time.sleep(5)
mod_name = uart0.read(uart0.any())
print(mod_name)
if len(mod_name) > 2:
    print("Sdi Module detected")


sx = SX1262(spi_bus=1, clk=10, mosi=11, miso=12, cs=3, irq=20, rst=15, gpio=2)

# LoRa
sx.begin(freq=868, bw=500.0, sf=12, cr=8, syncWord=0x12,
         power=-5, currentLimit=60.0, preambleLength=8,
         implicit=False, implicitLen=0xFF,
         crcOn=True, txIq=False, rxIq=False,
         tcxoVoltage=1.7, useRegulatorLDO=False, blocking=True)

# def begin(self, freq=868.3, bw=250.0, sf=7, cr=5, syncWord=SX126X_SYNC_WORD_PRIVATE,
#               power=14, currentLimit=60.0, preambleLength=8, implicit=False, implicitLen=0xFF,
#               crcOn=True, txIq=False, rxIq=False, tcxoVoltage=1.6, useRegulatorLDO=False,
#               blocking=True):
#         state = super().begin(bw, sf, cr, syncWord, currentLimit, preambleLength, tcxoVoltage, useRegulatorLDO, txIq, rxIq)
#         ASSERT(state)
# # FSK
##sx.beginFSK(freq=923, br=48.0, freqDev=50.0, rxBw=156.2, power=-5, currentLimit=60.0,
##            preambleLength=16, dataShaping=0.5, syncWord=[0x2D, 0x01], syncBitsLength=16,
##            addrFilter=SX126X_GFSK_ADDRESS_FILT_OFF, addr=0x00, crcLength=2, crcInitial=0x1D0F, crcPolynomial=0x1021,
##            crcInverted=True, whiteningOn=True, whiteningInitial=0x0100,
##            fixedPacketLength=False, packetLength=0xFF, preambleDetectorLength=SX126X_GFSK_PREAMBLE_DETECT_16,
##            tcxoVoltage=1.6, useRegulatorLDO=False,
##            blocking=True)

sx.setBlockingCallback(False, cb)

lh = LoRaWANHandler.LoRaWANHandler(LoRaConfig)
#blink(3, 1000)
utime.sleep_ms(5000)
lh.otaa()
#blink(3, 1000)
utime.sleep_ms(5000)
while(True):
    #meas = SCC.measurementSCC(i2c)
    print("Begin")
    uart0.write(b'0M!')
    time.sleep(2)
    M_info = uart0.read(uart0.any())
    print(M_info)
    time.sleep(15)
    
    uart0.write(b'0D0!')
    time.sleep(2)
    data0 = uart0.read(uart0.any())
    
    uart0.write(b'0D1!')
    time.sleep(2)
    data1 = uart0.read(uart0.any())
    
    print(data0,data1)
    
    #data0=data0+data1

    #sx.send(data0)
    #time.sleep(5)
    #sx.send(data1)
    print("Message Send phase")
    meas = [0,1,2]
    msg = str(data0)
    #print(msg)
    lh.send(msg, False)
    utime.sleep_ms(3000)
    msg = str(data1)
    #print(msg)
    lh.send(msg, False)
    #blink(2, 2000)
    utime.sleep_ms(850000)
 #   machine.deepsleep(60000*15)