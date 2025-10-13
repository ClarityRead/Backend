from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PaperSerializer
from .models import papers 

class PaperListView(APIView):
    def get(self, request):
        data = list(papers.find({}, {"_id": 0}))  
        serializer = PaperSerializer(data, many=True)

        return Response(serializer.data)

class PaperDetailView(APIView):
    def get(self, request, paper_id):
        paper = papers.find_one({"paper_id": paper_id}, {"_id": 0})
        if not paper:
            return Response({"error": "Paper not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = PaperSerializer(paper)

        return Response(serializer.data)