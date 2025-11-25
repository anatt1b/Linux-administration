import streamlit as st
import pandas as pd
import mysql.connector
import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh


# -------------------------------
# Sivun asetukset
# -------------------------------
st.set_page_config(
    page_title="Sähkön Spot-hinta",
    page_icon="⚡",
    layout="wide",
)

# -------------------------------
# MySQL -> DataFrame
# -------------------------------

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

    # Varmistetaan että ajat ovat datetime-tyyppiä
    df["start_time"] = pd.to_datetime(df["start_time"])
    df["end_time"] = pd.to_datetime(df["end_time"])

    # Järjestys aikajärjestykseen (vanhin ensin)
    df = df.sort_values("start_time")

    return df


# -------------------------------
# API: nykyhetken hinta
# -------------------------------
@st.cache_data(ttl=60)  # haetaan API:sta korkeintaan 1/min
def fetch_current_price_api():
    """
    Hakee nykyhetken spot-hinnan Pörssisähkö API:sta.
    Palauttaa hinnan snt/kWh (float) tai None jos virhe.
    """
    try:
        # Nykyinen UTC-aika ISO-muodossa, Z-loppuinen
        now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        url = "https://api.porssisahko.net/v2/price.json"
        r = requests.get(url, params={"date": now_utc}, timeout=10)
        r.raise_for_status()

        data = r.json()
        # API:n dokumentin mukaan price on snt/kWh (ALV mukana)
        price = float(data["price"])
        return price
    except Exception as e:
        # Virhetilanteessa palautetaan None ja näytetään teksti Streamlitissä
        st.warning(f"Nykyhetken hintaa ei saatu API:sta: {e}")
        return None


# -------------------------------
# Sovellus
# -------------------------------
def main():
    st.title("⚡ Sähkön Spot-hinta 📈 Pörssisähkö (Nord Pool / API)")

    st.caption("Data päivittyy 15 min välein.")

    # Automaattinen uudelleenajo 1 s välein (kello + vihreä laatikko)
    st_autorefresh(interval=1000, key="clock-refresh")

    # Suomen aika ruudulle
    now_fi = datetime.now(ZoneInfo("Europe/Helsinki"))
    st.info(f"Suomen aika: {now_fi:%Y-%m-%d %H:%M:%S}")

    # Ladataan historiadata MySQL:stä
    df = load_data()

    # Hae nykyinen tuntihinta API:sta
    current_price = fetch_current_price_api()

    # Jos API ei jostain syystä toimi, käytetään varasuunnitelmaa:
    if current_price is None and not df.empty:
        # otetaan uusin rivi kannasta
        current_price = float(df.iloc[-1]["hinta_sentit_kwh"])

    # ---------------------------
    # Värikoodaus vihreälle laatikolle
    # ---------------------------
    color = "green"
    if current_price is None:
        color = "gray"
    elif current_price < 8:
        color = "green"
    elif current_price < 15:
        color = "orange"
    else:
        color = "red"

    # ---------------------------
    # Näyttölaatikko: nykyinen tuntihinta
    # ---------------------------
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

    # ---------------------------
    # Aikasarja
    # ---------------------------
    st.subheader("📉 Sähkön hinta")
    if not df.empty:
        st.line_chart(df.set_index("start_time")["hinta_sentit_kwh"])
    else:
        st.write("Ei dataa näytettäväksi (tietokanta tyhjä).")

    # ---------------------------
    # Taulukko (uusin ensin)
    # ---------------------------
    st.subheader("📄 Raakadatat (uusin ensin)")
    if not df.empty:
        st.dataframe(df.iloc[::-1])
    else:
        st.write("Ei dataa taulukossa.")


if __name__ == "__main__":
    main()