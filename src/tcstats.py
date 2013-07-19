#!/usr/bin/python
from flask import Flask, g, render_template, url_for
# TODO only import what is used in the end
from flask import request, session, redirect, abort, flash

app = Flask(__name__)
app.config.from_object("config")
app.config.from_envvar("TCSTATS_SETTINGS", silent=True)

def get_db_conn():
  return None

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

@app.route("/tcstats")
def query_handle():
  return render_template("tcstats.html")

if __name__ == "__main__":
  app.run()
