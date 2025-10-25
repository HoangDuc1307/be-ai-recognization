from django.urls import path
from . import views

urlpatterns = [
    path('recognize/', views.recognize_faces, name='recognize_faces'),
]
