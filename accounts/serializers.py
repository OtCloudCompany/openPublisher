from accounts.models import Profile
from rest_framework import serializers


class ProfileSerializer:
    web3_key = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'other_name', 'email', 'primary_phone', 'national_id',
                  'secondary_phone', 'additional_email', 'address', 'additional_address', 'web3_address', 'web3_key']


class CreateProfileSerializer(serializers.ModelSerializer):

    password_repeat = serializers.CharField(write_only=True, required=True)

    def save(self):
        profile = Profile(
            email=self.validated_data['email'],
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            other_name=self.validated_data['other_name'],
            primary_phone=self.validated_data['primary_phone'],
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password_repeat']
        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        profile.set_password(password)
        profile.save()
        return profile

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'other_name', 'email', 'primary_phone', 'national_id', 'web3_address',
                  'secondary_phone', 'additional_email', 'address', 'additional_address', 'password', 'password_repeat']


class ProfileDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'other_name', 'email', 'primary_phone', 'national_id', 'web3_address',
                  'secondary_phone', 'additional_email', 'address', 'additional_address']


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['email', 'password']

