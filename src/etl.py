from tcstats import app

import logging
from logging.handlers import TimedRotatingFileHandler
import os.path
import requests
import sqlite3
import time
import urllib
import xml.etree.cElementTree as ET

config = app.config

# Program execution flow:
#  1a) fetch_round_list(): download the round_list xml, call load
#  1b) load_round_list(): load round_list into db
#  2a) fetch_round_results(): download all round_results xmls, call load
#  2b) load_round_results(): load round_reounds into db

# TODO who does log dir creation? also make sure permissions allow this
log_fhandler = TimedRotatingFileHandler(os.path.join(config["LOG_DIR"], "etl"),
    backupCount=config["LOG_BACKUPS"], when="midnight", interval=1, utc=True)
log_fmt = logging.Formatter(config["LOG_FORMAT"])
log = logging.getLogger("etl")
log.addHandler(log_fhandler)
log.setLevel(logging.DEBUG if config["DEBUG"] else logging.INFO)
log_fhandler.setFormatter(log_fmt)
log_fhandler.setLevel(logging.DEBUG if config["DEBUG"] else logging.INFO)

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
    time.sleep(config["FETCH_SLEEP"])
    log.info("Fetching %s to local file %s" % (url, filename))

    success = False
    for i in range(config["FETCH_RETRIES"]):
      try:
        req = requests.get(url, stream=True, timeout=config["FETCH_TIMEOUT"])
        if req.status_code == 200:
          with open(filename, "wb") as feedfile:
            for chunk in req.iter_content(config["FETCH_CHUNK_SIZE"]):
              feedfile.write(chunk)
          success = True
        else:
          log.error("Status code %s while fetching %s, retrying (%d of 5)" % \
              (re.status_code, url, i + 1))
      except: # TODO specific errors?
        log.error("Caught error while fetching %s, retrying (%d of 5)" % \
            (url, i + 1))
      if success:
        break
    if not success:
      log.error("Max retries for %s reached, skipping" % url)
    else:
      log.info("Successfully fetched %s" % url)
      fetched.append(filename)
  return fetched

def load_files(files, table, extra_data=[]):
  sql = "REPLACE INTO " + table + " (%s) VALUES (%s)"
  for f, filename in enumerate(files):
    log.info("Loading %s into db" % filename)
    data = []
    try:
      feed_et = ET.parse(filename)
      feed_root = feed_et.getroot()
      for row in feed_root:
        row_data = read_row(row)
        if len(extra_data) > f:
          row_data.update(extra_data[f])
        data.append(row_data)
    except: # TODO what kind of errors can this throw? IO? Parse?
      log.error("Failed to parse %s" % filename)
    expected_keys = None
    for i in xrange(len(data)):
      keys = sorted(data[i].keys())
      if expected_keys is None:
        expected_keys = keys
      elif keys != expected_keys:
        log.error("%s row %s does not match expected schema, skipping" % \
            (filename, i))
    placeholders = [":" + key for key in expected_keys]
    cursor.executemany(sql % (",".join(expected_keys),
        ",".join(placeholders)), data)
  conn.commit()

def fetch_round_list():
  fetched = fetch_feeds([(config["ROUND_LIST_URL"], config["ROUND_LIST_FILE"])])
  if len(fetched) > 0:
    load_files(fetched, config["ROUND_TABLE"])
    log.info("Finished loading round list")

def fetch_coder_list():
  fetched = fetch_feeds([(config["CODER_LIST_URL"], config["CODER_LIST_FILE"])])
  if len(fetched) > 0:
    load_files(fetched, config["CODER_TABLE"])
    log.info("Finishing loading coder list")

def fetch_round_results(round_ids):
  fetched = fetch_feeds([(config["RESULTS_URL"] % rid, \
      config["RESULTS_FILE"] % rid) for rid in round_ids])
  if len(fetched) > 0:
    load_files([config["RESULTS_FILE"] % rid for rid in round_ids],
        config["RESULTS_TABLE"],
        [{"round_id": rid} for rid in round_ids])
    log.info("Finished loading %s round results" % len(fetched))

def full_run():
  fetch_round_list()
  fetch_coder_list()
  round_ids = [row[0] for row in cursor.execute("SELECT round_id FROM rounds")]
  fetch_round_results(round_ids)
