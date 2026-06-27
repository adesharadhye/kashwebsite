from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('api/profile/', views.profile_data, name='profile-data'),
    path('downloads/<str:document_type>/', views.download_document, name='download-document'),
    path('backend/upload/', views.upload_documents, name='upload-documents'),
]
