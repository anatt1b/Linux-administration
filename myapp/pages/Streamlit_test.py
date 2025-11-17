import streamlit as st
import pandas as pd
import plotly.express as px

def main():
    st.title("Oulun säädata")

    df = pd.read_csv("pages/Oulu.csv", sep=';')

    # Muutetaan sarakkeiden nimet selkeämmiksi
    df = df.rename(columns={
        "DateTime": "Päivä",
        "Precipitation": "Sademäärä (mm)",
        "Minimum temperature": "Min (°C)",
        "Maximum temperature": "Max (°C)",
        "Typical maximum temperature (low)": "Tyyp. max low",
        "Typical maximum temperature (high)": "Tyyp. max high",
        "Typical minimum temperature (low)": "Tyyp. min low",
        "Typical minimum temperature (high)": "Tyyp. min high",
    })

    # Muutetaan päivämäärä oikeaksi datetime-tyypiksi
    df["Päivä"] = pd.to_datetime(df["Päivä"])

    # Näytä siisti taulukko
    st.subheader("Säähavainto taulukko")
    st.dataframe(df[["Päivä", "Sademäärä (mm)", "Min (°C)", "Max (°C)"]])

    # Piirretään kuvaaja
    st.subheader("Päivän ylin lämpötila")
    fig = px.line(df, x="Päivä", y="Max (°C)", markers=True)
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
