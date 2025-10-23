"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from project.views import PaperListView, PaperDetailView, PaperSearchView, PaperSummaryView, ExplainTermView, SignUpView, LogInView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/papers/', PaperListView.as_view(), name='papers-list'),
    path('api/papers/search/', PaperSearchView.as_view(), name='papers-search'),
    path('api/papers/summary', PaperSummaryView.as_view(), name="paper-summary"),
    path('api/papers/term', ExplainTermView.as_view(), name="papers-term"),
    path('api/papers/<str:paper_id>/', PaperDetailView.as_view(), name='paper-detail'),
    path('api/auth/signup', SignUpView.as_view(), name="signup"),
    path('api/auth/login', LogInView.as_view(), name="login"),
]