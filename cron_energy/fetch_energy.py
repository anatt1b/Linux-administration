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

# Luodaan taulu jos ei ole olemassa
cursor.execute("""
CREATE TABLE IF NOT EXISTS sahkonhinta(
    id INT AUTO_INCREMENT PRIMARY KEY,
    hinta_eur_mwh FLOAT,
    hinta_sentit_kwh FLOAT,
    start_time DATETIME,
    end_time DATETIME,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Hae data API:sta
r = requests.get(URL)
r.raise_for_status()
data = r.json()

prices = data["prices"]          # lista objekteja

# --- Otetaan vain uusin tunti ---
latest = prices[-1]

start = datetime.fromisoformat(latest["startDate"])
end = datetime.fromisoformat(latest["endDate"])
cents_kwh = float(latest["price"])
eur_mwh = cents_kwh * 10   # muutos €/MWh -> snt/kWh

# Tarkistetaan onko tämä tunti jo tietokannassa
cursor.execute(
    "SELECT COUNT(*) FROM sahkonhinta WHERE start_time = %s",
    (start,)
)
exists = cursor.fetchone()[0] > 0

if not exists:
    cursor.execute(
        """
        INSERT INTO sahkonhinta (hinta_eur_mwh, hinta_sentit_kwh, start_time, end_time)
        VALUES (%s, %s, %s, %s)
        """,
        (eur_mwh, cents_kwh, start, end)
    )
    conn.commit()
    print("Tallennettu 1 uusi hinta.")
else:
    print("Uusin hinta on jo tietokannassa, ei lisätty uutta riviä.")

cursor.close()
conn.close()
