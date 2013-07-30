#!/usr/bin/python

from flask import Flask, g, render_template, request, url_for
# TODO only import what is used in the end
from flask import session, redirect, abort, flash
import logging
from logging.handlers import TimedRotatingFileHandler
import os.path
import sqlite3

app = Flask(__name__)
app.config.from_object("config")
app.config.from_envvar("TCSTATS_SETTINGS", silent=True)

# this import must come after app.config is set up
import rating_functions

log_fhandler = TimedRotatingFileHandler(os.path.join(app.config["LOG_DIR"],
    "app"), backupCount=app.config["LOG_BACKUPS"], when="midnight",
    interval=1, utc=True)
log_fmt = logging.Formatter(app.config["LOG_FORMAT"])
app.logger.addHandler(log_fhandler)
app.logger.setLevel(logging.DEBUG if app.config["DEBUG"] else logging.INFO)
log_fhandler.setFormatter(log_fmt)
log_fhandler.setLevel(logging.DEBUG if app.config["DEBUG"] else logging.INFO)

def get_db_conn():
  conn = getattr(g, "conn", None)
  if conn is None:
    conn = sqlite3.connect(app.config["SQL_DB"])
  return conn

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
  return render_template("landing.html", asof=rating_functions.as_of(g.conn))

@app.route("/tcstats", methods=["GET"])
def query_handle():
  try:
    handle = request.args["handle"]
    cid, rating = g.conn.execute("SELECT coder_id, alg_rating FROM coders " + \
        "WHERE handle = ?", [handle]).fetchone()
  except: # TODO what errors?
    app.logger.error("Caught error on tcstats request")
    return render_template("landing.html", asof=rating_functions.as_of(g.conn))

  rounds = g.conn.execute(
      "SELECT * FROM coder_rounds WHERE coder_id = ?", [cid]).fetchall()
  round_ids = [row[7] for row in rounds]
  round_names = g.conn.execute(
      "SELECT short_name FROM rounds WHERE round_id IN (" + \
      ", ".join("?" * len(rounds)) + ")", round_ids).fetchall()
  for i in range(len(rounds)):
    rounds[i] = round_names[i] + rounds[i][1:]
  pvpetr = rating_functions.pvpetr(g.conn, cid)
  pvpetr = [["%s Level %d: %s to %s" % data for data in winloss] \
      for winloss in pvpetr]
  return render_template("tcstats.html", cid=cid, handle=handle, rating=rating,
      rounds=rounds, len_rounds=len(rounds),
      pvpetr=pvpetr, asof=rating_functions.as_of(g.conn),
      compliment=rating_functions.get_compliment(rating))

if __name__ == "__main__":
  app.run()
