#!/usr/bin/python
from flask import Flask, g, render_template, request, url_for
# TODO only import what is used in the end
from flask import session, redirect, abort, flash
import sqlite3

app = Flask(__name__)
app.config.from_object("config")
app.config.from_envvar("TCSTATS_SETTINGS", silent=True)

def get_db_conn():
  return sqlite3.connect(app.config["SQL_DB"])

@app.before_request
def before_request():
  g.conn = get_db_conn()

@app.teardown_request
def teardown_request(exception):
  conn = getattr(g, "conn", None)
  if conn is not None:
    conn.close()

@app.route("/")
def show_selector():
  return render_template("landing.html")

@app.route("/tcstats", methods=["GET"])
def query_handle():
  # TODO why can't i seem to access form data? this line falls thru to except
  try:
    handle = request.form["handle"]
  except:
    handle = "Aleksey"
  cid = g.conn.execute("SELECT coder_id FROM coders WHERE handle = ?", \
      [handle]).fetchone()[0]
  rounds = [row[0] for row in g.conn.execute(
      "SELECT round_id FROM coder_rounds WHERE coder_id = ?", [cid]).fetchall()]
  return render_template("tcstats.html", cid=cid, handle=handle,
      rounds=sorted(rounds), len_rounds=len(rounds))

if __name__ == "__main__":
  app.run()
