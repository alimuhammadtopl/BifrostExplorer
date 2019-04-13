###Utility functions for parsing transaction and block jsons to convert them to comma separated strings of a specific field

###Pretty prints json result
def print_json(json_data):
    print(json.dumps(json_data, indent = 4))

###parses txs array from a block and converts it to comma separated txHash string###
def create_transactions_string(block_result):
    if "txs" in block_result:
        txs_set = set()
        for tx in block_result["txs"]:
            try:
                txs_set.add(tx["txHash"])
            except Exception as e:
                print("Could not get transaction hash from transaction instance in block: ", e)
                raise

        return ','.join(map(str, txs_set))
    else:
        return None

###parses a transaction and converts it to comma separated addresses string of to addresses###
###NOTE: Checks unique address
###Returns a string or None since toAddresses column accepts NULL values
def create_to_addresses_string(transaction_result):
    if "to" in transaction_result:
        addresses_set = set()
        for to_instance in transaction_result["to"]:
            try:
                addresses_set.add(to_instance["proposition"])
            except Exception as e:
                print("Could not get proposition from to instance in transaction: ", e)
                raise

        return ','.join(map(str, addresses_set))
    else:
        return None

###parses a transaction and converts it to comma separated addresses string of to addresses###
###NOTE: Checks unique address
###Returns a string or None since fromAddresses column accepts NULL values
def create_from_addresses_string(transaction_result):
    if "from" in transaction_result:
        addresses_set = set()
        for from_instance in transaction_result["from"]:
            try:
                addresses_set.add(from_instance["proposition"])
            except Exception as e:
                print("Could not get proposition from from instance in transaction: ", e)
                raise

        return ','.join(map(str, addresses_set))
    else:
        return None


###parses a transaction and converts it to comma separated newBoxes string of newly created boxes ids###
###Returns a string or None since newBoxes column accepts NULL values
def create_new_boxes_string(transaction_result):
    if "newBoxes" in transaction_result:
        new_boxes_set = set()
        for new_boxes_instance in transaction_result["newBoxes"]:
            new_boxes_set.add(new_boxes_instance)

        return ','.join(map(str, new_boxes_set))
    else:
        return None

###parses a transaction and converts it to comma separated boxesToRemove string of destroyed boxes ids###
###Returns a string or None since boxesToRemove column accepts NULL values
def create_boxes_to_remove_string(transaction_result):
    if "boxesToRemove" in transaction_result:
        boxes_to_remove_set = set()
        for boxes_to_remove_instance in transaction_result["boxesToRemove"]:
            boxes_to_remove_set.add(boxes_to_remove_instance)

        return ','.join(map(str, boxes_to_remove_set))
    else:
        return None

###parses a transaction and converts it to comma separated signatures string of signatures created in the transaction###
###Returns a string or None since signatures column accepts NULL values
def create_signatures_string(transaction_result):
    if "signatures" in transaction_result:
        signatures_set = set()
        for signature_instance in transaction_result["signatures"]:
            signatures_set.add(signature_instance)

        return ','.join(map(str, signatures_set))
    else:
        return None
