from rest_framework import serializers
from .models import Paper

class PaperListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paper
        fields = ['paper_id', 'title', 'summary']

class PaperDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paper
        fields = [
            'paper_id',
            'title',
            'summary',
            'author',
            'published',
            'pdf_link',
            'reference_link',
            'domain',
            'subdomain',
        ]