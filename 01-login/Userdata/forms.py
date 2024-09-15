from django import forms
from .models import Goal, Step, SubTask, Progress

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['title', 'start_date', 'end_date']

class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ['name', 'weightage']

class SubTaskForm(forms.ModelForm):
    class Meta:
        model = SubTask
        fields = ['name', 'weightage']

class ProgressForm(forms.ModelForm):
    class Meta:
        model = Progress
        fields = ['user', 'goal', 'step', 'subtask', 'completed']
        widgets = {
            'user': forms.HiddenInput(),
            'goal': forms.HiddenInput(),
            'step': forms.HiddenInput(),
            'subtask': forms.HiddenInput(),
            'completed': forms.HiddenInput(),
        }