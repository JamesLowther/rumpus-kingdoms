from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

db_con = sqlite3.connect("../src/database.db", check_same_thread=False)
db_con.row_factory = sqlite3.Row
db_cur = db_con.cursor()

@app.route('/')
def index():

    db_cur.execute("SELECT k.uid, k.k_name, CASE WHEN s.total_pop is NULL THEN 0 ELSE s.total_pop END as total_pop FROM Kingdoms k LEFT JOIN (SELECT v.kid, SUM(v.population) as total_pop FROM Villages v GROUP BY v.kid) s ON k.kid=s.kid ORDER BY total_pop DESC LIMIT 10;")
    results = db_cur.fetchall()

    kingdoms = []

    if results:
        i = 1
        for kingdom in results:
            username = "todo"
            kingdoms.append({"index": "{:02d}".format(i), "username": username, "kingdom": kingdom['k_name'], "population":kingdom['total_pop']})
            i += 1

    return render_template("index.html", leaderboard=kingdoms)