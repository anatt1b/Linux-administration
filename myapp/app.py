import streamlit as st

st.set_page_config(
    page_title="Data-analyysit",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Data-analyysit")
st.write(
    "Tämä sovellus näyttää Oulun säähavainnot ja sähkön spot-hinnat. "
    "Valitse sivu vasemmasta sivupalkista, tai käytä alla olevia pikalinkkejä."
)

st.subheader("Pikalinkit")

# Sivujen polut suhteessa app.py:hen
st.page_link("pages/weather.py", label="🌦️ Oulun säädata", icon="🌦️")
st.page_link("pages/1_sahkohinta.py", label="⚡ Sähkön spot-hinta", icon="⚡")
