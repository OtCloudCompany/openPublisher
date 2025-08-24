

from solcx import compile_source, install_solc,set_solc_version, get_installable_solc_versions, get_installed_solc_versions

# Install specific version of solc (for example, '0.8.0')
install_solc('0.8.10')
set_solc_version('0.8.10')
from django.conf import settings
import os

def run():
    web3 = settings.W3
    contract_src = os.path.join(settings.BASE_DIR, 'JournalContract.sol')
    # contract_src = '../JournalContract.sol'

    compiled_sol = compile_source(open(contract_src).read())
    contract_interface = compiled_sol['<stdin>:JournalContract']
    # contract_interface = compiled_sol['JournalContract']

    bytecode = contract_interface['bin']
    abi = contract_interface['abi']

    contract = web3.eth.contract(abi=abi, bytecode=bytecode)
    tx_data = contract.constructor().build_transaction({
        'from': settings.W3_OWNERS_ADDRESS,
        'nonce': web3.eth.get_transaction_count(settings.W3_OWNERS_ADDRESS),
        'gas': 1728712,
        'gasPrice': web3.to_wei('21', 'gwei')
    })

    signed_tx = web3.eth.account.sign_transaction(tx_data, settings.W3_PRIV_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    contract_address = tx_receipt['contractAddress']
    print(f"Contract deployed at: {contract_address}")
    
    # Save the new ABI to JournalContract.json
    import json
    contract_json_path = os.path.join(settings.BASE_DIR, 'JournalContract.json')
    with open(contract_json_path, 'w') as f:
        json.dump({"abi": abi}, f, indent=2)
    print(f"Updated ABI saved to {contract_json_path}")
