#!/usr/bin/python

from flask import Flask, flash, g, render_template, request, url_for
# TODO only import what is used in the end
from flask import session, redirect, abort
import logging
from logging.handlers import TimedRotatingFileHandler
import os.path
import sqlite3

import utils

app = Flask(__name__)
app.config.from_object("config")
app.config.from_envvar("TCSTATS_SETTINGS", silent=True)
app.secret_key = "not secret"

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
  handle = None
  try:
    handle = request.args["handle"]
    cid, rating = g.conn.execute("SELECT coder_id, alg_rating FROM coders " + \
        "WHERE handle = ?", [handle]).fetchone()
  except: # TODO what errors?
    flash("Could not find a user with handle '%s'." % handle)
    return render_template("landing.html", asof=rating_functions.as_of(g.conn))

  rounds = []
  pvpetr = ""
  asof = ""
  compliment = ""
  
  try:
    rounds = g.conn.execute(
        "SELECT * FROM coder_rounds WHERE coder_id = ?", [cid]).fetchall()
    round_ids = [row[7] for row in rounds]
    round_names = g.conn.execute(
        "SELECT short_name FROM rounds WHERE round_id IN (" + \
        ", ".join("?" * len(rounds)) + ")", round_ids).fetchall()
    for i in range(len(rounds)):
      rounds[i] = round_names[i] + rounds[i][1:-1]
    rounds = utils.make_table(rounds,
        titles=["Match", "Div", "Rank", "New Rating", "New Volatility",
            "Old Rating", "Room Rank"])
  except: # TODO
    error_msg = "Failed to read round history for %s" % handle
    app.logger.error(error_msg)
    flash(error_msg)

  try:
    pvpetr_data = rating_functions.pvpetr(g.conn, cid)
    pvpetr_summary = "<p>Wins: %d / Losses: %d</p>" % \
        (len(pvpetr_data[0]), len(pvpetr_data[1]))
    for dataset in pvpetr_data:
      for i, row in enumerate(dataset):
        dataset[i] = list(row)
        dataset[i][1] = rating_functions.pname[row[1]]
    pvpetr_wins_table = utils.make_table(pvpetr_data[0],
        titles=["Match", "Problem", "%s Score" % handle, "Petr Score"],
        format=["%s", "%s", "<b>%0.2f</b>", "%0.2f"])
    pvpetr_losses_table = utils.make_table(pvpetr_data[1],
        titles=["Match", "Problem", "%s Score" % handle, "Petr Score"],
        format=["%s", "%s", "%0.2f", "<b>%0.2f</b>"])
    pvpetr = pvpetr_summary + pvpetr_wins_table + pvpetr_losses_table
  except: # TODO
    error_msg = "Failed to read PvPetr for %s" % handle
    app.logger.error(error_msg)
    flash(error_msg)

  try:
    asof = rating_functions.as_of(g.conn)
  except: # TODO
    error_msg = "Failed to read last match time"
    app.logger.error(error_msg)
    flash(error_msg)

  compliment = rating_functions.get_compliment(rating)

  return render_template("tcstats.html", cid=cid, handle=handle, rating=rating,
      rounds=rounds, len_rounds=len(rounds),
      pvpetr=pvpetr, asof=asof,
      compliment=compliment)

if __name__ == "__main__":
  app.run()
