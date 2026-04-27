from django import forms
from .models import Assignment, Question


class AssignmentForm(forms.ModelForm):
    class Meta:
        model  = Assignment
        fields = ['title', 'description', 'course', 'due_date']
        widgets = {
            'due_date':    forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model  = Question
        fields = ['text', 'model_answer', 'max_score', 'order']
        widgets = {
            'text':         forms.Textarea(attrs={'rows': 2}),
            'model_answer': forms.Textarea(attrs={'rows': 3}),
        }
