from django import forms
from django.forms import inlineformset_factory
from .models import Assessment, Question, Submission


class AssessmentForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Assessment
        fields = ['title', 'description', 'course', 'assessment_type', 'total_marks', 'due_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the assessment requirements...'}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'reference_answer', 'marks', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter the question text...'}),
            'reference_answer': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter the reference answer for AI evaluation...'}),
            'marks': forms.NumberInput(attrs={'min': 1}),
            'order': forms.NumberInput(attrs={'min': 1}),
        }


QuestionFormSet = inlineformset_factory(
    Assessment,
    Question,
    form=QuestionForm,
    extra=3,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class StudentAnswerForm(forms.Form):
    question_id = forms.IntegerField(widget=forms.HiddenInput())
    question_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'readonly': 'readonly', 'class': 'question-text'}),
        label='Question',
    )
    answer_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your answer here...'}),
        required=False,
        label='Your answer',
    )
    answer_file = forms.FileField(required=False, label='Upload file')

    def clean(self):
        cleaned_data = super().clean()
        answer_text = cleaned_data.get('answer_text', '').strip()
        answer_file = cleaned_data.get('answer_file')
        if not answer_text and not answer_file:
            raise forms.ValidationError('Please provide an answer text or upload a file for each question.')
        return cleaned_data


class GradingForm(forms.Form):
    final_grade = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'A, B+, 95, etc.'}),
        label='Final grade',
    )
    lecturer_feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Provide your grading feedback...'}),
        label='Lecturer feedback',
    )
    status = forms.ChoiceField(
        choices=Submission.STATUS_CHOICES,
        label='Submission status',
    )
