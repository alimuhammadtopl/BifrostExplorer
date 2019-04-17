import sqlite3
import json
import numpy as np
from LokiPy import Requests

###########################################################
##############Query database for api endpoints#############
###########################################################

def block_by_id(database, block_id):
    database.conn = sqlite3.connect(database.filename)
    database.cur = database.conn.cursor()
    c = database.cur.execute("SELECT blockJson FROM blocks WHERE blockHash=?", (block_id,))
    data = c.fetchone()
    response = None
    if data is not None:
      response = json.loads(data[0])
    database.conn.close()
    return response

def block_by_number(database, block_number):
    database.conn = sqlite3.connect(database.filename)
    database.cur = database.conn.cursor()
    c = database.cur.execute("SELECT blockJson FROM blocks WHERE blockNumber=?", (block_number,))
    data = c.fetchone()
    response = None
    if data is not None:
      response = json.loads(data[0])
    database.conn.close()
    return response

def transaction_by_id(database, tx_id):
    database.conn = sqlite3.connect(database.filename)
    database.cur = database.conn.cursor()
    c = database.cur.execute("SELECT txJson FROM transactions WHERE txHash=?", (tx_id,))
    data = c.fetchone()
    response = None
    if data is not None:
      response = json.loads(data[0])
    database.conn.close()
    return response

### Returns transaction jsons for all transactions the entered public key is involved in as a to or from address (note: issuers are not included)
###Consider removing "transactions" field from result json to standardize the results for instance with transaction_from_mempool
def transactions_by_public_key(database, public_key):
    database.conn = sqlite3.connect(database.filename)
    database.cur = database.conn.cursor()
    c = database.cur.execute("SELECT transactions FROM addresses WHERE publicKey=?", (public_key,))
    data = c.fetchone()
    tx_jsons = np.array([])
    if data is not None:
      transactions = np.array(data[0].split(","))
      for transaction in transactions:
          c = database.cur.execute("SELECT txJson FROM transactions WHERE txHash=?", (transaction,))
          data = c.fetchone()
          if data is not None:
              tx_jsons = np.append(tx_jsons, json.loads(data[0]))
    # response = {
    #     "transactions": tx_jsons.tolist()
    # }
    database.conn.close()
    return tx_jsons.tolist()

def transactions_by_block_number(database, block_number):
    database.conn = sqlite3.connect(database.filename)
    database.cur = database.conn.cursor()
    c = database.cur.execute("SELECT transactions FROM blocks WHERE blockNumber=?", (block_number,))
    data = c.fetchone()
    tx_jsons = np.array([])
    if data is not None:
      transactions = np.array(data[0].split(","))
      for transaction in transactions:
          c = database.cur.execute("SELECT txJson FROM transactions WHERE txHash=?", (transaction,))
          data = c.fetchone()
          if data is not None:
              tx_jsons = np.append(tx_jsons, json.loads(data[0]))

    # response = {
    #     "transactions": tx_jsons.tolist()
    # }
    database.conn.close()
    return tx_jsons.tolist()

def transactions_by_block_id(database, block_id):
    database.conn = sqlite3.connect(database.filename)
    database.cur = database.conn.cursor()
    c = database.cur.execute("SELECT transactions FROM blocks WHERE blockHash=?", (block_id,))
    data = c.fetchone()
    tx_jsons = np.array([])
    if data is not None:
      transactions = np.array(data[0].split(","))
      for transaction in transactions:
          c = database.cur.execute("SELECT txJson FROM transactions WHERE txHash=?", (transaction,))
          data = c.fetchone()
          if data is not None:
              tx_jsons = np.append(tx_jsons, json.loads(data[0]))
    # response = {
    #     "transactions": tx_jsons.tolist()
    # }
    database.conn.close()
    return tx_jsons.tolist()

def transactions_by_asset_code(database, asset_code):
    database.conn = sqlite3.connect(database.filename)
    database.cur = database.conn.cursor()
    c = database.cur.execute("SELECT transactions FROM assets WHERE assetCode=?", (asset_code,))
    data = c.fetchone()
    tx_jsons = np.array([])
    if data is not None:
      transactions = np.array(data[0].split(","))
      for transaction in transactions:
          c = database.cur.execute("SELECT txJson FROM transactions WHERE txHash=?", (transaction,))
          data = c.fetchone()
          if data is not None:
              tx_jsons= np.append(tx_jsons, json.loads(data[0]))
    # response = {
    #     "transactions": tx_jsons.tolist()
    # }
    database.conn.close()
    return tx_jsons.tolist()

