import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# Sivun asetukset
# -----------------------------
st.set_page_config(
    page_title="Sähkön Spot-hinta",
    page_icon="⚡",
    layout="wide",
)

# -----------------------------
# MySQL -> DataFrame
# -----------------------------
@st.cache_data(ttl=300)
def load_data():
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

    df["start_time"] = pd.to_datetime(df["start_time"])
    df["end_time"] = pd.to_datetime(df["end_time"])

    return df.sort_values("start_time")

# -----------------------------
# Sovellus
# -----------------------------
def main():

    st.title("⚡ Sähkön Spot-hinta 📈 Pörssisähkö (Nord Pool / API)")
    st.caption("Data päivittyy 15 min välein cronin avulla.")

    # Automaattinen päivitys 1 sek välein
    st_autorefresh(interval=1000, key="clock-refresh")

    # Suomen aika ruudulle
    now_fi = datetime.now(ZoneInfo("Europe/Helsinki"))
    st.info(f"Suomen aika: {now_fi:%Y-%m-%d %H:%M:%S}")

    # Lataa hinnat
    df = load_data()

    # Nykyinen aikaleima (ilman aikavyöhykettä)
    now = now_fi.replace(tzinfo=None)

    # Etsi rivi, jossa nyt on start_time–end_time sisällä
    current_row = df[(df["start_time"] <= now) & (df["end_time"] > now)]

    if not current_row.empty:
        current_price = float(current_row.iloc[0]["hinta_sentit_kwh"])
    else:
        # fallback
        current_price = float(df.iloc[-1]["hinta_sentit_kwh"])

    # Värikoodaus
    if current_price < 8:
        color = "green"
    elif current_price < 15:
        color = "orange"
    else:
        color = "red"

    # Näyttölaatikko
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

    st.subheader("📈 Sähkön hinta")
    st.line_chart(df.set_index("start_time")["hinta_sentit_kwh"])

    st.subheader("🧾 Raakadatat (uusin ensin)")
    st.dataframe(df.iloc[::-1])

if __name__ == "__main__":
    main()
