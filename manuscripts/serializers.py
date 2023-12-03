from rest_framework import serializers

from manuscripts.models import Manuscript


class CreateManuscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manuscript
        fields = "__all__"