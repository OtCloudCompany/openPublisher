import json

from django.shortcuts import get_object_or_404

from accounts.models import Profile
from journals.models import Journal
from manuscripts.models import Manuscript, Author, ManuscriptEvent, ReviewerAssignment
from utilities import CustomUUIDEncoder
from json import JSONDecodeError
from django.conf import settings
from django.http import JsonResponse
from rest_framework import permissions, status
from rest_framework.parsers import JSONParser
from django.db import transaction

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication


class Sepolia:
    def record_review(self, manuscript_id, reviewer_id, metadata):
        """
        Records a review submission event on the contract.
        Args:
            manuscript_id: The ID of the manuscript.
            reviewer_id: The ID of the reviewer.
            metadata: Additional metadata (dict) to store with the event.
        Returns:
            Transaction receipt or error dict.
        """
        if not self.web3.is_connected():
            return JsonResponse(
                {"result": "error", "message": "No connection to web3 endpoint"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        with open("JournalContract.json", 'r') as f:
            compiled_contract = json.load(f)
        abi = compiled_contract['abi']
        contract = self.web3.eth.contract(address=settings.W3_CONTRACT_ADDRESS, abi=abi)

        # Prepare the data for the contract call
        metadata_json = json.dumps(metadata, cls=CustomUUIDEncoder)
        encoded_data = contract.encodeABI(
            fn_name='recordReviewSubmission',
            args=[str(manuscript_id), str(reviewer_id), metadata_json]
        )
        nonce = self.web3.eth.get_transaction_count(settings.W3_OWNERS_ADDRESS)
        transaction = {
            'to': settings.W3_CONTRACT_ADDRESS,
            'gas': 2000000,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': nonce,
            'data': encoded_data,
        }

        signed_txn = self.web3.eth.account.sign_transaction(transaction, settings.W3_PRIV_KEY)
        try:
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        except Exception as e:
            return {'error': f'Error sending raw transaction: {e}'}

        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        if not tx_receipt:
            return JsonResponse(
                {"result": "error", "message": "Transaction receipt not found"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return tx_receipt

    def record_reviewer_assignment(self, manuscript_id, reviewer_id, metadata):
        """
        Records a reviewer assignment event on the contract.
        Args:
            manuscript_id: The ID of the manuscript.
            reviewer_id: The ID of the reviewer.
            metadata: Additional metadata (dict) to store with the event.
        Returns:
            Transaction receipt or error dict.
        """
        if not self.web3.is_connected():
            return JsonResponse(
                {"result": "error", "message": "No connection to web3 endpoint"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        with open("JournalContract.json", 'r') as f:
            compiled_contract = json.load(f)
        abi = compiled_contract['abi']
        contract = self.web3.eth.contract(address=settings.W3_CONTRACT_ADDRESS, abi=abi)

        # Prepare the data for the contract call
        metadata_json = json.dumps(metadata, cls=CustomUUIDEncoder)
        encoded_data = contract.encodeABI(
            fn_name='recordReviewerAssignment',
            args=[str(manuscript_id), str(reviewer_id), metadata_json]
        )
        nonce = self.web3.eth.get_transaction_count(settings.W3_OWNERS_ADDRESS)
        transaction = {
            'to': settings.W3_CONTRACT_ADDRESS,
            'gas': 2000000,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': nonce,
            'data': encoded_data,
        }

        signed_txn = self.web3.eth.account.sign_transaction(transaction, settings.W3_PRIV_KEY)
        try:
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        except Exception as e:
            return {'error': f'Error sending raw transaction: {e}'}

        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        if not tx_receipt:
            return JsonResponse(
                {"result": "error", "message": "Transaction receipt not found"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return tx_receipt
    def __init__(self):
        self.web3 = settings.W3
        with open("JournalContract.json", 'r') as f:
            compiled_contract = json.load(f)
        self.abi = compiled_contract['abi']
        self.contract = self.web3.eth.contract(
            address=settings.W3_CONTRACT_ADDRESS,
            abi=self.abi
        )

    def post_manuscript(self, manuscript):
        global tx_hash
        if not self.web3.is_connected():
            return JsonResponse(
                {"result": "error", "message": "No connection to web3 endpoint"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        with open("JournalContract.json", 'r') as f:
            compiled_contract = json.load(f)

        abi = compiled_contract['abi']
        contract = self.web3.eth.contract(address=settings.W3_CONTRACT_ADDRESS, abi=abi)

        json_string = json.dumps(manuscript, cls=CustomUUIDEncoder)
        encoded_data = contract.encodeABI(fn_name='publishManuscript', args=[json_string])
        nonce = self.web3.eth.get_transaction_count(settings.W3_OWNERS_ADDRESS)
        transaction = {
            'to': settings.W3_CONTRACT_ADDRESS,
            'gas': 2000000,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': nonce,
            'data': encoded_data,
        }

        signed_txn = self.web3.eth.account.sign_transaction(transaction, settings.W3_PRIV_KEY)
        try:
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        except Exception as e:
            # print("send_raw_transaction failed", e)
            return {'error': f'Error sending raw transaction: {e}'}

        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        if not tx_receipt:
            return JsonResponse(
                {"result": "error", "message": "Transaction receipt not found"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return tx_receipt


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class GetLocalManuscripts(APIView):
    authentication_classes = []
    permission_classes = []
    pagination_class = Pagination
    
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
                'journal_id': manuscript.journal_id_id,
                'keywords': manuscript.keywords,
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
                'status': manuscript.status
            }
            manuscript_list.append(manuscript_data)
        
        return paginator.get_paginated_response(manuscript_list)


class GetLocalManuscriptById(APIView):
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, manuscript_id, *args, **kwargs):
        try:
            manuscript = Manuscript.objects.get(pk=manuscript_id)
            
            # Prepare the detailed manuscript data
            manuscript_data = {
                'id': manuscript.pk,
                'title': manuscript.title,
                'abstract': manuscript.abstract,
                'keywords': [keyword.get('keyword') for keyword in manuscript.keywords],
                'journal_id': manuscript.journal_id_id,
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
                # 'journal_id': manuscript
                'status': manuscript.status,
                'provenance': [
                    {
                        'id': event.id,
                        'manuscript_id': event.manuscript_id,
                        'event_type': event.event_type,
                        'timestamp': event.timestamp,
                        'actor': event.actor_id,
                        'description': event.description,
                        'txn_hash': event.txn_hash,
                        'metadata': event.metadata,
                    }
                    for event in manuscript.get_provenance()
                ]
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
            manuscript_data.update({"journal_id": kwargs.get("journal_id")})
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

        sepolia = Sepolia()
        tx_receipt = sepolia.post_manuscript(manuscript_data)

        resp_data = {
            "status": tx_receipt.status,
            "block_number": tx_receipt.blockNumber,
            "gas_used": tx_receipt.gasUsed,
            "tx_index": tx_receipt.transactionIndex
        }

        if tx_receipt.status == 1:  # save manuscript data to db

            try:
                journal_id = manuscript_data.get("journal_id")
                if not journal_id:
                    return JsonResponse(
                        {"result": "error", "message": "Journal ID is required"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Ensure the journal exists
                journal = get_object_or_404(Journal, pk=journal_id)
            except Exception as e:
                print(f"Error finding journal with id {journal_id} ", e)
                resp_data["error"] = f"Error saving manuscript to db: {e}"

            try:
                manuscript = Manuscript.objects.create(
                    title=manuscript_data.get("title"),
                    abstract=manuscript_data.get("abstract"),
                    keywords=manuscript_data.get("keywords"),
                    journal_id=journal,
                    submitted_by_id=manuscript_data.get("submitted_by_id"),
                )
                # Update the authors field to use IDs instead of dict
                manuscript_data['authors'] = author_ids
                manuscript.authors.set(author_ids)

                resp_data["manuscript_id"] = manuscript.pk

                # record submission event
                txn_hash = tx_receipt.transactionHash.hex()
                if not txn_hash.startswith('0x'):
                    txn_hash = '0x' + txn_hash
                manuscript.record_submission(actor=request.user, txn_hash=txn_hash)
            except Exception as e:
                print("Error saving manuscript to db", e)
                resp_data["error"] = f"Error saving manuscript to db: {e}"

        return JsonResponse(data=resp_data, status=status.HTTP_201_CREATED)


class ChangeManuscriptStatus(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]
    model = Manuscript

    def post(self, request, manuscript_id, *args, **kwargs):
        try:
            manuscript = self.model.objects.get(pk=manuscript_id)
        except self.model.DoesNotExist:
            return JsonResponse(
                {"result": "error", 'message': 'Manuscript does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        req_status = self.request.GET.get("status")
        if req_status not in dict(Manuscript.Status.choices):
            return JsonResponse(
                {"result": "error", "message": "Invalid status"},
                status=status.HTTP_400_BAD_REQUEST
            )
        sepolia = Sepolia()
        if req_status == 'ACCEPTED':
            manuscript.status = Manuscript.Status.ACCEPTED
            tx_receipt = sepolia.post_manuscript(manuscript.to_json())
            txn_hash = tx_receipt.transactionHash.hex()
            if not txn_hash.startswith('0x'):
                txn_hash = '0x' + txn_hash
            manuscript.record_acceptance(actor=request.user, txn_hash=txn_hash)
        if req_status == 'REJECTED':
            manuscript.status = Manuscript.Status.REJECTED
            tx_receipt = sepolia.post_manuscript(manuscript.to_json())
            txn_hash = tx_receipt.transactionHash.hex()
            if not txn_hash.startswith('0x'):
                txn_hash = '0x' + txn_hash
            manuscript.record_rejection(actor=request.user, reason='', txn_hash=txn_hash)

        return JsonResponse(
            {"result": "success", "message": "Manuscript status updated"},
            status=status.HTTP_200_OK
        )

class AssignReviewer(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        journal_id = kwargs.get("journal_id")
        manuscript_id = kwargs.get("manuscript_id")
        selected_reviewer = self.request.GET.get("selected_reviewer")
        due_date = self.request.GET.get("due_date")  # Optional due date parameter


        if not selected_reviewer:
            return Response(
                {"result": "error", "message": "No reviewer selected"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Get the journal and verify it exists
                journal = get_object_or_404(Journal, id=journal_id)

                # Get the manuscript and verify it exists and belongs to the journal
                manuscript = get_object_or_404(
                    Manuscript,
                    id=manuscript_id,
                    journal_id=journal
                )

                # Get the reviewer profile
                reviewer = get_object_or_404(
                    Profile,
                    id=selected_reviewer,
                )

                # Check if manuscript is in a state where it can be assigned to a reviewer
                if manuscript.status not in [Manuscript.Status.ACCEPTED, Manuscript.Status.REVIEW]:
                    return Response(
                        {
                            "result": "error",
                            "message": "Manuscript is not in a state where reviewers can be assigned"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Check if reviewer is already assigned to this manuscript
                reviewer_is_assigned = ReviewerAssignment.objects.filter(
                        manuscript=manuscript,
                        reviewer=reviewer,
                        status__in=[
                            ReviewerAssignment.Status.PENDING,
                            ReviewerAssignment.Status.ACCEPTED
                        ]
                ).exists()
                if reviewer_is_assigned:
                    return Response(
                        {
                            "result": "error",
                            "message": "Reviewer is already assigned to this manuscript"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Create the reviewer assignment
                assignment = ReviewerAssignment.objects.create(
                    manuscript=manuscript,
                    reviewer=reviewer,
                    status=ReviewerAssignment.Status.PENDING,
                    due_date=due_date if due_date else None
                )

                # Record reviewer assignment on the contract
                sepolia = Sepolia()
                metadata = {
                    'reviewer_id': str(reviewer.id),
                    'reviewer_name': f"{reviewer.first_name} {reviewer.last_name}",
                    'reviewer_email': reviewer.email
                }
                tx_receipt = sepolia.record_reviewer_assignment(manuscript.id, reviewer.id, metadata)
                txn_hash = ''
                if isinstance(tx_receipt, dict) and 'error' in tx_receipt:
                    # Optionally handle error, e.g. log or notify
                    return Response(
                        {"result": "error", "message": tx_receipt['error']},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                else:
                    txn_hash = tx_receipt.transactionHash.hex()
                    if not txn_hash.startswith('0x'):
                        txn_hash = '0x' + txn_hash            

                # Assign the reviewer
                manuscript.reviewers.add(reviewer)             

                # Update manuscript status
                if manuscript.status == Manuscript.Status.SUBMISSION:
                    manuscript.status = Manuscript.Status.REVIEW
                    manuscript.save()
                # Record the event
                manuscript.create_event(
                    event_type=ManuscriptEvent.EventType.REVIEWER_ASSIGNED,
                    actor=request.user,
                    txn_hash=txn_hash,
                    metadata={
                        'reviewer_id': str(reviewer.id),
                        'reviewer_name': f"{reviewer.first_name} {reviewer.last_name}",
                        'reviewer_email': reviewer.email
                    }
                )
                resp_data = {
                    "result": "success",
                    "message": "Reviewer assigned successfully",
                    "data": {
                        "manuscript_id": manuscript.id,
                        "manuscript_title": manuscript.title,
                        "reviewer": {
                            "id": str(reviewer.id),
                            "name": f"{reviewer.first_name} {reviewer.last_name}",
                            "email": reviewer.email,
                            "web3_address": reviewer.web3_address,
                        },
                        "status": manuscript.status
                    }
                }
                # Return success response with reviewer details
                return Response(resp_data, status=status.HTTP_200_OK)

        except Journal.DoesNotExist:
            return Response(
                {"result": "error", "message": "Journal not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Manuscript.DoesNotExist:
            return Response(
                {"result": "error", "message": "Manuscript not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Profile.DoesNotExist:
            return Response(
                {"result": "error", "message": "Reviewer not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"result": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SubmitReview(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, manuscript_id, *args, **kwargs):
        try:
            with transaction.atomic():
                # Get the manuscript
                manuscript = get_object_or_404(Manuscript, id=manuscript_id)

                # Get the reviewer assignment
                reviewer_assignment = get_object_or_404(
                    ReviewerAssignment,
                    manuscript=manuscript,
                    reviewer=request.user,
                    status__in=[ReviewerAssignment.Status.PENDING, ReviewerAssignment.Status.ACCEPTED]
                )

                # Parse the review data
                try:
                    review_data = JSONParser().parse(request)
                except JSONDecodeError as e:
                    return Response(
                        {
                            "result": "error",
                            "message": f"Invalid JSON data: {str(e)}",
                            "location": "JSON parsing"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                comments = review_data.get('comments')
                verdict = review_data.get('verdict')

                if not comments or not verdict:
                    return Response(
                        {
                            "result": "error",
                            "message": "Missing required fields: comments and verdict",
                            "location": "Input validation"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Create metadata dictionary with explicit string conversion
                try:
                    metadata = {
                        'reviewer_id': str(request.user.id),
                        'reviewer_name': f"{request.user.first_name} {request.user.last_name}",
                        'comments': str(comments),
                        'recommendation': str(verdict)
                    }
                except Exception as e:
                    return Response(
                        {
                            "result": "error",
                            "message": f"Error creating metadata: {str(e)}",
                            "location": "Metadata creation"
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                # Record on blockchain
                try:
                    sepolia = Sepolia()
                    tx_receipt = sepolia.record_review(
                        manuscript_id=str(manuscript.id),
                        reviewer_id=str(request.user.id),
                        metadata=metadata
                    )
                except Exception as e:
                    return Response(
                        {
                            "result": "error",
                            "message": f"Blockchain recording failed: {str(e)}",
                            "location": "Blockchain interaction"
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                if isinstance(tx_receipt, dict) and 'error' in tx_receipt:
                    return Response(
                        {
                            "result": "error",
                            "message": tx_receipt['error'],
                            "location": "Transaction receipt"
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                try:
                    txn_hash = tx_receipt.transactionHash.hex()
                    if not txn_hash.startswith('0x'):
                        txn_hash = '0x' + txn_hash
                except Exception as e:
                    return Response(
                        {
                            "result": "error",
                            "message": f"Error processing transaction hash: {str(e)}",
                            "location": "Transaction hash processing"
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                # Record the review event
                try:
                    manuscript.record_review(
                        reviewer=request.user,
                        comments=comments,
                        verdict=verdict,
                        actor=request.user,
                        txn_hash=txn_hash
                    )
                except Exception as e:
                    return Response(
                        {
                            "result": "error",
                            "message": f"Error recording review event: {str(e)}",
                            "location": "Event recording"
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                # Return success response
                return Response(
                    {
                        "result": "success",
                        "message": "Review submitted successfully",
                        "data": {
                            "manuscript_id": str(manuscript.id),
                            "manuscript_title": manuscript.title,
                            "reviewer_id": str(request.user.id),
                            "status": reviewer_assignment.status,
                            "verdict": verdict,
                            "transaction_hash": str(txn_hash)
                        }
                    },
                    status=status.HTTP_200_OK
                )

        except ReviewerAssignment.DoesNotExist:
            return Response(
                {
                    "result": "error",
                    "message": "You are not assigned to review this manuscript",
                    "location": "Reviewer assignment check"
                },
                status=status.HTTP_403_FORBIDDEN
            )
        except Manuscript.DoesNotExist:
            return Response(
                {
                    "result": "error", 
                    "message": "Manuscript not found",
                    "location": "Manuscript lookup"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    "result": "error",
                    "message": str(e),
                    "location": "Unknown error"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class SubmitCorrections(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, manuscript_id, *args, **kwargs):
        try:
            with transaction.atomic():
                # Get the manuscript
                manuscript = get_object_or_404(Manuscript, id=manuscript_id)

                # Parse the corrections data
                corrections_data = JSONParser().parse(request)
                changes_description = corrections_data.get('changes_description')

                if not changes_description:
                    return Response(
                        {
                            "result": "error",
                            "message": "Changes description is required"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Record on blockchain
                sepolia = Sepolia()
                metadata = {
                    'author_id': str(request.user.id),
                    'author_name': f"{request.user.first_name} {request.user.last_name}",
                    'changes_description': changes_description
                }
                tx_receipt = sepolia.record_corrections(
                    manuscript_id=manuscript.id,
                    author_id=request.user.id,
                    metadata=metadata
                )

                if isinstance(tx_receipt, dict) and 'error' in tx_receipt:
                    return Response(
                        {"result": "error", "message": tx_receipt['error']},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                txn_hash = tx_receipt.transactionHash.hex()
                if not txn_hash.startswith('0x'):
                    txn_hash = '0x' + txn_hash

                # Record the corrections event
                manuscript.record_corrections(
                    actor=request.user,
                    changes_description=changes_description,
                    txn_hash=txn_hash
                )

                # Return success response
                return Response(
                    {
                        "result": "success",
                        "message": "Corrections submitted successfully",
                        "data": {
                            "manuscript_id": manuscript.id,
                            "manuscript_title": manuscript.title,
                            "author_id": request.user.id,
                            "transaction_hash": txn_hash
                        }
                    },
                    status=status.HTTP_200_OK
                )

        except Manuscript.DoesNotExist:
            return Response(
                {"result": "error", "message": "Manuscript not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"result": "error", "message": str(e)})

class PublishManuscript(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, manuscript_id, *args, **kwargs):
        try:
            manuscript = Manuscript.objects.get(pk=manuscript_id)
        except Manuscript.DoesNotExist:
            return JsonResponse(
                {"result": "error", 'message': 'Manuscript does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        if manuscript.status != Manuscript.Status.REVIEW:
            return JsonResponse(
                {"result": "error", "message": "Only reviewed manuscripts can be published"},
                status=status.HTTP_400_BAD_REQUEST
            )

        sepolia = Sepolia()
        tx_receipt = sepolia.post_manuscript(manuscript.to_json())
        txn_hash = tx_receipt.transactionHash.hex()
        if not txn_hash.startswith('0x'):
            txn_hash = '0x' + txn_hash
        manuscript.publish(actor=request.user, txn_hash=txn_hash)

        return JsonResponse(
            {"result": "success", "message": "Manuscript published successfully"},
            status=status.HTTP_200_OK
        )

class AssignedReviews(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = Pagination

    def get(self, request, *args, **kwargs):
        # Get all reviewer assignments for the authenticated user
        assignments = ReviewerAssignment.objects.filter(
            reviewer=request.user,
            status__in=[
                ReviewerAssignment.Status.PENDING,
                ReviewerAssignment.Status.ACCEPTED
            ]
        ).select_related('manuscript', 'manuscript__journal_id', 'manuscript__submitted_by')

        # Initialize paginator
        paginator = self.pagination_class()
        paginated_assignments = paginator.paginate_queryset(assignments, request)

        # Prepare the response data
        manuscript_list = []
        for assignment in paginated_assignments:
            manuscript = assignment.manuscript
            manuscript_data = {
                'id': manuscript.pk,
                'title': manuscript.title,
                'abstract': manuscript.abstract,
                'journal': {
                    'id': manuscript.journal_id.id,
                    'name': manuscript.journal_id.name
                },
                'keywords': manuscript.keywords,
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
                'assignment': {
                    'id': assignment.id,
                    'status': assignment.status,
                    'assigned_date': assignment.assigned_date,
                    'due_date': assignment.due_date,
                    'completed_date': assignment.completed_date
                },
                'submitted': manuscript.submitted,
                'status': manuscript.status
            }
            manuscript_list.append(manuscript_data)

        return paginator.get_paginated_response(manuscript_list)
