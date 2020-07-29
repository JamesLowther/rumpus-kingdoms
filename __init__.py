from flask import Flask, render_template
import sqlite3, os

app = Flask(__name__)

DB_PATH = os.path.dirname(os.path.abspath(__file__)) + '/bot/database.db'

db_con = sqlite3.connect(DB_PATH, check_same_thread=False)
db_con.row_factory = sqlite3.Row
db_cur = db_con.cursor()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/rules.html')
def rules():
    return render_template("rules.html")

"""
@app.route('/score.html')
def score():

    db_cur.execute("SELECT u.username, k.k_name, CASE WHEN s.total_pop is NULL THEN 0 ELSE s.total_pop END as total_pop FROM Users u, Kingdoms k LEFT JOIN (SELECT v.kid, SUM(v.population) as total_pop FROM Villages v GROUP BY v.kid) s ON k.kid=s.kid WHERE u.uid=k.uid ORDER BY total_pop DESC;")
    results = db_cur.fetchall()

    kingdoms = []

    if results:
        i = 1
        for kingdom in results:
            kingdoms.append({"index": "{:02d}".format(i), "username": kingdom['username'], "kingdom": kingdom['k_name'], "population":kingdom['total_pop']})
            i += 1

    return render_template("score.html", leaderboard=kingdoms)
"""

@app.route('/score.html')
def score():
    return render_template("panic.html")