import os
import json
import time
from waitress import serve
from src.app import app
from src.database import Database
from multiprocessing import Process
import subprocess
from queue import Queue
import src.app

###update function - runs query and database update script every n interval
def update(database):
    while True:
        database.query_chain_and_update_database()
        time.sleep(app.config["query_chain_interval"])

###Read configurations from config
with open(os.path.abspath(os.path.join('','config.json'))) as f:
    config = json.load(f)
    app.config.update(config)


###Initialize the database according to the configurations
def main():
    database = Database(app.config["database_path"], app.config["chain_url"] + ":" + app.config["chain_port"] + "/", app.config["chain_api_key"])
    database.init()
    ###Update database at queryInterval and serve flask app
    p = Process(target=update, args=(database,))
    p.start()
    serve(app, host='0.0.0.0', port=app.config["app_api_port"])
    p.join()

if __name__ == "__main__":
    main()
