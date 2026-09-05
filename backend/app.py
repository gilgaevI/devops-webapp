import os
import logging
import psycopg2
from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="postgres"
    )


def create_table():
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS servers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                status VARCHAR(20),
                cpu INTEGER,
                ram INTEGER
            )
        """)

        conn.commit()

        logger.info("Table 'servers' initialized successfully.")

    except Exception as e:
        logger.error(f"Failed to create table: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/")
def home():
    return "Devops Webapp is running"


@app.route("/health")
def health():
    return "OK", 200


@app.route("/db")
def database():
    conn = None

    try:
        conn = get_db_connection()

        return "Postgresql is OK", 200

    except Exception as e:
        logger.error(f"PostgreSQL connection failed: {e}")
        return "Postgres connection failed", 500

    finally:
        if conn:
            conn.close()


@app.route("/servers", methods=["GET"])
def get_servers():
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM servers;")
        servers = cursor.fetchall()

        result = []

        for server in servers:
            result.append({
                "id": server[0],
                "name": server[1],
                "status": server[2],
                "cpu": server[3],
                "ram": server[4]
            })

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Failed to get servers: {e}")
        return jsonify({
            "error": "Database error"
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


@app.route("/servers/<int:server_id>", methods=["GET"])
def get_server(server_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, name, status, cpu, ram
            FROM servers
            WHERE id = %s;
            """,
            (server_id,)
        )

        server = cursor.fetchone()

        if not server:
            return jsonify({
                "error": "Server not found"
            }), 404

        result = {
            "id": server[0],
            "name": server[1],
            "status": server[2],
            "cpu": server[3],
            "ram": server[4]
        }

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Failed to get server {server_id}: {e}")

        return jsonify({
            "error": "Database error"
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


@app.route("/servers", methods=["POST"])
def create_server():
    conn = None
    cursor = None

    try:
        data = request.json

        if not data:
            return jsonify({
                "error": "JSON body is required"
            }), 400

        required_fields = ["name", "status", "cpu", "ram"]

        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Missing field: {field}"
                }), 400

        if not isinstance(data["cpu"], int):
            return jsonify({
                "error": "CPU must be an integer"
            }), 400

        if not isinstance(data["ram"], int):
            return jsonify({
                "error": "RAM must be an integer"
            }), 400

        if not 0 <= data["cpu"] <= 100:
            return jsonify({
                "error": "CPU must be between 0 and 100"
            }), 400

        if data["ram"] <= 0:
            return jsonify({
                "error": "RAM must be greater than 0"
            }), 400

        if data["status"] not in ["up", "down"]:
            return jsonify({
                "error": "Status must be up or down"
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO servers (name, status, cpu, ram)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
            """,
            (
                data["name"],
                data["status"],
                data["cpu"],
                data["ram"]
            )
        )

        server_id = cursor.fetchone()[0]

        conn.commit()

        return jsonify({
            "id": server_id,
            "message": "Server created"
        }), 201

    except Exception as e:
        logger.error(f"Failed to create server: {e}")

        if conn:
            conn.rollback()

        return jsonify({
            "error": "Database error"
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


@app.route("/servers/<int:server_id>", methods=["PUT"])
def update_server(server_id):
    conn = None
    cursor = None

    try:
        data = request.json

        if not data:
            return jsonify({
                "error": "JSON body is required"
            }), 400

        allowed_fields = ["name", "status", "cpu", "ram"]

        for field in data:
            if field not in allowed_fields:
                return jsonify({
                    "error": f"Field '{field}' is not allowed"
                }), 400

        if "cpu" in data:
            if not isinstance(data["cpu"], int):
                return jsonify({
                    "error": "CPU must be an integer"
                }), 400

            if not 0 <= data["cpu"] <= 100:
                return jsonify({
                    "error": "CPU must be between 0 and 100"
                }), 400

        if "ram" in data:
            if not isinstance(data["ram"], int):
                return jsonify({
                    "error": "RAM must be an integer"
                }), 400

            if data["ram"] <= 0:
                return jsonify({
                    "error": "RAM must be greater than 0"
                }), 400

        if "status" in data:
            if data["status"] not in ["up", "down"]:
                return jsonify({
                    "error": "Status must be up or down"
                }), 400

        fields_to_update = []
        values = []

        for field in allowed_fields:
            if field in data:
                fields_to_update.append(f"{field} = %s")
                values.append(data[field])

        if not fields_to_update:
            return jsonify({
                "error": "No fields to update"
            }), 400

        values.append(server_id)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM servers WHERE id = %s;",
            (server_id,)
        )

        server = cursor.fetchone()

        if not server:
            return jsonify({
                "error": "Server not found"
            }), 404

        cursor.execute(
            f"""
            UPDATE servers
            SET {", ".join(fields_to_update)}
            WHERE id = %s;
            """,
            values
        )

        conn.commit()

        return jsonify({
            "message": "Server updated"
        }), 200

    except Exception as e:
        logger.error(f"Failed to update server {server_id}: {e}")

        if conn:
            conn.rollback()

        return jsonify({
            "error": "Database error"
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


@app.route("/servers/<int:server_id>", methods=["DELETE"])
def delete_server(server_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM servers WHERE id = %s;",
            (server_id,)
        )

        server = cursor.fetchone()

        if not server:
            return jsonify({
                "error": "Server not found"
            }), 404

        cursor.execute(
            """
            DELETE FROM servers
            WHERE id = %s;
            """,
            (server_id,)
        )

        conn.commit()

        return jsonify({
            "message": "Server deleted"
        }), 200

    except Exception as e:
        logger.error(f"Failed to delete server {server_id}: {e}")

        if conn:
            conn.rollback()

        return jsonify({
            "error": "Database error"
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


if __name__ == "__main__":
    create_table()
    app.run(host="0.0.0.0", port=5000)
