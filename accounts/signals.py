from django.db.models.signals import post_save
from django.dispatch import receiver
# from django.contrib.auth.models import User
from accounts.models import Profile
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=Profile, weak=False)
def report_new_profile(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user=instance)
