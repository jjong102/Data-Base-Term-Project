from django.urls import path

from . import views

urlpatterns = [
    path("", views.festival_list, name="festival_list"),
    path("festival/<int:pk>/", views.festival_detail, name="festival_detail"),
    path("festival/new/", views.festival_create, name="festival_create"),
    path("festival/<int:pk>/edit/", views.festival_update, name="festival_update"),
    path("festival/<int:pk>/delete/", views.festival_delete, name="festival_delete"),
]
