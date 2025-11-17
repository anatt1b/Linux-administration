from flask import Flask, render_template
import mysql.connector
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

@app.route("/")
def home():
    conn = mysql.connector.connect(
        host="localhost",
        user="streamlit_user",
        password="streamlit",
        database="weather"
    )
    cur = conn.cursor()
    cur.execute("SELECT NOW();")
    result = cur.fetchone()
    cur.close(); conn.close()

    # MySQL palauttaa UTC:n -> muutetaan Suomen aikaan (EET/UTC+2)
    sql_time_utc = result[0]
    sql_time_fi = sql_time_utc + timedelta(hours=2)

    return render_template("index.html", sql_time=sql_time_fi, year=datetime.now().year)