def transactions_by_issuer(database, issuer):
    database.conn = sqlite3.connect(database.filename)
    database.cur = database.conn.cursor()
    c = database.cur.execute("SELECT transactions FROM issuers WHERE issuer=?", (issuer,))
    data = c.fetchone()
    tx_jsons = np.array([])
    if data is not None:
      transactions = np.array(data[0].split(","))
      for transaction in transactions:
          c = database.cur.execute("SELECT txJson FROM transactions WHERE txHash=?", (transaction,))
          data = c.fetchone()
          if data is not None:
              tx_jsons = np.append(tx_jsons, json.loads(data[0]))
    # response = {
    #     "transactions": tx_jsons.tolist()
    # }
    database.conn.close()
    return tx_jsons.tolist()

def transactions_by_issuer_by_asset_code(database, issuer, asset_code):
    database.conn = sqlite3.connect(database.filename)
    database.cur = database.conn.cursor()
    c = database.cur.execute("SELECT transactions FROM issuers WHERE issuer=?", (issuer,))
    data = c.fetchone()
    tx_jsons = np.array([])
    if data is not None:
      issuer_transactions = np.array(data[0].split(","))
      c = database.cur.execute("SELECT transactions FROM assets WHERE assetCode=?", (asset_code,))
      data = c.fetchone()
      if data is not None:
          asset_code_transactions = np.array(data[0].split(","))
          transactions = np.intersect1d(issuer_transactions, asset_code_transactions)
          # transactions = list(set(issuer_transactions).intersection(asset_code_transactions))
          for transaction in transactions:
              c = database.cur.execute("SELECT txJson FROM transactions WHERE txHash=?", (transaction,))
              data = c.fetchone()
              if data is not None:
                  tx_jsons = np.append(tx_jsons, json.loads(data[0]))
    # response = {
    #     "transactions": tx_jsons.tolist()
    # }
    database.conn.close()
    return tx_jsons.tolist()

def transactions_in_mempool(database):
    try:
      database.loki_obj = Requests.LokiPy()
      database.loki_obj.setUrl(database.chain_full_url)
      if database.chain_api_key is not None:
          database.loki_obj.setApiKey(database.chain_api_key)
      response = database.loki_obj.getMempool()
      result = json.loads(json.dumps(response))["result"]
      return result
    except Exception as e:
      print("Could not get mempool from chain: ", e)
      pass

def number_of_confirmed_transactions(database):
    database.conn = sqlite3.connect(database.filename)
    database.cur = database.conn.cursor()
    c = database.cur.execute("SELECT Count(*) FROM transactions")
    data = c.fetchone()
    response = None
    if data is not None:
      response = {
          "number": data[0]
      }
    database.conn.close()
    return response

def current_block_height(database):
    database.conn = sqlite3.connect(database.filename)
    database.cur = database.conn.cursor()
    c = database.cur.execute("SELECT MAX(blockNumber) FROM blocks")
    data = c.fetchone()
    response = None
    if data is not None:
      response = {
          "height": data[0]
      }
    database.conn.close()
    return response

###Timestamp of genesis block is 0 so disregard it by reducing block height by 1 in average calculation
def average_block_delay(database):
    database.conn = sqlite3.connect(database.filename)
    database.cur = database.conn.cursor()
    c = database.cur.execute("SELECT timestamp FROM blocks WHERE blockNumber=?", (2,))
    timestamp_2 = c.fetchone()
    c = database.cur.execute("SELECT MAX(blockNumber) FROM blocks")
    block_height = c.fetchone()
    response = None
    if timestamp_2 is not None and  block_height is not None:
      c = database.cur.execute("SELECT timestamp FROM blocks WHERE blockNumber=?", (block_height[0],))
      timestamp_height = c.fetchone()
      if timestamp_height is not None:
          average_delay = int((int(timestamp_height[0]) - int(timestamp_2[0]))/(block_height[0] - 1))
          response = {
              "averageDelay": average_delay
          }
    database.conn.close()
    return response

###Handles the case where block parameters are reversed since negatives cancel each other in average_delay calculation
def average_delay_between_specified_blocks(database, block_1, block_2):
    database.conn = sqlite3.connect(database.filename)
    database.cur = database.conn.cursor()
    c = database.cur.execute("SELECT timestamp FROM blocks WHERE blockNumber=?", (block_1,))
    timestamp_1 = c.fetchone()
    c = database.cur.execute("SELECT timestamp FROM blocks WHERE blockNumber=?", (block_2,))
    timestamp_2 = c.fetchone()
    response = None
    if timestamp_1 is not None and timestamp_2 is not None:
      average_delay = int((int(timestamp_2[0]) - int(timestamp_1[0]))/(block_2 - block_1))
      response = {
          "averageDelay": average_delay
      }
    database.conn.close()
    return response
