from django.db import models

from accounts.models import Profile


class Journal(models.Model):
    title = models.CharField(max_length=250, blank=False, null=False)
    abbreviation = models.CharField(max_length=25, blank=False, null=False, unique=True)
    description = models.TextField(max_length=25, help_text="A short description shown on list pages")
    active = models.BooleanField(default=True)
    publisher = models.CharField(max_length=250, blank=False, null=False)
    online_issn = models.CharField(max_length=250, blank=True, unique=True)
    print_issn = models.CharField(max_length=250, blank=True, unique=True)
    about = models.TextField(max_length=250, blank=True, help_text="All about the journal displayed on journal page")
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Profile, on_delete=models.DO_NOTHING)


class Issue(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.DO_NOTHING)
    volume = models.CharField(max_length=15, blank=False, null=False)
    number = models.CharField(max_length=15, blank=False, null=False)
    year = models.CharField(max_length=15, blank=False, null=False)
    title = models.CharField(max_length=15, blank=False, null=False)
    description = models.TextField(max_length=15, blank=False, null=False)
    cover_image = models.ImageField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

