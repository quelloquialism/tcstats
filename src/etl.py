from tcstats import app
config = app.config

import logging
from logging.handlers import TimedRotatingFileHandler
import sqlite3
import time
import urllib
from xml.dom.minidom import parse

# Program execution flow:
#  1a) fetch_round_list(): download the round_list xml, call load
#  1b) load_round_list(): load round_list into db
#  2a) fetch_round_results(): download all round_results xmls, call load
#  2b) load_round_results(): load round_reounds into db

# TODO who does log dir creation? also make sure permissions allow this
log_fhandler = TimedRotatingFileHandler(config["LOG_DIR"] + "/etl", \
    backupCount=config["LOG_BACKUPS"], when="midnight", interval=1, utc=True)
log_fhandler.setLevel(logging.DEBUG if config["DEBUG"] else logging.INFO)
log = logging.getLogger("etl")
log.addHandler(log_fhandler)
log.setLevel(logging.DEBUG if config["DEBUG"] else logging.INFO)

round_list_keys = [r[0] for r in config["ROUND_LIST_HEAD"]]
round_list_table = "CREATE TABLE IF NOT EXISTS rounds (" + \
    ",".join([" ".join(field) for field in config["ROUND_LIST_HEAD"]]) + ")"

round_results_keys = [r[0] for r in config["ROUND_RESULTS_HEAD"]]
round_results_table = "CREATE TABLE IF NOT EXISTS results_%s (" + \
    ",".join([" ".join(field) for field in config["ROUND_RESULTS_HEAD"]]) + ")"

coder_list_keys = [r[0] for r in config["CODER_LIST_HEAD"]]
coder_list_table = "CREATE TABLE IF NOT EXISTS coders (" + \
    ",".join([" ".join(field) for field in config["CODER_LIST_HEAD"]]) + ")"

conn = sqlite3.connect(config["SQL_DB"])
cursor = conn.cursor()

def read_row(row):
  row_data = {}
  child = row.firstChild
  while child is not None:
    if child.firstChild is not None:
      row_data[child.nodeName] = child.firstChild.nodeValue
    else:
      row_data[child.nodeName] = None
    child = child.nextSibling
  return row_data

def fetch_feeds(to_fetch):
  fetched = []
  for (url, filename) in to_fetch:
    time.sleep(1) # throttle fetches to prevent flooding TC server
    log.debug("Fetching %s to local file %s" % (url, filename))
    fetched.append(filename)
    try:
      # TODO this is very slow on connection failure, is there a way to 
      #   config a timeout?
      (_, headers) = urllib.urlretrieve(url, filename)
    except:
      log.error("Caught error while fetching %s" % url)
  return fetched

def fetch_round_list():
  fetched = fetch_feeds([(config["ROUND_LIST_URL"], config["ROUND_LIST_FILE"])])
  if len(fetched) > 0:
    load_round_list()

def fetch_coder_list():
  fetched = fetch_feeds([(config["CODER_LIST_URL"], config["CODER_LIST_FILE"])])
  if len(fetched) > 0:
    load_coder_list()

def fetch_round_results(round_ids):
  fetched = fetch_feeds([(config["ROUND_RESULTS_URL"] % rid, \
      config["ROUND_RESULTS_FILE"] % rid) for rid in round_ids])
  load_round_results(fetched)

def load_files(to_load, expected_keys):
  for (filename, sql) in to_load:
    log.debug("Loading %s into db" % filename)
    # TODO parse is slower than shit
    # (maybe try lxml when i get a chance to download it?)
    feed_dom = parse(filename)
    data = []
    for row in feed_dom.getElementsByTagName("row"):
      data.append(read_row(row))
    for i in xrange(len(data)):
      keys = sorted(data[i].keys())
      if keys == expected_keys:
        data[i] = [data[i][x] for x in keys]
      else:
        log.error("%s does not match expected schema, skipping" % filename)
    cursor.executemany(sql, data)
  conn.commit()

def load_round_list():
  log.info("Creating round list table 'rounds'")
  cursor.execute(round_list_table)
  field_ct = len(config["ROUND_LIST_HEAD"])
  insert_sql = "REPLACE INTO rounds VALUES (" + \
      ",".join("?" * field_ct) + ")"
  load_files([(config["ROUND_LIST_FILE"], insert_sql)], round_list_keys)

def load_coder_list():
  log.info("Creating round list table 'coders'")
  cursor.execute(coder_list_table)
  field_ct = len(config["CODER_LIST_HEAD"])
  insert_sql = "REPLACE INTO coders VALUES (" + \
      ",".join("?" * field_ct) + ")"
  load_files([(config["CODER_LIST_FILE"], insert_sql)], coder_list_keys)

def load_round_results(round_ids):
  for rid in round_ids:
    log.info("Creating round results table 'results_%s'" % rid)
    cursor.execute(round_results_table % rid)
  field_ct = len(config["ROUND_RESULTS_HEAD"])
  insert_sql = "REPLACE INTO results_%s VALUES (" + \
      ",".join("?" * field_ct) + ")"
  load_files([(config["ROUND_RESULTS_FILE"] % rid, \
      insert_sql % rid) for rid in round_ids], round_results_keys)

def full_run():
  fetch_round_list()
  fetch_coder_list()
  round_ids = [row[0] for row in cursor.execute("SELECT round_id FROM rounds")]
  fetch_round_results(round_ids)
