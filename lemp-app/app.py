from flask import Flask
import mysql.connector

app = Flask(__name__)

@app.route('/')
def home():
# Connect to MySQL
	conn = mysql.connector.connect(
	host="localhost",
	user="exampleuser",
	password="nuutti14",
	database="exampledb"
)
	cursor = conn.cursor()
	cursor.execute("SELECT 'Hello From MySQL!'")
	result = cursor.fetchone()
	# Clean up
	cursor.close()
	conn.close()
	return f"<h1>LEMP flask</h1><p>SQL Server Time: {reuslt[0]}"

if __name__=='__main__':
	app.run(host='0.0.0.0', port=5000)
