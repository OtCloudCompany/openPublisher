from django.conf import settings
import json


def run():
    web3 = settings.W3
    sender_account = settings.W3_OWNERS_ADDRESS
    print(sender_account)
    if web3.is_connected():
        # Load contract ABI and bytecode from Remix compilation output
        with open("JournalContract.json", 'r') as f:
            compiled_contract = json.load(f)

        contract = web3.eth.contract(
            address=settings.W3_CONTRACT_ADDRESS,
            abi=compiled_contract['abi']
        )

        manuscript_details = contract.functions.getManuscriptsBySubmitter(sender_account).call()

        print(manuscript_details)

    else:
        print("No connection to network")

