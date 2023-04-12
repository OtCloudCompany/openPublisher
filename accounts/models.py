from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from django.utils.translation import gettext_lazy as _
import uuid


class Profile(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, serialize=False)
    last_name = models.CharField(max_length=250, blank=False, null=False)
    first_name = models.CharField(max_length=250, blank=False, null=False)
    other_name = models.CharField(max_length=250, null=True)
    description = models.CharField(max_length=500, blank=True)
    primary_phone = models.CharField(max_length=15, blank=True)
    secondary_phone = models.CharField(max_length=15, blank=True)
    national_id = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=50, blank=False, unique=True)
    additional_email = models.EmailField(max_length=50, blank=True)
    address = models.TextField(max_length=50, blank=True)
    additional_address = models.TextField(max_length=50, blank=True)
    date_created = models.DateTimeField(auto_created=True, auto_now_add=True)
    email_verified = models.BooleanField(default=False)
    username = None

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'password']

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('accounts')
        permissions = (
            ('can_view_profile', _('Can view profiles')),
            ('can_change_profile', _('Can change profiles')),
            ('can_delete_profiles', _('Can delete profiles')),
        )

    def validate_email(self, email=''):
        member = Profile.objects.get(email=email)
        if member:
            raise ValidationError(
                _('%(email)s already exist'),
                params={'email': email},
            )

    def get_short_name(self):
        '''
        Returns the last name for the user.
        '''
        return self.last_name

    def __str__(self):
        return self.last_name
