import json
from flask import Flask
import time
from src.database import Database


app = Flask(__name__)

@app.route("/")
def doNothing():
    return "Hello!"

def printJson(jsonData):
    print(json.dumps(jsonData, indent = 4))


###main function - initialize db and run update script every n interval
# def main():
#     with open('../config.json') as f:
#         config = json.load(f)
#         app.config.update(config)
#
#     database = Database(app.config["databasePath"], app.config["chainUrl"] + ":" + app.config["port"])
#     database.init()
#     while True:
#         database.queryAndUpdate()
#         time.sleep(app.config["queryChainInterval"])
#
#
# if __name__ == '__main__':
#    p = Process(target=main)
#    p.start()
#    app.run(debug=True, use_reloader=False)
#    p.join()
