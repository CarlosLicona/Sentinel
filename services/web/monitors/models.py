from django.db import models
class Server(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('unknown', 'Unknown'),
    ]

    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unknown')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.ip_address})"


class Service(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('unknown', 'Unknown'),
    ]

    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    port = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unknown')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} on {self.server.name}:{self.port}"


class StatusLog(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='logs', null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='logs', null=True, blank=True)
    previous_status = models.CharField(max_length=10)
    new_status = models.CharField(max_length=10)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.changed_at} - {self.previous_status} → {self.new_status}"
# Create your models here.
