from accounts.models import Profile
from rest_framework import serializers


class LoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['email', 'password']


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'other_name', 'email', 'primary_phone', 'national_id',
                  'secondary_phone', 'additional_email', 'address', 'additional_address', ]
