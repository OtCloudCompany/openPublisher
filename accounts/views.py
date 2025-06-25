from json import JSONDecodeError
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework import status
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import Profile
from accounts.serializers import CreateProfileSerializer, LoginSerializer, ProfileSerializer, ProfileDetailsSerializer


class ListProfiles(APIView):
    """
    API endpoint for listing profiles.
    """

    model = Profile
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        profiles = self.model.objects.all()
        serializer = ProfileSerializer(instance=profiles, many=True)

        return Response(data=serializer.data)


class CreateProfile(APIView):
    """
    API endpoint for creating a profile.
    """

    model = Profile
    serializer_class = CreateProfileSerializer
    web3 = settings.W3

    def post(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=settings.DEBUG):
                instance = serializer.save()
                if self.web3.is_connected():
                    web3_account = self.web3.eth.account.create()
                    instance.web3_address = web3_account.address
                    instance.save()
                    web3_key = self.web3.to_hex(web3_account.key)
                    data['web3_address'] = instance.web3_address
                    data['web3_key'] = web3_key
                return Response(data=data, status=status.HTTP_201_CREATED)
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


class UpdateProfile(APIView):
    """ API endpoint for updating a profile."""
    model = Profile

    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):

        try:
            data = JSONParser().parse(request)
        except JSONDecodeError:
            return JsonResponse(
                {"result": "error", "message": "JSON decoding error"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            profile = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({"result": "error", 'message': 'Profile does not exist'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(instance=profile, data=data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateAddress(APIView):
    """ API endpoint for creating web3 address."""
    model = Profile
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    web3 = settings.W3
    serializer_class = ProfileDetailsSerializer

    def put(self, request, pk):

        try:
            profile = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({"result": "error", 'message': 'Profile does not exist'}, status=status.HTTP_404_NOT_FOUND)

        if self.web3.is_connected():
            web3_account = self.web3.eth.account.create()
            profile.web3_address = web3_account.address
            profile.save()
            serializer = ProfileSerializer(profile)
            data = serializer.data
            data['web3_key'] = self.web3.to_hex(web3_account.key)
            # data = JSONParser().parse(profile)
            # data['web3_key'] = self.web3.to_hex(web3_account.key)

            return Response(data=data, status=status.HTTP_201_CREATED)
        return Response(
            {"result": "error", 'message': 'An error occurred, no connection to web3 established.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class DeleteProfile(APIView):
    """Delete a profile"""

    model = Profile

    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):

        try:
            profile = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Profile does not exist'}, status=status.HTTP_404_NOT_FOUND)

        profile.delete()

        return JsonResponse({"result": "success", "message": "Profile deleted"})


class ProfileDetails(APIView):
    """Single profile details"""

    model = Profile
    serializer_class = ProfileDetailsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):

        try:
            profile = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Profile does not exist'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(instance=profile)

        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)


class Login(APIView):
    """Login"""

    model = Profile
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):

        try:
            data = JSONParser().parse(request)
        except JSONDecodeError:
            return Response(
                {"result": "error", 'message': 'JSON decode error'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        profile = authenticate(
            request,
            email=data.get('email'),
            password=data.get('password')
        )

        if profile:

            try:
                token = Token.objects.get(user=profile)
                user_permissions = profile.get_user_permissions()
            except Token.DoesNotExist:
                return Response(
                    {"result": "error", 'message': 'No token found for user'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            return Response(
                data={
                    'access_token': token.key,
                    'id': profile.pk,
                    'first_name': profile.first_name,
                    'last_name': profile.last_name,
                    'email': profile.email,
                    'permissions': user_permissions
                },
                status=status.HTTP_200_OK)
        else:
            return Response(
                data={"result": "error", 'message': 'Login failed'},
                status=status.HTTP_401_UNAUTHORIZED
            )
