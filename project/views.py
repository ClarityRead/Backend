from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PaperSerializer
from .models import get_papers_collection
import logging

logger = logging.getLogger(__name__)

class PaperListView(APIView):
    def get(self, request):
        try:
            print("Getting papers")
            papers = get_papers_collection()
            if papers is None:
                return Response(
                    {"error": "Database connection failed. Please check MongoDB connection."}, 
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            data = list(papers.find({}, {"_id": 0}))  
            if not data:
                return Response([])
            serializer = PaperSerializer(data, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching papers: {str(e)}")
            return Response(
                {"error": "Database connection failed. Please check MongoDB connection."}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

class PaperDetailView(APIView):
    def get(self, request, paper_id):
        try:
            papers = get_papers_collection()
            if papers is None:
                return Response(
                    {"error": "Database connection failed. Please check MongoDB connection."}, 
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            paper = papers.find_one({"paper_id": paper_id}, {"_id": 0})
            if not paper:
                return Response({"error": "Paper not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = PaperSerializer(paper)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching paper {paper_id}: {str(e)}")
            return Response(
                {"error": "Database connection failed. Please check MongoDB connection."}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )