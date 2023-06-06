import os
import socket
from flask import Flask, jsonify
from ddtrace import tracer
import psycopg2
import requests
from dotenv import load_dotenv

tracer.configure(hostname='127.0.0.1', port=8126)

os.environ["DD_DBM_PROPAGATION_MODE"] = "full"

load_dotenv()

app = Flask(__name__)

# Set up the database connection
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS hosts (id SERIAL PRIMARY KEY, hostname VARCHAR(255), ip_address VARCHAR(255))")
conn.commit()

url = "https://api.nostr.watch/v1/public"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    
    # Insert data into the table
    cur = conn.cursor()
    for host in data:
        host_name = host.replace("wss://", "")
        try:
            ip = socket.gethostbyname(host_name)
        except socket.gaierror as e:
            print(f"Error: {e}. Skipping {host}")
            continue
        cur.execute("INSERT INTO hosts (hostname, ip_address) VALUES (%s, %s)", (host, ip))
        print(f"Added item {host} and {ip} to the database")
    conn.commit()
else:
    print("Error: Unable to fetch data from API")

@app.route('/apm-dbm')
def index():
    # Query the database for all rows in a table
    cur = conn.cursor()
    cur.execute("SELECT * FROM hosts")
    rows = cur.fetchall()
    result = []
    for row in rows:
        result.append({
            'hostname': row[1],
            'ip_address': row[2],
            # Add additional fields as needed
        })
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
