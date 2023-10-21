from django.contrib import admin

from .models import DocumentChunk
from .models import UploadedDocument


@admin.register(UploadedDocument)
class UploadedDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "title",
        "url",
        "doc_type",
        "created",
        "modified",
    )
    list_filter = ("created", "modified", "owner")


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "document",
        "content",
        "embedding",
        "created",
        "modified",
    )
    list_filter = ("created", "modified", "document")
