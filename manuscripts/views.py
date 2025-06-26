import json

from manuscripts.models import Manuscript, Author
from utilities import CustomUUIDEncoder
from json import JSONDecodeError
from django.conf import settings
from django.http import JsonResponse
from rest_framework import permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from django.db import transaction

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class ManuscriptPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100



class GetLocalManuscripts(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ManuscriptPagination
    
    def get(self, request, *args, **kwargs):
        # Get all manuscripts
        manuscripts = Manuscript.objects.all().order_by('-submitted')
        
        # Initialize paginator
        paginator = self.pagination_class()
        paginated_manuscripts = paginator.paginate_queryset(manuscripts, request)
        
        # Prepare the response data
        manuscript_list = []
        for manuscript in paginated_manuscripts:
            manuscript_data = {
                'id': manuscript.pk,
                'title': manuscript.title,
                'abstract': manuscript.abstract,
                'keywords': manuscript.keywords,
                'tx_receipt': manuscript.tx_receipt,
                'submitted_by': manuscript.submitted_by.username if manuscript.submitted_by else None,
                'authors': [
                    {
                        'id': author.id,
                        'first_name': author.first_name,
                        'last_name': author.last_name,
                        'email': author.email,
                        'affiliation': author.affiliation
                    }
                    for author in manuscript.authors.all()
                ],
                'submitted': manuscript.submitted
            }
            manuscript_list.append(manuscript_data)
        
        return paginator.get_paginated_response(manuscript_list)


class GetLocalManuscriptById(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, manuscript_id, *args, **kwargs):
        try:
            manuscript = Manuscript.objects.get(pk=manuscript_id)
            
            # Prepare the detailed manuscript data
            manuscript_data = {
                'id': manuscript.pk,
                'title': manuscript.title,
                'abstract': manuscript.abstract,
                'keywords': manuscript.keywords,
                'tx_receipt': manuscript.tx_receipt,
                'submitted_by': manuscript.submitted_by.username if manuscript.submitted_by else None,
                'authors': [
                    {
                        'id': author.id,
                        'first_name': author.first_name,
                        'last_name': author.last_name,
                        'email': author.email,
                        'affiliation': author.affiliation
                    }
                    for author in manuscript.authors.all()
                ],
                'submitted': manuscript.submitted,
            }
            
            return JsonResponse(manuscript_data, status=status.HTTP_200_OK)
            
        except Manuscript.DoesNotExist:
            return JsonResponse(
                {"result": "error", "message": f"Manuscript {manuscript_id} not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class SubmitManuscript(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]
    model = Manuscript

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        try:
            manuscript_data = JSONParser().parse(request)
            manuscript_data.update({"submitted_by_id": self.request.user.pk})
        except JSONDecodeError:
            return JsonResponse(
                {"result": "error", "message": "JSON decoding error"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # First create the author(s)
        authors_data = manuscript_data.get("authors", [])
        author_ids = []

        for author_data in authors_data:
            # Create or get the author
            author, created = Author.objects.get_or_create(
                email=author_data['email'],
                defaults={
                    'first_name': author_data['first_name'],
                    'last_name': author_data['last_name'],
                    'affiliation': author_data['affiliation']
                }
            )
            author_ids.append(author.id)

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
        try:
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        except Exception as e:
            print("send_raw_transaction failed", e)

        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        resp_data = {
            "status": tx_receipt.status,
            "block_number": tx_receipt.blockNumber,
            "gas_used": tx_receipt.gasUsed,
            "tx_index": tx_receipt.transactionIndex
        }

        if tx_receipt.status == 1:  # save manuscript data to db

            try:

                manuscript = Manuscript.objects.create(
                    title=manuscript_data.get("title"),
                    abstract=manuscript_data.get("abstract"),
                    keywords=manuscript_data.get("keywords"),
                    tx_receipt=tx_receipt,
                    submitted_by_id=manuscript_data.get("submitted_by_id"),
                )
                # Update the authors field to use IDs instead of dict
                manuscript_data['authors'] = author_ids
                manuscript.authors.set(author_ids)

                resp_data["manuscript_id"] = manuscript.pk
            except Exception as e:
                print("Error saving manuscript to db", e)
                resp_data["error"] = f"Error saving manuscript to db: {e}"

        return JsonResponse(data=resp_data, status=status.HTTP_201_CREATED)
