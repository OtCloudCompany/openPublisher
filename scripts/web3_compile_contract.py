from solc import compile_source
from django.conf import settings
import os


def run():
    web3 = settings.W3
    # contract_src = os.path.join(settings.BASE_DIR, 'contractFiles', 'JournalContract.sol')
    contract_src = 'JournalContract.sol'

    compiled_sol = compile_source(open(contract_src).read())
    # contract_interface = compiled_sol['<stdin>:JournalContract']
    contract_interface = compiled_sol['JournalContract']

    bytecode = contract_interface['bin']
    abi = contract_interface['abi']

    contract = web3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    tx_data = contract.constructor().buildTransaction({
        'from': settings.W3_OWNERS_ADDRESS,
        'nonce': web3.eth.get_transaction_count(settings.W3_OWNERS_ADDRESS),
        'gas': 1728712,
        'gasPrice': web3.toWei('21', 'gwei')
    })

    signed_tx = web3.eth.account.sign_transaction(tx_data, settings.W3_PRIV_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    contract_address = tx_receipt['contractAddress']

    print(tx_receipt)
    print('=======================================')
    print(contract_address)


