import pandas as pd
import sqlalchemy as sa

DATABASE = "weather"
USER = "streamlit_user"
PASSWORD = "streamlit"
HOST = "localhost"
TABLE = "oulu_weather"
CSV_FILE = "/home/ubuntu/myapp/pages/Oulu.csv"

# Lue CSV (puolipiste-erotin)
df = pd.read_csv(CSV_FILE, sep=';')

# Muuta sarakenimet vastaamaan taulua
df.columns = [
    "DateTime",
    "Precipitation",
    "MinTemp",
    "MaxTemp",
    "TypicalMaxTempLow",
    "TypicalMaxTempHigh",
    "TypicalMinTempLow",
    "TypicalMinTempHigh"
]

# Muuta DateTime päivämäärämuotoon
df["DateTime"] = pd.to_datetime(df["DateTime"]).dt.date

# Luo yhteys
engine = sa.create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DATABASE}")

# Vie tauluun (korvaa datan)
df.to_sql(TABLE, con=engine, if_exists="replace", index=False)

print("Data imported successfully!")
