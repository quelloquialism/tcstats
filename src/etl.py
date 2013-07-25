from tcstats import app
config = app.config

import logging
from logging.handlers import TimedRotatingFileHandler
import sqlite3
import time
import urllib
import xml.etree.cElementTree as ET

# Program execution flow:
#  1a) fetch_round_list(): download the round_list xml, call load
#  1b) load_round_list(): load round_list into db
#  2a) fetch_round_results(): download all round_results xmls, call load
#  2b) load_round_results(): load round_reounds into db

# TODO who does log dir creation? also make sure permissions allow this
log_fhandler = TimedRotatingFileHandler(config["LOG_DIR"] + "/etl", \
    backupCount=config["LOG_BACKUPS"], when="midnight", interval=1, utc=True)
log_fmt = logging.Formatter(config["LOG_FORMAT"])
log = logging.getLogger("etl")
log.addHandler(log_fhandler)
log.setLevel(logging.DEBUG if config["DEBUG"] else logging.INFO)
log_fhandler.setFormatter(log_fmt)
log_fhandler.setLevel(logging.DEBUG if config["DEBUG"] else logging.INFO)

def keys_table(head, table_name):
  keys = [r[0] for r in head]
  table = "CREATE TABLE IF NOT EXISTS " + table_name + " (" + \
      ",".join([" ".join(field) for field in head]) + ")"
  return keys, table

round_list_keys, round_list_table = keys_table(
    config["ROUND_LIST_HEAD"], "rounds")
round_results_keys, round_results_table = keys_table(
    config["ROUND_RESULTS_HEAD"], "results_%s")
coder_list_keys, coder_list_table = keys_table(
    config["CODER_LIST_HEAD"], "coders")
coder_rounds_keys, coder_rounds_table = keys_table(
    config["CODER_ROUNDS_HEAD"], "coder_rounds")

conn = sqlite3.connect(config["SQL_DB"])
cursor = conn.cursor()

def read_row(row):
  row_data = {}
  for child in row:
    row_data[child.tag] = child.text
  return row_data

def fetch_feeds(to_fetch):
  fetched = []
  for (url, filename) in to_fetch:
    time.sleep(1) # throttle fetches to prevent flooding TC server
    log.info("Fetching %s to local file %s" % (url, filename))
    fetched.append(filename)
    try:
      # TODO this is very slow on connection failure, is there a way to 
      #   config a timeout?
      (_, headers) = urllib.urlretrieve(url, filename)
    except IOError, e: # TODO is IOError the only one urllib throws?
      log.error("Caught error while fetching %s: %s" % (url, e))
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
    log.info("Loading %s into db" % filename)
    data = []
    try:
      feed_et = ET.parse(filename)
      feed_root = feed_et.getroot()
      for row in feed_root:
        data.append(read_row(row))
    except: # TODO what kind of errors can this throw? IO? Parse?
      log.error("Failed to parse %s" % filename)
    for i in xrange(len(data)):
      keys = sorted(data[i].keys())
      if keys == expected_keys:
        data[i] = [data[i][x] for x in keys]
      else:
        log.error("%s row %s does not match expected schema, skipping" % \
            (filename, i))
    cursor.executemany(sql, data)
  conn.commit()

def load_round_list():
  log.info("Creating round list table 'rounds'")
  cursor.execute(round_list_table)
  field_ct = len(config["ROUND_LIST_HEAD"])
  insert_sql = "REPLACE INTO rounds VALUES (" + \
      ",".join("?" * field_ct) + ")"
  load_files([(config["ROUND_LIST_FILE"], insert_sql)], round_list_keys)
  log.info("Finished loading round list")

def load_coder_list():
  log.info("Creating coder list table 'coders'")
  cursor.execute(coder_list_table)
  field_ct = len(config["CODER_LIST_HEAD"])
  insert_sql = "REPLACE INTO coders VALUES (" + \
      ",".join("?" * field_ct) + ")"
  load_files([(config["CODER_LIST_FILE"], insert_sql)], coder_list_keys)
  log.info("Finishing loading coder list")

def load_round_results(round_ids):
  for rid in round_ids:
    log.info("Creating round results table 'results_%s'" % rid)
    cursor.execute(round_results_table % rid)
  field_ct = len(config["ROUND_RESULTS_HEAD"])
  insert_sql = "REPLACE INTO results_%s VALUES (" + \
      ",".join("?" * field_ct) + ")"
  load_files([(config["ROUND_RESULTS_FILE"] % rid, \
      insert_sql % rid) for rid in round_ids], round_results_keys)
  log.info("Finished loading %s round results" % len(round_ids))
  update_coder_rounds_mapping(round_ids)

def update_coder_rounds_mapping(round_ids):
  log.info("Creating coder-rounds mapping table 'coder_rounds'")
  cursor.execute(coder_rounds_table)
  log.info("Writing mappings for %s rounds" % len(round_ids))
  for rid in round_ids:
    get_cids = "SELECT coder_id FROM results_%s" % rid
    insert_sql = "REPLACE INTO coder_rounds VALUES (?, ?)"
    commands = []
    for row in cursor.execute(get_cids):
      commands.append((row[0], rid))
    cursor.executemany(insert_sql, commands)
  log.info("Mappings complete")

def full_run():
  fetch_round_list()
  fetch_coder_list()
  round_ids = [row[0] for row in cursor.execute("SELECT round_id FROM rounds")]
  fetch_round_results(round_ids)
