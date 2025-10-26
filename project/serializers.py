from rest_framework import serializers

class PaperSerializer(serializers.Serializer):
    paper_id = serializers.CharField()
    title = serializers.CharField()
    summary = serializers.CharField()
    author = serializers.CharField()
    published = serializers.CharField()
    pdf_link = serializers.CharField()
    reference_link = serializers.CharField()
    domain = serializers.CharField()
    subdomain = serializers.CharField()