from django.urls import path
from apps.reports.adapters.web.views import GenerateReportView, DownloadReportView


app_name = 'reports'

urlpatterns = [
    path('generate/', GenerateReportView.as_view(), name='generate'),
    path('download/', DownloadReportView.as_view(), name='download'),
]