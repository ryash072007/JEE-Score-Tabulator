from django import forms
from .models import JEEPdfUpload

class JEEPdfUploadForm(forms.ModelForm):
    class Meta:
        model = JEEPdfUpload
        fields = ['answer_key', 'student_response', 'pattern_q', 'pattern_a']
        widgets = {
            'pattern_q': forms.NumberInput(attrs={'class': 'form-control'}),
            'pattern_a': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'answer_key': 'Answer Key PDF',
            'student_response': 'Student Response PDF',
            'pattern_q': 'Question Pattern Adjustment',
            'pattern_a': 'Answer Pattern Adjustment',
        }