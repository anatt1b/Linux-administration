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


@st.cache_data
def load_data():
    """Lataa viimeisimmät sähkön spot-hinnat MySQL:stä."""
    conn = mysql.connector.connect(
        host="localhost",
        user="sahkonseuraaja",
        password="Kekkonen11!",
        database="energy_db"
    )

    query = """
        SELECT hinta_eur_mwh,
               hinta_sentit_kwh,
               start_time,
               end_time
        FROM sahkonhinta
        ORDER BY start_time DESC
        LIMIT 200;
    """

    df = pd.read_sql(query, conn)
    conn.close()

    df = df.sort_values("start_time")
    return df


def main():
    st.title("⚡ Sähkön Spot-hinta – Pörssisähkö (Nord Pool / API)")
    st.caption("Data päivittyy 15 min välein cronin avulla.")
    st_autorefresh(interval=5000, key="clock-refresh")
    now = datetime.now(ZoneInfo("Europe/Helsinki"))
    st.info(f"Suomen aika: {now:%Y-%m-%d %H:%M:%S}")


    df = load_data()

    # Viimeisin hinta
    latest = df.iloc[-1]
    current_price = float(latest["hinta_sentit_kwh"])

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
        unsafe_allow_html=True
    )

    # Aikasarja
    st.subheader("📉 Sähkön hinta")
    st.line_chart(df.set_index("start_time")["hinta_sentit_kwh"])

    # Taulukko
    st.subheader("📄 Raakadatat (uusin ensin)")
    st.dataframe(df.iloc[::-1])


if __name__ == "__main__":
    main()
