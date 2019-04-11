###Utility functions for parsing transaction and block jsons to convert them to comma separated strings of a specific field

###Pretty prints json result
def printJson(jsonData):
    print(json.dumps(jsonData, indent = 4))

###parses txs array from a block and converts it to comma separated txHash string###
def createTxsString(blockResult):
    if "txs" in blockResult:
        txsSet = set()
        for tx in blockResult["txs"]:
            try:
                txsSet.add(tx["txHash"])
            except Exception as e:
                print("Could not get transaction hash from transaction instance in block: ", e)
                raise

        return ','.join(map(str, txsSet))
    else:
        return None

###parses a transaction and converts it to comma separated addresses string of to addresses###
###NOTE: Checks unique address
###Returns a string or None since toAddresses column accepts NULL values
def createToAddressesString(transactionResult):
    if "to" in transactionResult:
        addressesSet = set()
        for toInstance in transactionResult["to"]:
            try:
                addressesSet.add(toInstance["proposition"])
            except Exception as e:
                print("Could not get proposition from to instance in transaction: ", e)
                raise

        return ','.join(map(str, addressesSet))
    else:
        return None

###parses a transaction and converts it to comma separated addresses string of to addresses###
###NOTE: Checks unique address
###Returns a string or None since fromAddresses column accepts NULL values
def createFromAddressesString(transactionResult):
    if "from" in transactionResult:
        addressesSet = set()
        for fromInstance in transactionResult["from"]:
            try:
                addressesSet.add(fromInstance["proposition"])
            except Exception as e:
                print("Could not get proposition from from instance in transaction: ", e)
                raise

        return ','.join(map(str, addressesSet))
    else:
        return None


###parses a transaction and converts it to comma separated newBoxes string of newly created boxes ids###
###Returns a string or None since newBoxes column accepts NULL values
def createNewBoxesString(transactionResult):
    if "newBoxes" in transactionResult:
        newBoxesSet = set()
        for newBoxesInstance in transactionResult["newBoxes"]:
            newBoxesSet.add(newBoxesInstance)

        return ','.join(map(str, newBoxesSet))
    else:
        return None

###parses a transaction and converts it to comma separated boxesToRemove string of destroyed boxes ids###
###Returns a string or None since boxesToRemove column accepts NULL values
def createBoxesToRemoveString(transactionResult):
    if "boxesToRemove" in transactionResult:
        boxesToRemoveSet = set()
        for boxesToRemoveInstance in transactionResult["boxesToRemove"]:
            boxesToRemoveSet.add(boxesToRemoveInstance)

        return ','.join(map(str, boxesToRemoveSet))
    else:
        return None

###parses a transaction and converts it to comma separated signatures string of signatures created in the transaction###
###Returns a string or None since signatures column accepts NULL values
def createSignaturesString(transactionResult):
    if "signatures" in transactionResult:
        signaturesSet = set()
        for signatureInstance in transactionResult["signatures"]:
            signaturesSet.add(signatureInstance)

        return ','.join(map(str, signaturesSet))
    else:
        return None
