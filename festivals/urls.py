from django.urls import path

from . import views

urlpatterns = [
    path("", views.festival_list, name="festival_list"),
    path("festival/<int:pk>/", views.festival_detail, name="festival_detail"),
]
