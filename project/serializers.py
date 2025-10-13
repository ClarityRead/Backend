from rest_framework import serializers

class PaperSerializer(serializers.Serializer):
    paper_id = serializers.CharField()
    title = serializers.CharField()
    summary = serializers.CharField()
    author = serializers.CharField(required=False)
    published = serializers.CharField(required=False)
    pdf_link = serializers.CharField(required=False)
    reference_link = serializers.CharField(required=False)
    domain = serializers.CharField(required=False)
    subdomain = serializers.CharField(required=False)