from flask import Flask, render_template
import mysql.connector
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    conn = mysql.connector.connect(
        host="localhost",
        user="exampleuser",
        password="nuutti14",
        database="exampledb"
    )
    cur = conn.cursor()
    cur.execute("SELECT NOW();")
    result = cur.fetchone()
    cur.close(); conn.close()

    sql_time = result[0]  # MySQL DATETIME
    return render_template("index.html", sql_time=sql_time, year=datetime.now().year)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

