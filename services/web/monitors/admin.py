from django.contrib import admin
from .models import Server, Service, StatusLog


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip_address', 'status', 'is_active', 'updated_at']
    list_filter = ['status', 'is_active']
    search_fields = ['name', 'ip_address']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'server', 'port', 'status', 'updated_at']
    list_filter = ['status']
    search_fields = ['name', 'server__name']


@admin.register(StatusLog)
class StatusLogAdmin(admin.ModelAdmin):
    list_display = ['server', 'service', 'previous_status', 'new_status', 'changed_at']
    list_filter = ['new_status']