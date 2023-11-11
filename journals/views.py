from json import JSONDecodeError

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status, permissions, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from journals.models import Journal
from journals.serializers import JournalSerializer


class CreateJournal(APIView):
    """Create a new Journal"""

    model = Journal
    serializer_class = JournalSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):

        try:
            data = JSONParser().parse(request)
            data.update({"created_by": self.request.user.pk})
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                journal = serializer.save()
                serialized_journal = self.serializer_class(instance=journal)

                return Response(data=serialized_journal.data, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse(
                    data=serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
        except JSONDecodeError:
            return JsonResponse(
                {"result": "error", "message": "JSON decoding error"},
                status=status.HTTP_400_BAD_REQUEST
            )


class UpdateJournal(APIView):

    """ API endpoint for updating a journal."""
    model = Journal
    serializer_class = JournalSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def put(self, request, pk):

        try:
            data = JSONParser().parse(request)
        except JSONDecodeError:
            return JsonResponse(
                {"result": "error", "message": "JSON decoding error"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            journal = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response(
                {"result": "error", 'message': 'Journal does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(instance=journal, data=data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteJournal(APIView):
    """Delete a journal"""

    model = Journal
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, pk):
        try:
            journal = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response(
                {'error': 'Journal does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        journal.delete()

        return JsonResponse({"result": "success", "message": "Journal deleted"})


class JournalDetails(APIView):
    """API endpoint for single journal details"""

    model = Journal
    serializer_class = JournalSerializer

    def get(self, request, pk):
        try:
            journal = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response(
                {'error': 'Journal does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(instance=journal)

        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)

class ListJournals(APIView):
    """
    API endpoint for listing all journals.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = []
    model = Journal
    serializer_class = JournalSerializer

    def get(self, request):
        journals = self.model.objects.all()
        serializer = JournalSerializer(instance=journals, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

