from django.contrib import admin

from .models import Comment, Festival


@admin.register(Festival)
class FestivalAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "organizer", "start_year", "pub_date")
    search_fields = ("title", "organizer", "category", "external_id")
    ordering = ("title",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("nickname", "festival", "created_at")
    search_fields = ("nickname", "content")
    ordering = ("-created_at",)
