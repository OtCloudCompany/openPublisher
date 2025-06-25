import json
import os
from web3 import Web3
from solcx import compile_standard, install_solc
from django.conf import settings

def deploy_contract():
    # Install specific solidity version
    install_solc('0.8.0')
    
    # Read the Solidity contract
    with open("../JournalContract.sol", "r") as file:
        contract_source = file.read()

    # Compile the contract
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"JournalContract.sol": {"content": contract_source}},
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                    }
                }
            },
        },
        solc_version="0.8.0",
    )

    # Save the compilation output
    with open("JournalContract.json", "w") as file:
        json.dump(compiled_sol, file)

    # Get contract binary and ABI
    contract_interface = compiled_sol['contracts']['JournalContract.sol']['JournalContract']
    bytecode = contract_interface['evm']['bytecode']['object']
    abi = contract_interface['abi']

    # Connect to Sepolia
    w3 = Web3(Web3.HTTPProvider(settings.W3_ENDPOINT))
    
    if not w3.is_connected():
        raise Exception("Couldn't connect to Sepolia network")

    # Get chain ID
    chain_id = w3.eth.chain_id

    # Get account details
    my_address = settings.W3_OWNERS_ADDRESS
    private_key = settings.W3_PRIV_KEY

    # Create contract
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Get nonce
    nonce = w3.eth.get_transaction_count(my_address)

    # Build transaction
    transaction = Contract.constructor().build_transaction(
        {
            "chainId": chain_id,
            "from": my_address,
            "nonce": nonce,
            "gasPrice": w3.eth.gas_price,
        }
    )

    # Sign transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

    # Send transaction
    print("Deploying contract...")
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    # Wait for transaction receipt
    print("Waiting for transaction to be mined...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print(f"Contract deployed to {tx_receipt.contractAddress}")
    
    # Save contract address
    with open("contract_address.txt", "w") as file:
        file.write(tx_receipt.contractAddress)

    return tx_receipt.contractAddress, abi

if __name__ == "__main__":
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openPublisher.settings')
    django.setup()
    
    contract_address, _ = deploy_contract()
    print(f"Contract deployed successfully at: {contract_address}")