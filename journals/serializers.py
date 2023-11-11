from rest_framework import serializers
from journals.models import Journal


class JournalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Journal
        fields = "__all__"

        # exclude = ("id", "title", "about", "description", "publisher", "online_issn", "print_issn", "created_by",
        #            "created")
