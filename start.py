import os
import json
from waitress import serve
from src.app import app
from src.database import Database
import time
from multiprocessing import Process

###main function - initialize db and run update script every n interval
def main():
    with open('config.json') as f:
        config = json.load(f)
        app.config.update(config)

    database = Database(app.config["databasePath"], app.config["chainUrl"] + ":" + app.config["port"])
    ### initialize db and run update script every n interval
    database.init()
    while True:
        database.queryAndUpdate()
        time.sleep(app.config["queryChainInterval"])

###Make such that database is initialized first and then update and app serving are done simultaneously
p = Process(target=main)
p.start()
serve(app, host='0.0.0.0', port=5000)
p.join()
