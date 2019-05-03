import sqlite3
import json
import numpy as np
from LokiPy import Requests

###########################################################
##############Query database for api endpoints#############
###########################################################

def block_by_hash(params, _id, conn, logger, config):
    block_hash = params["blockHash"]
    c = conn.cursor()
    c.execute("SELECT blockJson FROM blocks WHERE blockHash=?", (block_hash,))
    data = c.fetchone()
    response = None
    if data is not None:
      response = json.loads(data[0])
    return response

def block_by_number(params, _id, conn, logger, config):
    block_number = params["blockNumber"]
    c = conn.cursor()
    c.execute("SELECT blockJson FROM blocks WHERE blockNumber=?", (block_number,))
    data = c.fetchone()
    response = None
    if data is not None:
      response = json.loads(data[0])
    return response

def transaction_by_hash(params, _id, conn, logger, config):
    tx_hash = params["transactionHash"]
    c = conn.cursor()
    c.execute("SELECT txJson FROM transactions WHERE txHash=?", (tx_hash,))
    data = c.fetchone()
    response = None
    if data is not None:
      response = json.loads(data[0])
    return response

### Returns transaction jsons for all transactions the entered public key is involved in as a to or from address (note: issuers are not included)
###Consider removing "transactions" field from result json to standardize the results for instance with transaction_from_mempool
def transactions_by_public_key(params, _id, conn, logger, config):
    public_key = params["publicKey"]
    c = conn.cursor()
    c.execute("SELECT transactions FROM addresses WHERE publicKey=?", (public_key,))
    data = c.fetchone()
    tx_jsons = np.array([])
    if data is not None:
      transactions = np.array(data[0].split(","))
      for transaction in transactions:
          c.execute("SELECT txJson FROM transactions WHERE txHash=?", (transaction,))
          data = c.fetchone()
          if data is not None:
              tx_jsons = np.append(tx_jsons, json.loads(data[0]))
    # response = {
    #     "transactions": tx_jsons.tolist()
    # }
    return tx_jsons.tolist()

def transactions_by_block_number(params, _id, conn, logger, config):
    block_number = params["blockNumber"]
    c = conn.cursor()
    c.execute("SELECT transactions FROM blocks WHERE blockNumber=?", (block_number,))
    data = c.fetchone()
    tx_jsons = np.array([])
    if data is not None:
      transactions = np.array(data[0].split(","))
      for transaction in transactions:
          c.execute("SELECT txJson FROM transactions WHERE txHash=?", (transaction,))
          data = c.fetchone()
          if data is not None:
              tx_jsons = np.append(tx_jsons, json.loads(data[0]))

    # response = {
    #     "transactions": tx_jsons.tolist()
    # }
    return tx_jsons.tolist()

def transactions_by_block_hash(params, _id, conn, logger, config):
    block_hash = params["blockHash"]
    c = conn.cursor()
    c.execute("SELECT transactions FROM blocks WHERE blockHash=?", (block_hash,))
    data = c.fetchone()
    tx_jsons = np.array([])
    if data is not None:
      transactions = np.array(data[0].split(","))
      for transaction in transactions:
          c.execute("SELECT txJson FROM transactions WHERE txHash=?", (transaction,))
          data = c.fetchone()
          if data is not None:
              tx_jsons = np.append(tx_jsons, json.loads(data[0]))
    # response = {
    #     "transactions": tx_jsons.tolist()
    # }
    return tx_jsons.tolist()

def transactions_by_asset_code(params, _id, conn, logger, config):
    asset_code = params["assetCode"]
    c = conn.cursor()
    c.execute("SELECT transactions FROM assets WHERE assetCode=?", (asset_code,))
    data = c.fetchone()
    tx_jsons = np.array([])
    if data is not None:
      transactions = np.array(data[0].split(","))
      for transaction in transactions:
          c.execute("SELECT txJson FROM transactions WHERE txHash=?", (transaction,))
          data = c.fetchone()
          if data is not None:
              tx_jsons= np.append(tx_jsons, json.loads(data[0]))
    # response = {
    #     "transactions": tx_jsons.tolist()
    # }
    return tx_jsons.tolist()

