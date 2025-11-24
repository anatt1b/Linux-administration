#!/usr/bin/env python3

import requests
import mysql.connector
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

URL = "https://api.porssisahko.net/v2/latest-prices.json"

# --- MySQL-yhteysasetukset ---
conn = mysql.connector.connect(
    host="localhost",
    user="sahkonseuraaja",
    password="Kekkonen11!",
    database="energy_db"
)
cursor = conn.cursor()

# --- Luodaan taulu jos ei ole olemassa ---
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

# --- Hae data API:sta ---
r = requests.get(URL)
r.raise_for_status()
data = r.json()

prices = data["prices"]          # lista objekteja

# --- Selvitetään mikä jakso sisältää nykyhetken ---

now_utc = datetime.now(timezone.utc)

current = None
for p in prices:
    start_utc = datetime.fromisoformat(p["startDate"].replace("Z", "+00:00"))
    end_utc   = datetime.fromisoformat(p["endDate"].replace("Z", "+00:00"))

    if start_utc <= now_utc < end_utc:
        current = (p, start_utc, end_utc)
        break

# Jos ei löytynyt mitään (ei pitäisi yleensä käydä), käytetään viimeistä
if current is None:
    latest = prices[-1]
    start_utc = datetime.fromisoformat(latest["startDate"].replace("Z", "+00:00"))
    end_utc   = datetime.fromisoformat(latest["endDate"].replace("Z", "+00:00"))
    current = (latest, start_utc, end_utc)

p, start_utc, end_utc = current

# Muunnetaan ajat Suomen ajaksi ennen talletusta (näkyvät tietokannassa oikein)
start_time = start_utc.astimezone(ZoneInfo("Europe/Helsinki"))
end_time   = end_utc.astimezone(ZoneInfo("Europe/Helsinki"))

cents_kwh = float(p["price"])
#eur_mwh = cents_kwh * 10.0

print(
    "DEBUG: chosen period:",
    p,
    "start_local =", start_time,
    "end_local =", end_time,
)

# --- Tarkistetaan onko tämä jakso jo kannassa ---
cursor.execute(
    "SELECT COUNT(*) FROM sahkonhinta WHERE start_time = %s AND end_time = %s",
    (start_time, end_time),
)
exists = cursor.fetchone()[0] > 0

if not exists:
    cursor.execute(
        """
        INSERT INTO sahkonhinta
        (hinta_eur_mwh, hinta_sentit_kwh, start_time, end_time)
        VALUES (%s, %s, %s, %s)
        """,
        (eur_mwh, cents_kwh, start_time, end_time),
    )
    conn.commit()
    print("Tallennettu 1 uusi hinta.")
else:
    print("Uusin jakso on jo tietokannassa, ei lisätty uutta riviä.")

cursor.close()
conn.close()
