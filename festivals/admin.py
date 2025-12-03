from django.contrib import admin

from .models import Comment, Festival


@admin.register(Festival)
class FestivalAdmin(admin.ModelAdmin):
    list_display = ("title", "place", "start_date", "organizer", "host", "data_reference_date")
    search_fields = ("title", "organizer", "host", "external_id")
    ordering = ("start_date", "title")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("nickname", "festival", "created_at")
    search_fields = ("nickname", "content")
    ordering = ("-created_at",)
