import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh



# SIVUN ASETUKSET

st.set_page_config(
    page_title="Säädata",
    page_icon="⛅",
    layout="wide",
)



# Tietokannasta lukeminen

@st.cache_data(ttl=300)  # cache 5 min
def load_weather_data():
    """Lataa viimeisimmät säähavainnot MySQL:stä."""
    conn = mysql.connector.connect(
        host="localhost",
        user="saamies",
        password="Säämies123!",
        database="weather_db"
    )

    query = """
        SELECT city,
               temperature,
               description,
               timestamp
        FROM weather_data
        ORDER BY timestamp DESC
        LIMIT 200;
    """

    df = pd.read_sql(query, conn)
    conn.close()

    # varmistetaan, että timestamp on datetime-tyyppiä
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def main():
    # pieni teksti yläreunaan
    st.caption("Data päivittyy 15 min välein cronin avulla.")

    # automaattinen päivitys (esim. 10 sek välein)
    st_autorefresh(interval=10_000, key="weather-refresh")

    # Suomen aika näkyviin
    now_fi = datetime.now(ZoneInfo("Europe/Helsinki"))
    st.info(f"Suomen aika: {now_fi:%Y-%m-%d %H:%M:%S}")

    # Ladataan data
    df = load_weather_data()

    if df.empty:
        st.warning("Tietokannassa ei ole vielä säädataa.")
        return

    
    # Nykyinen säähavainto
   
    latest = df.iloc[0]
    city = latest["city"]
    temp = float(latest["temperature"])
    desc = latest["description"]
    ts = latest["timestamp"]

    # yksinkertainen värikoodaus lämpötilan mukaan
    if temp < 0:
        color = "#0077ff"    # kylmä -> sininen
    elif temp < 15:
        color = "green"      # viileä/mieto
    elif temp < 25:
        color = "orange"     # lämmin
    else:
        color = "red"        # helle

    # iso laatikko nykyiselle säälle
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
            {city}: {temp:.1f}°C — {desc}<br>
            (päivitetty: {ts:%Y-%m-%d %H:%M:%S})
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")  # pieni väli

    
    # Aikasarja (lämpötila vs. aika)
   
    st.subheader("🌡 Lämpötila")

    # piirretään taulukko aikajärjestyksessä vanhin ensin
    df_sorted = df.sort_values("timestamp")
    st.line_chart(df_sorted.set_index("timestamp")["temperature"])

  
    # Raakadatat
    
    st.subheader("📄 Kempele sää")
    st.dataframe(df)


if __name__ == "__main__":
    main()
