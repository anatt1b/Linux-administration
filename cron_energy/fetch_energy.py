#!/usr/bin/env python3

import requests
import mysql.connector
from datetime import datetime

URL = "https://api.porssisahko.net/v2/latest-prices.json"

# MySQL-yhteys
conn = mysql.connector.connect(
    host="localhost",
    user="sahkonseuraaja",
    password="Kekkonen11!",
    database="energy_db"
)
cursor = conn.cursor()

# Luodaan taulu jos ei ole olemassa
cursor.execute("""
CREATE TABLE IF NOT EXISTS sahkonhinta(
    id INT AUTO_INCREMENT PRIMARY KEY,
    hinta_eur_mwh FLOAT,
    hinta_sentit_kwh FLOAT,
    start_time DATETIME UNIQUE,
    end_time DATETIME,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
)
""")

# Haetaan data API:sta
r = requests.get(URL)
r.raise_for_status()
data = r.json()
prices = data["prices"]      # lista tunneista / 15 min jaksoista
print("DEBUG, latest item from API:", prices[-1])

inserted = 0

for p in prices:
    # API antaa ajat muodossa 2025-11-24T17:00:00Z (UTC)
    start = datetime.fromisoformat(p["startDate"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(p["endDate"].replace("Z", "+00:00"))
    eur_mwh = float(p["price"])
    cents_kwh = eur_mwh / 10.0  # €/MWh -> snt/kWh

    # Tarkistetaan onko tämä jakso jo taulussa
    cursor.execute(
        "SELECT COUNT(*) FROM sahkonhinta WHERE start_time = %s",
        (start,)
    )
    exists = cursor.fetchone()[0] > 0
    if exists:
        continue

    # Lisätään uusi jakso
    cursor.execute("""
        INSERT INTO sahkonhinta (hinta_eur_mwh, hinta_sentit_kwh, start_time, end_time)
        VALUES (%s, %s, %s, %s)
    """, (eur_mwh, cents_kwh, start, end))
    inserted += 1

conn.commit()
cursor.close()
conn.close()

print(f"Tallennettu {inserted} uutta hintaa.")