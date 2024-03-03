from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()


urlpatterns = [
    path('', home, name='home'),
    path('api/facilities',FacilityFilterOptions.as_view(),name='filterOptions'),
    path('api/upload-data/', UploadData.as_view(), name='upload-data'),
    path('data/', data_index, name='data_index'),
    path('api/run-analytics',RunIndicatorAnalytics.as_view(),name='run_analytics'),
    path('api/bpcontrol-analytics',BPControlAnalytics.as_view(),name='bpcontrol_analytics'),
    path('api/analytics-overview',AnalyticsOverview.as_view(),name='bpcontrol_analytics'),
]