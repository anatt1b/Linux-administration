import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh

# Sivun asetukset
st.set_page_config(
    page_title="Sähkön Spot-hinta",
    page_icon="⚡",
    layout="wide",
)

@st.cache_data(ttl=300)  # cache 5 min
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

    # varmisteaan, että aikakentät ovat datetime-tyyppiä ilman aikavyöhykettä
    df["start_time"] = pd.to_datetime(df["start_time"])
    df["end_time"] = pd.to_datetime(df["end_time"])

    # varmuuden vuoksi järjestys aikajärjestykseen
    df = df.sort_values("start_time")

    return df


def main():
    st.title("⚡ Sähkön Spot-hinta 📈 Pörssisähkö (Nord Pool / API)")
    st.caption("Data päivittyy 15 min välein cronin avulla.")

    # automaattinen sivun päivitys 1 s välein, jotta kello rullaa
    st_autorefresh(interval=1000, key="clock-refresh")

    # Suomen aika näytölle (aikavyöhykkeen kanssa)
    now_fi = datetime.now(ZoneInfo("Europe/Helsinki"))
    st.info(f"Suomen aika: {now_fi:%Y-%m-%d %H:%M:%S}")

    # Ladataan hinnat
    df = load_data()

    # Tehdään "naive"-aika vertailua varten (ilman tz:tä),
    # koska tietokannan DATETIME-kentät ovat myös ilman tz:tä.
    now = now_fi.replace(tzinfo=None)

    # Etsitään se rivi, jonka aikaväli sisältää nykyhetken
    current_row = df[(df["start_time"] <= now) & (df["end_time"] > now)]

    if not current_row.empty:
        current_price = float(current_row.iloc[0]["hinta_sentit_kwh"])
    else:
        # fallback – jos ei löydy (ei pitäisi tapahtua), otetaan uusin rivi
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

    # Aikasarja
    st.subheader("📈 Sähkön hinta")
    st.line_chart(df.set_index("start_time")["hinta_sentit_kwh"])

if __name__ == "__main__":
    main()