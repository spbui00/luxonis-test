from flask import Flask, render_template
import psycopg2
import os

app = Flask(__name__)

@app.route('/')
def home():
    hostname='db'
    username='postgres'
    password=os.getenv('POSTGRES_PASSWORD')
    database='sreality'

    conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
    cur = conn.cursor()

    cur.execute("SELECT * FROM ads")
    ads = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('index.html', ads=ads)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)