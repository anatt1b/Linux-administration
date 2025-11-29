import paho.mqtt.client as mqtt
import json, time

BROKER = "86.50.22.163"
PORT = 1883
TOPIC = "chat/messages"

def send_message(nickname, text):
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    payload = json.dumps({
        "nickname": nickname,
        "text": text,
        "clientId": f"py_{int(time.time())}",
        "timestamp": int(time.time() * 1000)
    })
    client.publish(TOPIC, payload)
    client.disconnect()
send_message("Käyttäjä", "Hei kaikille!")