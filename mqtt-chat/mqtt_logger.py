#!/usr/bin/env python3
'''
MQTT to MySQL Logger
Kuuntelee MQTT-viestejä ja tallentaa ne tietokantaan.
'''

import json
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
import mysql.connector
from mysql.connector import pooling

# konfiguraatio
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'chat/messages'

DB_CONFIG = {
    'host': 'localhost',
    'user': 'mqtt_user',
    'password': 'Salasana123!',
    'database': 'mqtt_chat'
}

# lokitus
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Tietokantapooli
db_pool = pooling.MySQLConnectionPool(
    pool_name="mqtt_pool",
    pool_size=5,
    **DB_CONFIG
)

def save_message(nickname, message, clinet_id):
    '''Tallentaa viestin tietokantaan'''
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        query = '''
        INSERT INTO messages (nickname, message, client_id) VALUES (%s, %s, %s)
        '''
        cursor.execute(query, (nickname, message, clinet_id))
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"Viesti tallennettu: [{nickname}]  {message[:50]}...")
    except mysql.connector.Error as err:
        logger.error(f"Tietokantavirhe: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
def on_connect(client, userdata, flags, rc):
    '''Yhdistetty MQTT-välittäjään'''
    if rc == 0:
        logger.info("Yhdistetty MQTT-välittäjään")
        client.subscribe(MQTT_TOPIC)
        logger.info(f"Tilattu aihe: {MQTT_TOPIC}")
    else:
        logger.error(f"Yhdistäminen epäonnistui, koodi: {rc}")
        
def on_message(client, userdata, msg):
    '''Käsittelee saapuvat MQTT-viestit'''
    try:
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        nickname = data.get('nickname', 'Tuntematon')[:50]
        message = data.get('text', '')
        client_id = data.get('client_id', '')[:100]
        if message:
            save_message(nickname, message, client_id)
    except json.JSONDecodeError:
        logger.warning("Virhellinen JSON: (msg.payload)")
    except Exception as e:
        logger.error(f"Virhe viestin käsittelyssä: {e}")
        
def main():
    '''Pääohjelma'''
    logger.info("MQtt-logger käynnistyy...")
    
    #testaa tietokantayhteys
    try:
        conn = db_pool.get_connection()
        conn.close()
        logger.info("Yhdistetty tietokantaan onnistuneesti")
    except mysql.connector.Error as err:
        logger.error(f"Tietokantayhteyden testaus epäonnistui: {err}")
        return
    
    #MQTT-asiakas
    client = mqtt.Client(client_id="mqtt_logger")
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forver()
    except KeyboardInterrupt:
        logger.info("Sammutetaan MQTT-logger...")
        client.disconnect()
    
    if __name__ == '__main__':
        main()