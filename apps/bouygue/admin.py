from django.contrib import admin

from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at", "expires_at")
    readonly_fields = ("created_at",)
    filter_horizontal = ("read_by",)
