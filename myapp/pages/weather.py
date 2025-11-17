import streamlit as st
import pandas as pd
import sqlalchemy as sa
import plotly.express as px

st.set_page_config(page_title="Oulun säädata", layout="wide")

# MySQL yhteysasetukset
DB = "weather"
USER = "streamlit_user"
PASSWORD = "streamlit"
HOST = "localhost"
TABLE = "oulu_weather"

@st.cache_data(ttl=600)
def load_data():
    engine = sa.create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DB}")
    query = f"SELECT * FROM {TABLE} ORDER BY DateTime"
    return pd.read_sql(query, engine)

def main():
    st.title("Oulun säädata")

    df = load_data()

    st.subheader("Tarkastelu: raakadata")
    st.dataframe(df)

    st.subheader("Lämpötilat")
    fig_temp = px.line(
        df, x="DateTime", y=["MinTemp", "MaxTemp"],
        labels={"value": "Lämpötila (°C)", "DateTime": "Päivämäärä"},
        title="Päivittäiset minimi- ja maksimi lämpötilat"
    )
    st.plotly_chart(fig_temp, use_container_width=True)

    st.subheader("Sademäärä")
    fig_rain = px.bar(
        df, x="DateTime", y="Precipitation",
        labels={"Precipitation": "Sademäärä (mm)", "DateTime": "Päivämäärä"},
        title="Päivittäinen sademäärä"
    )
    st.plotly_chart(fig_rain, use_container_width=True)

if __name__ == "__main__":
    main()
