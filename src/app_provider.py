from flask import Flask
import logging
from logging.handlers import TimedRotatingFileHandler
import os.path

app = Flask(__name__)
app.config.from_object("config")
app.config.from_envvar("TCSTATS_SETTINGS", silent=True)
app.secret_key = app.config["SECRET_KEY"]

log_fhandler = TimedRotatingFileHandler(os.path.join(app.config["LOG_DIR"],
    "app"), backupCount=app.config["LOG_BACKUPS"], when="midnight",
    interval=1, utc=True)
log_fmt = logging.Formatter(app.config["LOG_FORMAT"])
app.logger.addHandler(log_fhandler)
app.logger.setLevel(logging.DEBUG if app.config["DEBUG"] else logging.INFO)
log_fhandler.setFormatter(log_fmt)
log_fhandler.setLevel(logging.DEBUG if app.config["DEBUG"] else logging.INFO)
