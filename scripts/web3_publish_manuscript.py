from accounts.models import Profile
from django.conf import settings
import json


def run():
    web3 = settings.W3
    if web3.is_connected():
        # Load contract ABI and bytecode from Remix compilation output
        with open("JournalContract.json", 'r') as f:
            compiled_contract = json.load(f)

        abi = compiled_contract['abi']
        contract = web3.eth.contract(address=settings.W3_CONTRACT_ADDRESS, abi=abi)

        manuscript_data = {
            "title": "Sample Title 2",
            "abstract": "Another Sample Abstract",
            "authors": [
                {
                    "firstName": "Jane",
                    "lastName": "Doe",
                    "email": "jane@example.com",
                    "affiliatedInstitution": "Example University",
                    "isPrimaryAuthor": True,
                    "web3Address": "0xAddress1"
                },
                {
                    "firstName": "Alicia",
                    "lastName": "Smith",
                    "email": "alicia@example.com",
                    "affiliatedInstitution": "Different University",
                    "isPrimaryAuthor": False,
                    "web3Address": "0xAddress2"
                }
            ],
            "datePublished": "2023-11-25",
            "keywords": ["biology", "chemistry", "physics"]
        }
        json_data = json.dumps(manuscript_data)
        encoded_data = contract.encodeABI(fn_name='publishManuscript', args=[json_data])
        nonce = web3.eth.get_transaction_count(settings.W3_OWNERS_ADDRESS)
        transaction = {
            'to': settings.W3_CONTRACT_ADDRESS,
            'gas': 2000000,
            'gasPrice': web3.eth.gas_price,
            'nonce': nonce,
            'data': encoded_data,
        }
        signed_txn = web3.eth.account.sign_transaction(transaction, settings.W3_PRIV_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        print(f"Manuscript published on block number {tx_receipt.blockNumber}")

    else:
        print("No connection to network")

