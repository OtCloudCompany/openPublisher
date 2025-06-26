import json

from django.db import models

from accounts.models import Profile


class Author(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    affiliation = models.CharField(max_length=50)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return self.last_name


class Manuscript(models.Model):
    title = models.CharField(max_length=250, )
    abstract = models.TextField(max_length=500)
    authors = models.ManyToManyField(to=Author, blank=True,)
    keywords = models.JSONField()  # list of strings
    tx_receipt = models.TextField(max_length=500, blank=True)
    submitted_by = models.ForeignKey(to=Profile, on_delete=models.DO_NOTHING)
    submitted = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


