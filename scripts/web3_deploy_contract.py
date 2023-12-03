from accounts.models import Profile
from django.conf import settings
import json
import os


def run():
    web3 = settings.W3
    owners_account = settings.W3_OWNERS_ADDRESS
    if web3.is_connected():
        # Load contract ABI and bytecode from Remix compilation output
        with open("JournalContract.json", 'r') as f:
            compiled_contract = json.load(f)

        abi = compiled_contract['abi']
        bytecode = compiled_contract['bytecode']

        journal_contract = web3.eth.contract(abi=abi, bytecode=bytecode)
        tx_hash = journal_contract.constructor().transact({'from': owners_account})
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        contract_address = tx_receipt.contractAddress

        print("Contract deployed at => ", contract_address)

    else:
        print("No connection to network")

