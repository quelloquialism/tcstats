# TCStats Flask configuration file
DEBUG = True
LOG_DIR = "/var/log/tcstats"
LOG_BACKUPS = 365
SQL_DB = "tc_data.db"
STATS_URL = "http://community.topcoder.com/tc?module=BasicData"
ROUND_LIST_URL = STATS_URL + "&c=dd_round_list"
ROUND_LIST_FILE = "/tmp/round_list.xml"
ROUND_RESULTS_URL = STATS_URL + "&c=dd_round_results&rd=%s"
ROUND_RESULTS_FILE = "/tmp/round_results_%s.xml"
