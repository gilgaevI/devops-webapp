import os
import psycopg2
from flask import Flask, jsonify
app = Flask(__name__)
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="postgres"
    )
def create_table():
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS servers (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        status VARCHAR(20),
                        cpu INTEGER,
                        ram INTEGER
                    )
                """)
        conn.close()
        print("Table 'servers' initialized successfully.")
    except Exception as e:
        print(f"Failed to create table: {e}")
@app.route('/')
def home():
    return "Devops Webapp is running"
@app.route('/health')
def health():
    return "OK", 200
@app.route('/db')
def database():
    try:
        conn = get_db_connection()
        conn.close()
        return "Postgresql is OK", 200
    except Exception as e:
        return "Postgres connection failed", 500
@app.route("/servers")
def get_servers():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="postgres"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM servers;")
    servers = cursor.fetchall()
    cursor.close()
    conn.close()
    result = []
    for server in servers:
        result.append({
            "id": server[0],
            "name": server[1],
            "status": server[2],
            "cpu": server[3],
            "ram": server[4]
        })
    return jsonify(result)
if __name__ == '__main__':
    create_table()
    app.run(host="0.0.0.0", port=5000)
