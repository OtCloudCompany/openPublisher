import json

from django.core import serializers
from django.db import models
from accounts.models import Profile
from django.db import models
from django.contrib.auth import get_user_model

from journals.models import Journal

User = get_user_model()

class Author(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    affiliation = models.CharField(max_length=50)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return self.last_name


class Manuscript(models.Model):
    class Status(models.TextChoices):
        SUBMISSION = 'SUBMISSION', 'Submission'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'
        REVIEW = 'REVIEW', 'Review'
        COPYEDITING = 'COPYEDITING', 'Copyediting'
        PUBLISHED = 'PUBLISHED', 'Published'

    title = models.CharField(max_length=250, )
    abstract = models.TextField(max_length=500)
    authors = models.ManyToManyField(to=Author, blank=True,)
    keywords = models.JSONField()
    journal_id = models.ForeignKey(to=Journal, on_delete=models.DO_NOTHING)
    submitted_by = models.ForeignKey(to=Profile, on_delete=models.DO_NOTHING)
    submitted = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMISSION
    )

    def create_event(self, event_type, actor, txn_hash, description='', metadata=None,):
        """
        Create a new event for this manuscript
        """
        return ManuscriptEvent.objects.create(
            manuscript=self,
            event_type=event_type,
            actor=actor,
            txn_hash=txn_hash,
            description=description,
            metadata=metadata or {}
        )

    def record_submission(self, actor, txn_hash):
        """Record initial submission"""
        self.status = self.Status.SUBMISSION
        self.save()
        return self.create_event(
            ManuscriptEvent.EventType.SUBMISSION,
            actor=actor,
            txn_hash=txn_hash,
        )

    def record_acceptance(self, actor, txn_hash, comment=''):
        """Record manuscript acceptance"""
        self.status = self.Status.ACCEPTED
        self.save()
        return self.create_event(
            ManuscriptEvent.EventType.ACCEPTANCE,
            actor=actor,
            txn_hash=txn_hash,
            description=comment
        )

    def record_rejection(self, actor, txn_hash, reason=''):
        """Record manuscript rejection"""
        self.status = self.Status.REJECTED
        self.save()
        return self.create_event(
            ManuscriptEvent.EventType.REJECTION,
            actor=actor,
            txn_hash=txn_hash,
            description=reason
        )

    def assign_reviewer(self, reviewer, txn_hash, actor):
        """Record reviewer assignment"""
        metadata = {'reviewer_id': reviewer.id}
        self.status = self.Status.REVIEW
        self.save()
        return self.create_event(
            ManuscriptEvent.EventType.REVIEWER_ASSIGNED,
            actor=actor,
            txn_hash=txn_hash,
            metadata=metadata
        )

    def record_review(self, reviewer, comments, actor, txn_hash):
        """Record review submission"""
        metadata = {
            'reviewer_id': reviewer.id,
            'comments': comments
        }
        return self.create_event(
            ManuscriptEvent.EventType.REVIEW_SUBMITTED,
            actor=actor,
            txn_hash=txn_hash,
            metadata=metadata
        )

    def record_corrections(self, actor, changes_description, txn_hash):
        """Record author corrections"""
        return self.create_event(
            ManuscriptEvent.EventType.CORRECTIONS_SUBMITTED,
            actor=actor,
            txn_hash=txn_hash,
            description=changes_description
        )

    def publish(self, actor, txn_hash):
        """Record manuscript publication"""
        self.status = self.Status.PUBLISHED
        self.save()
        return self.create_event(
            ManuscriptEvent.EventType.PUBLISHED,
            actor=actor,
            txn_hash=txn_hash,
        )

    def get_provenance(self):
        """Get all events for this manuscript in chronological order"""
        return self.events.all()

    def to_json(self):
        return serializers.serialize('json', [self])

    def __str__(self):
        return self.title


class ManuscriptEvent(models.Model):
    class EventType(models.TextChoices):
        SUBMISSION = 'SUBMISSION', 'Manuscript Submitted'
        ACCEPTANCE = 'ACCEPTANCE', 'Manuscript Accepted'
        REJECTION = 'REJECTION', 'Manuscript Rejected'
        REVIEWER_ASSIGNED = 'REVIEWER_ASSIGNED', 'Reviewer Assigned'
        REVIEW_SUBMITTED = 'REVIEW_SUBMITTED', 'Review Submitted'
        CORRECTIONS_SUBMITTED = 'CORRECTIONS_SUBMITTED', 'Corrections Submitted'
        PUBLISHED = 'PUBLISHED', 'Manuscript Published'

    manuscript = models.ForeignKey(
        'Manuscript',
        on_delete=models.CASCADE,
        related_name='events'
    )
    event_type = models.CharField(
        max_length=50,
        choices=EventType.choices
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="User who triggered this event"
    )
    description = models.TextField(
        blank=True,
        help_text="Additional details about the event"
    )
    txn_hash = models.TextField(
        blank=True,
        help_text="Additional details about the event"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional structured data specific to the event type"
    )

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['manuscript', '-timestamp']),
            models.Index(fields=['event_type']),
        ]

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.manuscript.title} ({self.timestamp})"