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
STATS_URL = "http://community.topcoder.com/tc?module=BasicData"
ROUND_LIST_URL = STATS_URL + "&c=dd_round_list"
ROUND_LIST_FILE = "/tmp/round_list.xml"
CODER_LIST_URL = STATS_URL + "&c=dd_coder_list"
CODER_LIST_FILE = "/tmp/coder_list.xml"
ROUND_RESULTS_URL = STATS_URL + "&c=dd_round_results&rd=%s"
ROUND_RESULTS_FILE = "/tmp/round_results_%s.xml"

ROUND_LIST_HEAD = sorted([
  ("round_id", "integer", "primary key"),
  ("full_name", "text"),
  ("short_name", "text"),
  ("round_type_desc", "text"),
  ("date", "text")
])

CODER_LIST_HEAD = sorted([
  ("coder_id", "integer", "primary key"),
  ("handle", "text"),
  ("country_name", "text"),
  ("alg_rating", "integer"),
  ("alg_vol", "integer"),
  ("alg_num_ratings", "integer"),
  ("des_rating", "integer"),
  ("des_vol", "integer"),
  ("des_num_ratings", "integer"),
  ("dev_rating", "integer"),
  ("dev_vol", "integer"),
  ("dev_num_ratings", "integer"),
  ("mar_rating", "integer"),
  ("mar_vol", "integer"),
  ("mar_num_ratings", "integer"),
  ("school", "text")
])

ROUND_RESULTS_HEAD = sorted([
  ("round_id", "integer"),
  ("room_id", "integer"),
  ("room_name", "text"),
  ("coder_id", "integer"),
  ("handle", "text"),
  ("paid", "text"),
  ("old_rating", "integer"),
  ("new_rating", "integer"),
  ("new_vol", "integer"),
  ("num_ratings", "integer"),
  ("room_placed", "integer"),
  ("division_placed", "integer"),
  ("advanced", "text"),
  ("challenge_points", "real"),
  ("system_test_points", "real"),
  ("defense_points", "real"),
  ("submission_points", "real"),
  ("final_points", "real"),
  ("division", "integer"),
  ("problems_presented", "integer"),
  ("problems_submitted", "integer"),
  ("problems_correct", "integer"),
  ("problems_failed_by_system_test", "integer"),
  ("problems_failed_by_challenge", "integer"),
  ("problems_opened", "integer"),
  ("problems_left_open", "integer"),
  ("challenge_attempts_made", "integer"),
  ("challenges_made_successful", "integer"),
  ("challenges_made_failed", "integer"),
  ("challenge_attempts_received", "integer"),
  ("challenges_received_successful", "integer"),
  ("challenges_received_failed", "integer"),
  ("rated_flag", "integer"),
  ("level_one_problem_id", "integer"),
  ("level_one_submission_points", "real"),
  ("level_one_final_points", "real", "default 0"),
  ("level_one_status", "text"),
  ("level_one_time_elapsed", "integer"),
  ("level_one_placed", "integer"),
  ("level_one_language", "text"),
  ("level_two_problem_id", "integer"),
  ("level_two_submission_points", "real"),
  ("level_two_final_points", "real", "default 0"),
  ("level_two_status", "text"),
  ("level_two_time_elapsed", "integer"),
  ("level_two_placed", "integer"),
  ("level_two_language", "text"),
  ("level_three_problem_id", "integer"),
  ("level_three_submission_points", "real"),
  ("level_three_final_points", "real", "default 0"),
  ("level_three_status", "text"),
  ("level_three_time_elapsed", "integer"),
  ("level_three_placed", "integer"),
  ("level_three_language", "text"),
  ("unique", "(coder_id, round_id)")
])
