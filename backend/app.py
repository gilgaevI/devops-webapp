from flask import Flask
import psycopg2
import os
app = Flask(__name__)
@app.route('/')
def home():
    return "Devops Webapp is running"
@app.route('/health')
def health():
    return "OK"
@app.route('/db')
def database():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database="postgres"
        )
        conn.close()
        return "Postgresql is OK"
    except Exception as e:
        return "Postgres connection is failed"

app.run(host="0.0.0.0", port=5000)
