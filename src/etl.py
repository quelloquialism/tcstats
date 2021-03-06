from collections import defaultdict
import logging
from logging.handlers import TimedRotatingFileHandler
import os.path
import requests
import sqlite3
import time
import urllib
import xml.etree.cElementTree as ET

from app_provider import app

config = app.config

# TODO who does log dir creation? also make sure permissions allow this
log_fhandler = TimedRotatingFileHandler(os.path.join(config["LOG_DIR"], "etl"),
    backupCount=config["LOG_BACKUPS"], when="midnight", interval=1, utc=True)
log_fmt = logging.Formatter(config["LOG_FORMAT"])
log = logging.getLogger("etl")
log.addHandler(log_fhandler)
log.setLevel(logging.DEBUG if config["DEBUG"] else logging.INFO)
log_fhandler.setFormatter(log_fmt)
log_fhandler.setLevel(logging.DEBUG if config["DEBUG"] else logging.INFO)

conn = None
cursor = None

def create_tables():
  try:
    cursor.executescript(open("schema.sql").read())
  except Exception, e:
    log.error("Error executing schema.sql: %s" % e)

# Parse out a single <row> element from TC xml into a dict
def read_row(row):
  row_data = {}
  for child in row:
    row_data[child.tag] = child.text
  return row_data

# Download a list of xml feeds from TC
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
          log.warn("Status code %s while fetching %s, retrying (%d of 5)" % \
              (re.status_code, url, i + 1))
      except Exception, e:
        log.warn("Caught error while fetching %s, retrying (%d of 5): %s" % \
            (url, i + 1, e))
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
    except Exception, e:
      log.error("Failed to parse %s: %s" % (filename, e))
    expected_keys = None
    for i in xrange(len(data)):
      keys = sorted(data[i].keys())
      if expected_keys is None:
        expected_keys = keys
      elif keys != expected_keys:
        log.error("%s row %s does not match expected schema, skipping" % \
            (filename, i))
    if expected_keys is not None:
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

# Populate old_vol for every round and coder
def calculate_old_vol():
  vols = defaultdict(lambda: config["STARTING_VOL"])
  rounds_sql = "SELECT round_id FROM rounds ORDER BY date"
  coders_sql = "SELECT coder_id FROM results WHERE round_id = ? " + \
      "AND rated_flag = 1"
  update_sql = "UPDATE results SET old_vol = ? " + \
      "WHERE coder_id = ? AND round_id = ?"
  new_vol_sql = "SELECT new_vol FROM results " + \
      "WHERE coder_id = ? AND round_id = ?"
  round_ids = [row[0] for row in cursor.execute(rounds_sql)]
  for rid in round_ids:
    coders = [row[0] for row in cursor.execute(coders_sql, [rid])]
    update_args = [(vols[cid], cid, rid) for cid in coders]
    cursor.executemany(update_sql, update_args)
    for cid in coders:
      new_vol = cursor.execute().fetchone()[0]
      vols[cid] = new_vol
  conn.commit()

# Populate participation for every coder
# participation = # of matches played out of the last 30 (configurable)
def calculate_participation(matches):
  participation = defaultdict(lambda: 0)
  rounds_sql = "SELECT round_id FROM rounds WHERE " + \
      "short_name LIKE \"%SRM%\" ORDER BY date DESC LIMIT " + str(matches)
  # TODO should participation care about rated_flag?
  coders_sql = "SELECT coder_id FROM results WHERE round_id = ?"
  update_sql = "UPDATE coders SET participation = ? WHERE coder_id = ?"
  round_ids = [row[0] for row in cursor.execute(rounds_sql)]
  for rid in round_ids:
    coders = [row[0] for row in cursor.execute(coders_sql, [rid])]
    for cid in coders:
      participation[cid] += 1
  cursor.executemany(update_sql,
      [(participation[cid], cid) for cid in participation])
  conn.commit()

# Populate pref_language for every coder
# pref_language = most used language from all time
def calculate_pref_language():
  # TODO should this be most recent N matches instead of all time?
  coders = {}
  # TODO should pref_language care about rated_flag?
  problem_levels = ["one", "two", "three"]
  coders_sql = "SELECT coder_id, level_%s_language FROM results WHERE " + \
      "level_%s_status = 'Passed System Test'"
  update_sql = "UPDATE coders SET pref_language = ? WHERE coder_id = ?"
  for level in problem_levels:
    coder_langs = cursor.execute(coders_sql % (level, level))
    for (cid, lang) in coder_langs:
      if cid not in coders:
        coders[cid] = defaultdict(lambda: 0)
      coders[cid][lang] += 1
  updates = []
  for cid in coders:
    most = 0
    most_lang = ""
    for lang in coders[cid]:
      if coders[cid][lang] > most:
        most = coders[cid][lang]
        most_lang = lang
    updates.append((most_lang, cid))
  # TODO why not record the % usage of each language, rather than just the top?
  cursor.executemany(update_sql, updates)
  conn.commit()

def full_run():
  create_tables()
  fetch_round_list()
  fetch_coder_list()
  # TODO is there a way to fetch only rounds that need to be updated?
  round_ids = [row[0] for row in cursor.execute("SELECT round_id FROM rounds")]
  fetch_round_results(round_ids)
  calculate_old_vol()
  calculate_participation(config["RECENT_MATCHES"])

def controller():
  conn = sqlite3.connect(config["SQL_DB"])
  cursor = conn.cursor()
  while True:
    try:
      full_run()
    except Exception, e:
      error_msg = "ETL failed: %s" % e
      app.logger.error(error_msg)
    time.sleep(config["ETL_SLEEP"])
