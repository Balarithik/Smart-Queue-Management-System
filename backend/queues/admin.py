from django.contrib import admin

from queues.models import Queue, QueueEntry


class QueueEntryInline(admin.TabularInline):
    model = QueueEntry
    extra = 0
    readonly_fields = ("token", "status", "joined_at")


@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "organization", "public_id", "is_active", "last_token_issued", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "organization__slug", "public_id")
    inlines = [QueueEntryInline]


@admin.register(QueueEntry)
class QueueEntryAdmin(admin.ModelAdmin):
    list_display = ("token", "queue", "status", "joined_at")
    list_filter = ("status",)
    search_fields = ("token", "queue__slug")
