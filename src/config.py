# TCStats Flask configuration file
DEBUG = True
LOG_DIR = "/var/log/tcstats"
LOG_BACKUPS = 365
LOG_FORMAT = \
    "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d :: %(message)s"
SQL_DB = "tc_data.db"
FETCH_RETRIES = 5
FETCH_TIMEOUT = 60 # seconds
FETCH_CHUNK_SIZE = 1024 # bytes
FETCH_SLEEP = 1 # seconds
STATS_URL = "http://community.topcoder.com/tc?module=BasicData"
ROUND_LIST_URL = STATS_URL + "&c=dd_round_list"
ROUND_LIST_FILE = "/tmp/round_list.xml"
ROUND_TABLE = "rounds"
CODER_LIST_URL = STATS_URL + "&c=dd_coder_list"
CODER_LIST_FILE = "/tmp/coder_list.xml"
CODER_TABLE = "coders"
RESULTS_URL = STATS_URL + "&c=dd_round_results&rd=%s"
RESULTS_FILE = "/tmp/round_results_%s.xml"
RESULTS_TABLE = "results"
