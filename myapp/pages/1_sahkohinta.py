import streamlit as st
import pandas as pd
import mysql.connector
import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh

# ----------------------------------------
# Sivun asetukset
# ----------------------------------------
st.set_page_config(
    page_title="Sähkön Spot-hinta",
    page_icon="⚡",
    layout="wide",
)

# ----------------------------------------
# MySQL -> DataFrame (historiadata käyrää ja taulukkoa varten)
# ----------------------------------------
@st.cache_data(ttl=300)  # välimuisti 5 min
def load_data():
    """Lataa viimeisimmät sähkön spot-hinnat MySQL:stä."""
    conn = mysql.connector.connect(
        host="localhost",
        user="sahkonseuraaja",
        password="Kekkonen11!",
        database="energy_db",
    )

    query = """
        SELECT
            hinta_eur_mwh,
            hinta_sentit_kwh,
            start_time,
            end_time
        FROM sahkonhinta
        ORDER BY start_time ASC
        LIMIT 200;
    """

    df = pd.read_sql(query, conn)
    conn.close()

    # Varmistetaan että aikakentät ovat datetime-tyyppiä
    df["start_time"] = pd.to_datetime(df["start_time"])
    df["end_time"] = pd.to_datetime(df["end_time"])

    return df


# ----------------------------------------
# Nykyisen hinnan haku Pörssisähkö API:sta
# ----------------------------------------
def fetch_current_price_api():
    """
    Hakee tämän hetken hinnan Pörssisähkö API:n price.json -endpointista.
    Palauttaa hinnan snt/kWh (float) tai None jos epäonnistuu.
    """
    try:
        # Nykyhetki UTC-ajassa ISO-8601 muodossa, esim. 2025-11-24T17:20:00Z
        now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        url = "https://api.porssisahko.net/v2/price.json"
        params = {"date": now_utc}

        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()

        # API:n dokumentaation mukaan yksikkö on snt/kWh (sis. alv)
        return float(data["price"])
    except Exception as e:
        st.error(f"Nykyisen hinnan haku epäonnistui: {e}")
        return None


# ----------------------------------------
# Varsinainen sovellus
# ----------------------------------------
def main():
    st.title("⚡ Sähkön Spot-hinta 📈 Pörssisähkö (Nord Pool / API)")
    st.caption("Data päivittyy 15 min välein cronin avulla. Nykyinen hinta haetaan API:sta reaaliaikaisesti.")

    # Automaattinen sivun päivitys 1 s välein
    st_autorefresh(interval=1000, key="clock-refresh")

    # Suomen aika näkyviin
    now_fi = datetime.now(ZoneInfo("Europe/Helsinki"))
    st.info(f"Suomen aika: {now_fi:%Y-%m-%d %H:%M:%S}")

    # Ladataan historiadata MySQL:stä
    df = load_data()

    # Haetaan nykyinen hinta API:sta
    current_price = fetch_current_price_api()

    # Jos API-haku epäonnistui, käytetään varana tietokannan viimeisintä arvoa
    if current_price is None and not df.empty:
        current_price = float(df.iloc[-1]["hinta_sentit_kwh"])

    # ----------------------------------------
    # Näyttölaatikko: nykyinen tuntihinta
    # ----------------------------------------
    if current_price is not None:
        # Värit rajojen mukaan (voit säätää mielesi mukaan)
        if current_price < 8:
            color = "green"
        elif current_price < 15:
            color = "orange"
        else:
            color = "red"

        st.markdown(
            f"""
            <div style="
                background-color:{color};
                padding:20px;
                border-radius:10px;
                color:white;
                text-align:center;
                font-size:28px;
                font-weight:bold;">
                Nykyinen tuntihinta: {current_price:.2f} snt/kWh
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.warning("Nykyistä hintaa ei voitu hakea.")

    st.write("")  # pieni väli

    # ----------------------------------------
    # Aikasarja-käyrä historiadatasta
    # ----------------------------------------
    if not df.empty:
        st.subheader("📉 Sähkön hinta")
        st.line_chart(df.set_index("start_time")["hinta_sentit_kwh"])
    else:
        st.warning("Historiadataa ei löytynyt tietokannasta.")

    # ----------------------------------------
    # Raakadata taulukkona (uusin ensin)
    # ----------------------------------------
    if not df.empty:
        st.subheader("📄 Raakadatadat (uusin ensin)")
        st.dataframe(df.iloc[::-1])
    else:
        st.info("Näytettävää raakadataa ei ole.")


if __name__ == "__main__":
    main()