#!/usr/bin/python3

import uuid
import time
import Adafruit_BluefruitLE
import philble.client
import paho.mqtt.client as mqtt

# TODO: handle disconnects and publish state


mqtt_client = mqtt.Client()
ble = Adafruit_BluefruitLE.get_provider()
ble_client = None

TOPIC = "hue-1"
TEMP_TOPIC = f"{TOPIC}/temp"
RGB_TOPIC = f"{TOPIC}/color"
SWITCH_TOPIC = f"{TOPIC}/switch"
BRIGHTNESS_TOPIC = f"{TOPIC}/brightness"


def on_message(mqtt_client, userdata, msg):
    try:
        if ble_client is None:
            print("BLE not initialized")
        elif msg.topic == TEMP_TOPIC:
            print(f"Changing temperature to {msg.payload}")
            ble_client.temperature(int(msg.payload))
        elif msg.topic == SWITCH_TOPIC:
            print(f"Setting switch to {msg.payload}")
            ble_client.power("on" in msg.payload.decode('UTF-8').lower())
        elif msg.topic == RGB_TOPIC:
            hexstr = ''.join(map(lambda x: format(int(x), 'x'), msg.payload.decode('UTF-8').split(',')))
            print(f"Changing color to {hexstr}")
            ble_client.color(hexstr)
        elif msg.topic == BRIGHTNESS_TOPIC:
            print(f"Changing brightness to {msg.payload}")
            ble_client.brightness(int(msg.payload))
    except Exception as e:
        print(f"Error: {str(e)}")


def on_connect(mqtt_client, userdata, flags, rc):
    print("Connected to MQTT")
    mqtt_client.subscribe(TEMP_TOPIC)
    mqtt_client.subscribe(RGB_TOPIC)
    mqtt_client.subscribe(BRIGHTNESS_TOPIC)
    mqtt_client.subscribe(SWITCH_TOPIC)


def main():
    print('Discovering Hue...')
    ble.clear_cached_data()
    adapter = ble.get_default_adapter()
    adapter.power_on()
    adapter.start_scan()
    device = ble.find_device()
    adapter.stop_scan()
    print('Discovered')

    time.sleep(.5)
    global ble_client
    ble_client = philble.client.Client(device)

    # blink
    ble_client.power(False);
    time.sleep(.5)
    ble_client.power(True);
    time.sleep(.5)
    ble_client.power(False);

    print("Starting MQTT loop")
    mqtt_client.loop_forever()


# mqtt init
mqtt_client.on_message = on_message
mqtt_client.on_connect = on_connect
mqtt_client.connect("server-m", 1883, 60)

# ble init
ble.initialize()

# starting point
ble.run_mainloop_with(main)
