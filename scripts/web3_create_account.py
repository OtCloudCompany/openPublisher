from accounts.models import Profile
from django.conf import settings
import json


def run():
    web3 = settings.W3
    if web3.is_connected():
        new_account = web3.eth.account.create()
        print("newAcc", f"key={web3.to_hex(new_account.key)}, account={new_account.address}")
        # print(web3.eth.accounts)

    else:
        print("No connection to network")

