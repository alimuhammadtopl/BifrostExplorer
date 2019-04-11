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
