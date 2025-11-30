#!/usr/bin/env python3

"""
MQTT to MySQL Logger
Kuuntelee MQTT-viestejä ja tallentaa ne tietokantaan.
"""

import json
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
import mysql.connector
from mysql.connector import pooling

# Konfiguraatio
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "chat/messages"

DB_CONFIG = {
    "host": "localhost",
    "user": "mqtt_user",
    "password": "Salasana123!", # Vaihda!
    "database": "mqtt_chat"
}

# Lokitus
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
def save_message(nickname, message, client_id):
    """ Tallenna viesti tietokantaan. """
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        query = '''
        INSERT INTO messages (nickname, message, client_id)
        VALUES (%s, %s, %s)
        '''
        cursor.execute(query, (nickname, message, client_id))
        conn.commit()
        logger.info(f"Tallennettu: [{nickname}] {message[:50]}...")
    except mysql.connector.Error as err:
        logger.error(f"Tietokantavirhe: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
def on_connect(client, userdata, flags, rc):
    """MQTT-yhteys muodostettu."""
    if rc == 0:
        logger.info("Yhdistetty MQTT-brokeriin")
        client.subscribe(MQTT_TOPIC)
        logger.info(f"Tilattu: {MQTT_TOPIC}")
    else:
        logger.error(f"Yhteysvirhe, koodi: {rc}")
        
def on_message(client, userdata, msg):
    """Käsittele saapuva MQTT-viesti."""
    try:
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        nickname = data.get('nickname', 'Tuntematon')[:50]
        message = data.get('text', '')
        client_id = data.get('clientId', '')[:100]
        if message:
            save_message(nickname, message, client_id)
    except json.JSONDecodeError:
        logger.warning(f"Virheellinen JSON: {msg.payload}")
    except Exception as e:
        logger.error(f"Virhe: {e}")
        
def main():
    """Pääohjelma."""
    logger.info("MQTT Logger käynnistyy...")
    
    # Testaa tietokantayhteys
    try:
        conn = db_pool.get_connection()
        conn.close()
        logger.info("Tietokantayhteys OK")
    except mysql.connector.Error as err:
        logger.error(f"Ei yhteyttä tietokantaan: {err}")
        return
if __name__ == "__main__":
    main()