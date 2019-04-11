import os
import json
from waitress import serve
from src.app import app
from src.database import Database
import time
from multiprocessing import Process

###update function - initialize db and run update script every n interval
def update(database):
    while True:
        database.queryAndUpdate()
        time.sleep(app.config["queryChainInterval"])

###Read configurations from config
with open('config.json') as f:
    config = json.load(f)
    app.config.update(config)

###Initialize the database according to the configurations
database = Database(app.config["databasePath"], app.config["chainUrl"] + ":" + app.config["port"])
database.init()
###Update database at queryInterval and serve flask app
p = Process(target=update, args=(database,))
p.start()
serve(app, host='0.0.0.0', port=5000)
p.join()
