# python 3.6
#https://www.emqx.com/en/blog/how-to-use-mqtt-in-python
#https://python.plainenglish.io/mqtt-beginners-guide-in-python-38590c8328ae
#https://raw.githubusercontent.com/E-t0m/zeroinput/main/zeroinput.py
import time
import json

from paho.mqtt import client as mqtt_client

#MQTT Broker Einstellungen
broker = '1883'
port = 
client_id = 'Powerhandler'
username = ''
password = ''


#Inverter Einstellungen
inverter_serial = ""
inverter_power_now = 0 #aktueller inverter_power_set des Inverters
inverter_power_set = 0 #Power des Inverters
inverter_power_setMqtt = 0 #inverter_power_set für MQTT
inverter_voltage = 0 #Volt an Batterie
max_power_limit = 600 #Maximalwert des Inverters
low_battery = 25.4 #Minimale Batteriespannung


send_history = []
powermeter_history = []

powermeter_value = 0 #Tesaurierter Wert am Stromzähler
power_status = 1


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def on_message_powermeter(client, userdata, msg):
    global powermeter_value
    try:
        unpacked_json = json.loads(msg.payload.decode('utf-8'))
    except Exception as e:
        print("Couldn't parse raw data: %s", e)
    try:
        powermeter_value = unpacked_json['SM']['16_7_0']
    except KeyError:
        pass

def on_message_hm_power(client, userdata, msg):
    global inverter_power_now
    try:
        inverter_power_now = json.loads(msg.payload.decode('utf-8'))
    except Exception as e:
        print("Couldn't parse raw data: %s", e)

def on_message_hm_voltage(client, userdata, msg):
    global inverter_voltage
    try:
        inverter_voltage = json.loads(msg.payload.decode('utf-8'))
    except Exception as e:
        print("Couldn't parse raw data: %s", e)

def on_message_hm_power_status(client, userdata, msg):
    global power_status
    try:
        power_status = json.loads(msg.payload.decode('utf-8'))
    except Exception as e:
        print("Couldn't parse raw data: %s", e)

def avg(inlist):	# return the average of a list variable
	if len(inlist) == 0: return(0)
	return( sum(inlist) / len(inlist) )

def history(value,liste):
    liste.append(value)
    if len(liste) > 4:
        liste.remove(liste[0])
    return(liste)

def main():

    client = connect_mqtt()
    client.message_callback_add('tele/stromzahler/SENSOR', on_message_powermeter)
    client.message_callback_add('tele/'+inverter_serial+'/status/limit_absolute', on_message_hm_power)
    client.message_callback_add('tele/'+inverter_serial+'/1/voltage', on_message_hm_voltage)
    client.message_callback_add('tele/'+inverter_serial+'/cmd/power', on_message_hm_power_status)

    client.loop_start()
    client.subscribe("tele/#")
    while True:

        time.sleep(10)
        print("Grid Wh",powermeter_value)
        print("Inverter Wh",inverter_power_now)
        print("Battery V",inverter_voltage)

        print("Power Status",power_status)

        print("Inverter Wh History",history(inverter_power_now,send_history))
        print("Grid Wh History",history(powermeter_value,powermeter_history))

        inverter_power_set = abs(avg(powermeter_history)+avg(send_history))

        if inverter_power_set <= max_power_limit:
            inverter_power_set = int(inverter_power_set)
        else:
            inverter_power_set = max_power_limit

        if abs(powermeter_value) > 5 and inverter_voltage >= low_battery and power_status == 1:
            inverter_power_setMqtt = str(inverter_power_set)
            print("Inverter set to",inverter_power_setMqtt)
            send = client.publish(topic='tele/'+inverter_serial+'/cmd/limit_nonpersistent_absolute',payload=inverter_power_setMqtt.encode('utf-8'),qos=0,)
            send.wait_for_publish()
            print("inverter set",send.is_published())


        if inverter_voltage >= low_battery and power_status == 0:
            shutdown = client.publish(topic='tele/'+inverter_serial+'/cmd/power',payload="1",qos=1,)
            shutdown.wait_for_publish()
            print("interver start due to battrerie voltage")#,shutdown.is_published())
        if inverter_voltage <= low_battery and power_status == 1: 
            shutdown = client.publish(topic='tele/'+inverter_serial+'/cmd/power',payload="0",qos=1,)
            shutdown.wait_for_publish()
            print("interver stop due to battrerie voltage",shutdown.is_published())

if __name__ == '__main__':
    main()