def transactions_by_issuer(params, _id, conn, logger, config):
    issuer = params["issuer"]
    c = conn.cursor()
    c.execute("SELECT transactions FROM issuers WHERE issuer=?", (issuer,))
    data = c.fetchone()
    tx_jsons = np.array([])
    if data is not None:
      transactions = np.array(data[0].split(","))
      for transaction in transactions:
          c.execute("SELECT txJson FROM transactions WHERE txHash=?", (transaction,))
          data = c.fetchone()
          if data is not None:
              tx_jsons = np.append(tx_jsons, json.loads(data[0]))
    # response = {
    #     "transactions": tx_jsons.tolist()
    # }
    return tx_jsons.tolist()

def transactions_by_issuer_by_asset_code(params, _id, conn, logger, config):
    asset_code = params["assetCode"]
    issuer = params["issuer"]
    c = conn.cursor()
    c.execute("SELECT transactions FROM issuers WHERE issuer=?", (issuer,))
    data = c.fetchone()
    tx_jsons = np.array([])
    if data is not None:
      issuer_transactions = np.array(data[0].split(","))
      c.execute("SELECT transactions FROM assets WHERE assetCode=?", (asset_code,))
      data = c.fetchone()
      if data is not None:
          asset_code_transactions = np.array(data[0].split(","))
          transactions = np.intersect1d(issuer_transactions, asset_code_transactions)
          # transactions = list(set(issuer_transactions).intersection(asset_code_transactions))
          for transaction in transactions:
              c.execute("SELECT txJson FROM transactions WHERE txHash=?", (transaction,))
              data = c.fetchone()
              if data is not None:
                  tx_jsons = np.append(tx_jsons, json.loads(data[0]))
    # response = {
    #     "transactions": tx_jsons.tolist()
    # }
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

def number_of_confirmed_transactions(params, _id, conn, logger, config):
    c = conn.cursor()
    c.execute("SELECT Count(*) FROM transactions")
    data = c.fetchone()
    response = None
    if data is not None:
      response = {
          "number": data[0]
      }
    return response

def current_block_height(params, _id, conn, logger, config):
    c = conn.cursor()
    c.execute("SELECT MAX(blockNumber) FROM blocks")
    data = c.fetchone()
    response = None
    if data is not None:
      response = {
          "height": data[0]
      }
    return response

###Timestamp of genesis block is 0 so disregard it by reducing block height by 1 in average calculation
def average_block_delay(params, _id, conn, logger, config):
    c = conn.cursor()
    c.execute("SELECT timestamp FROM blocks WHERE blockNumber=?", (2,))
    timestamp_2 = c.fetchone()
    c.execute("SELECT MAX(blockNumber) FROM blocks")
    block_height = c.fetchone()
    response = None
    if timestamp_2 is not None and  block_height is not None:
      c.execute("SELECT timestamp FROM blocks WHERE blockNumber=?", (block_height[0],))
      timestamp_height = c.fetchone()
      if timestamp_height is not None:
          average_delay = int((int(timestamp_height[0]) - int(timestamp_2[0]))/(block_height[0] - 1))
          response = {
              "averageDelay": average_delay
          }
    return response

###Handles the case where block parameters are reversed since negatives cancel each other in average_delay calculation
def average_delay_between_specified_blocks(params, _id, conn, logger, config):
    block_1 = params["block1"]
    block_2 = params["block2"]
    c = conn.cursor()
    c.execute("SELECT timestamp FROM blocks WHERE blockNumber=?", (block_1,))
    timestamp_1 = c.fetchone()
    c.execute("SELECT timestamp FROM blocks WHERE blockNumber=?", (block_2,))
    timestamp_2 = c.fetchone()
    response = None
    if timestamp_1 is not None and timestamp_2 is not None:
      average_delay = int((int(timestamp_2[0]) - int(timestamp_1[0]))/(block_2 - block_1))
      response = {
          "averageDelay": average_delay
      }
    return response
