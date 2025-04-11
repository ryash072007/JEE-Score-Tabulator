from django.db import models

class JEEPdfUpload(models.Model):
    """Model for storing uploaded JEE PDFs"""
    answer_key = models.FileField(upload_to='answer_keys/')
    student_response = models.FileField(upload_to='student_responses/')
    pattern_q = models.IntegerField(default=0, help_text="Question pattern adjustment")
    pattern_a = models.IntegerField(default=0, help_text="Answer pattern adjustment")
    upload_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"JEE Upload {self.id} - {self.upload_date.strftime('%Y-%m-%d %H:%M')}"
