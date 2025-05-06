from django.urls import path
from . import views

urlpatterns = [
    path('', views.gallery_list, name='gallery_list'),
    path('upload/', views.gallery_upload, name='gallery_upload'),
    path('<int:media_id>/', views.media_detail, name='media_detail'),
    path('<int:media_id>/delete/', views.media_delete, name='media_delete'),
    path('wedding/<int:wedding_id>/', views.wedding_gallery, name='wedding_gallery'),
]
