from django.contrib import admin
from .models import Exchange, Reservation

admin.site.register(Reservation)


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ("offered", "requested", "requester", "status", "created_at")
    list_filter = ("status",)
