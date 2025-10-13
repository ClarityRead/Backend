from rest_framework import generics, filters
from .models import Paper
from .serializers import PaperListSerializer, PaperDetailSerializer

class PaperListView(generics.ListAPIView):
    queryset = Paper.objects.all()
    serializer_class = PaperListSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'summary']  
    ordering_fields = ['published', 'title']  

    def get_queryset(self):
        qs = super().get_queryset()
        domain = self.request.query_params.get('domain')
        subdomain = self.request.query_params.get('subdomain')
        if domain:
            qs = qs.filter(domain=domain)
        if subdomain:
            qs = qs.filter(subdomain=subdomain)
        return qs

class PaperDetailView(generics.RetrieveAPIView):
    queryset = Paper.objects.all()
    serializer_class = PaperDetailSerializer
    lookup_field = 'paper_id'