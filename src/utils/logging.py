import json
import time


def log_error(req):
    with open("errors.log", "a") as f:
        f.write(str(time.time()) + "\n")
        f.write(json.dumps(req) + "\n\n")


def log_general(req):
    with open("general.log", "a") as f:
        f.write(str(time.time()) + "\n")
        f.write(json.dumps(req) + "\n\n")

# ADD CUSTOM FILE LOGGERS HERE
