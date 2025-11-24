#!/usr/bin/env python3

import requests
import mysql.connector
from datetime import datetime

URL = "https://api.porssisahko.net/v2/latest-prices.json"

conn = mysql.connector.connect(
    host="localhost",
    user="sahkonseuraaja",
    password="Kekkonen11!",
    database="energy_db"
)

cursor = conn.cursor()

cursor.execute("""
               CREATE TABLE IF NOT EXISTS sahkonhinta(
               id INT AUTO_INCREMENT PRIMARY KEY,
               hinta_eur_mwh FLOAT,
               hinta_sentit_kwh FLOAT,
               start_time DATETIME,
               end_time DATETIME,
               updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
               """)

# Hae data

r = requests.get(URL)
r.raise_for_status()
data = r.json()

prices = data["prices"]  # lista objekteja

inserted = 0

for p in prices:
    start = datetime.fromisoformat(p["startDate"])
    end = datetime.fromisoformat(p["endDate"])
    eur_mwh = float(p["price"])
    cents_kwh = eur_mwh / 10 # muutos €/MWh -> snt/KWh

    cursor.execute("""
                   INSERT INTO sahkonhinta (hinta_eur_mwh, hinta_sentit_kwh, start_time, end_time)
                   VALUES(%s, %s, %s, %s)
                   """, (eur_mwh, cents_kwh, start, end))
    inserted += 1

conn.commit()
cursor.close()
conn.close()

print(f"Tallennettu {inserted} hintaa.")