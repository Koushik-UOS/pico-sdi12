import paho.mqtt.client as mqttc
import time
import ssl
import calendar
import datetime
import json
import random
from ssl import SSLContext, PROTOCOL_TLS_CLIENT, CERT_REQUIRED
from csv import writer

def on_connect(client, userdata, flags, rc):
        print("Code:",flags,rc)

def on_message(client,userdata,msg):
        print("error"+msg.topic+" "+str(msg.payload))

def on_log(client,userdata,level,buf):
        print("log:",buf)

def send_message(message):

    client=mqttc.Client(client_id='Base_test', protocol=mqttc.MQTTv311, transport="tcp")
    client.on_log=on_log
    client.on_connect=on_connect
    client.on_message=on_message
    print("Mqtt Block 1")
    username='4eraiothub.azure-devices.net/Base_test/?api-version=2021-04-12'
    password='SharedAccessSignature sr=4eraiothub.azure-devices.net%2Fdevices%2FBase_test&sig=PN0lpYUTfYwwmyqD9%2BAU566X8DlYbZNdSwqkhq%2FEtrY%3D&se=1821696533'
    host='4eraiothub.azure-devices.net'
    password='SharedAccessSignature sr=4eraiothub.azure-devices.net%2Fdevices%2FBase_test&sig=PN0lpYUTfYwwmyqD9%2BAU566X8DlYbZNdSwqkhq%2FEtrY%3D&se=1821696533'
    host='4eraiothub.azure-devices.net'
    print("Mqtt Block 2")

    client.username_pw_set(username=username,password=password)
    ssl_context=SSLContext(protocol=PROTOCOL_TLS_CLIENT)
    ssl_context.load_default_certs()
    ssl_context.verify_mode=CERT_REQUIRED
    ssl_context.check_hostname=True
    client.tls_set_context(context=ssl_context)
    client.connect(host,8883,120)
    print("Mqtt Block 3")

    time.sleep(2)
    exp=datetime.datetime.utcnow()
    #abcstring1={"Hi Matthew":random.randint(0,100)}
    data_out1=json.dumps(message)
    flag=client.publish("devices/Base_test/messages/events/", payload=data_out1, qos=0, retain=True)
    print(data_out1)
    FLAG=flag.next()
    print(FLAG)
    time.sleep(2)
    client.disconnect()
    return FLAG

def csv(List):
    with open('senseh2o_trilux.csv', 'a') as f_object:

    # Pass this file object to csv.writer()
    # and get a writer object
        writer_object = writer(f_object)

        # Pass the list as an argument into
        # the writerow()
        writer_object.writerow(List)

        # Close the file object
        f_object.close()
