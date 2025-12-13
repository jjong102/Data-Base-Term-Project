from django.contrib import admin

from .models import Comment, Festival, FestivalOrganization, Location, Organization


class FestivalOrganizationInline(admin.TabularInline):
    model = FestivalOrganization
    extra = 0


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "address_road", "address_lot", "latitude", "longitude")
    search_fields = ("name", "address_road", "address_lot")


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "telephone", "homepage")
    search_fields = ("name",)


@admin.register(Festival)
class FestivalAdmin(admin.ModelAdmin):
    list_display = ("title", "place", "start_date", "organizer", "host", "data_reference_date")
    search_fields = ("title", "organizations__organization__name", "external_id")
    ordering = ("start_date", "title")
    inlines = [FestivalOrganizationInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("nickname", "festival", "created_at")
    search_fields = ("nickname", "content")
    ordering = ("-created_at",)
