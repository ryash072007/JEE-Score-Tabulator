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

class JEEScores(models.Model):
    """Model for storing JEE calculation results"""
    name = models.CharField(max_length=100, blank=True)
    total_score = models.FloatField(default=0.0)
    correct_answers = models.IntegerField(default=0)
    incorrect_answers = models.IntegerField(default=0)
    unattempted_questions = models.IntegerField(default=0)

    math_score = models.IntegerField(default=0)
    physics_score = models.IntegerField(default=0)
    chemistry_score = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Calculation for {self.jee_pdf} - Total Score: {self.total_score}"