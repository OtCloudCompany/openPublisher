import json

from manuscripts.models import Manuscript
from utilities import CustomUUIDEncoder
from json import JSONDecodeError
from django.conf import settings
from django.http import JsonResponse
from rest_framework import permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView


class SubmitManuscript(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]
    model = Manuscript

    def post(self, request, *args, **kwargs):

        try:
            manuscript_data = JSONParser().parse(request)
            manuscript_data.update({"submitted_by_id": self.request.user.pk})
        except JSONDecodeError:
            return JsonResponse(
                {"result": "error", "message": "JSON decoding error"},
                status=status.HTTP_400_BAD_REQUEST
            )

        web3 = settings.W3
        if not web3.is_connected():
            return JsonResponse(
                {"result": "error", "message": "No connection to web3 endpoint"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        with open("JournalContract.json", 'r') as f:
            compiled_contract = json.load(f)

        abi = compiled_contract['abi']
        contract = web3.eth.contract(address=settings.W3_CONTRACT_ADDRESS, abi=abi)

        json_string = json.dumps(manuscript_data, cls=CustomUUIDEncoder)
        encoded_data = contract.encodeABI(fn_name='publishManuscript', args=[json_string])
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

        resp_data = {
            "status": tx_receipt.status,
            "block_number": tx_receipt.blockNumber,
            "gas_used": tx_receipt.gasUsed,
            "tx_index": tx_receipt.transactionIndex
        }

        if tx_receipt.status == 1:  # save manuscript data to db
            manuscript = Manuscript.objects.create(
                title=manuscript_data.get("title"),
                abstract=manuscript_data.get("abstract"),
                keywords=manuscript_data.get("keywords"),
                submitted_by_id=manuscript_data.get("submitted_by_id"),
            )
            manuscript.authors.set(manuscript_data.get("authors"))

            new_manuscript = manuscript.save()
            resp_data["manuscript_id"] = new_manuscript.pk

        return JsonResponse(data=resp_data, status=status.HTTP_201_CREATED)
