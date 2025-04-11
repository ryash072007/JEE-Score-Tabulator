from django.contrib import admin
from .models import JEEPdfUpload

@admin.register(JEEPdfUpload)
class JEEPdfUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'upload_date', 'pattern_q', 'pattern_a')
    list_filter = ('upload_date',)
    search_fields = ('id',)
