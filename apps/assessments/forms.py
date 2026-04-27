from django import forms
from .models import Assessment, Question


class AssessmentForm(forms.ModelForm):
    class Meta:
        model  = Assessment
        fields = ['title', 'description', 'course', 'assessment_type', 'total_marks', 'due_date']
        widgets = {
            'due_date':    forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model  = Question
        fields = ['question_text', 'model_answer', 'marks', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 2}),
            'model_answer':  forms.Textarea(attrs={'rows': 3}),
        }
