#!/usr/bin/env python3
import requests 
import mysql.connector
from datetime import datetime

#API-asetukset
API_KEY = 'YOUR_API_KEY'
CITY = 'Kempele'
URL = f'https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric'

# MYSQL tietokantayhteys
conn = mysql.connector.connect(
    host='localhost',
    user='saamies',
    password='Säämies123!'
    database='weather_db'
)
cursor = conn.cursor()

# Luodaan taulu jos sitä ei jo ole
cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather_data
               (
               id INT AUTO_INCREMENT PRIMARY KEY,
               city VARCHAR (50),
               temperature FLOAT,
               description VARCHAR(100),
               timestamp DATETIME
               )
               
''')

# haetaan säädata OpenWeatherista
response = requests.get(URL)
data = response.json()

# Poimitaan halutut arvot
temp = data['main']['temp']
desc = data['weather'][0]['description']
timestamp = datetime.now()

# Tallennetaan tiedot tietokantaan
cursor.execute('INSERT INTO weather_data (city, temperature, description, timestamp) VALUES (%s,%s,%s,%s)', (CITY, temp, desc, timestamp))

conn.commit()
cursor.close()
conn.close()

print(f'Data tallennettu: {CITY} {temp}°C {desc}')