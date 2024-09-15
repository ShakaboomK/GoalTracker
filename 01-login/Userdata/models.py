from django.db import models
from django.utils import timezone

class Goal(models.Model):
    user = models.CharField(max_length=255) 
    title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.title

class Step(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='steps')
    name = models.CharField(max_length=255)
    weightage = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class SubTask(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name='subtasks')
    name = models.CharField(max_length=255)
    weightage = models.PositiveIntegerField()

    def __str__(self):
        return self.name
    
class Progress(models.Model):
    user = models.CharField(max_length=255)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    step = models.ForeignKey(Step, on_delete=models.CASCADE, null=True, blank=True)
    subtask = models.ForeignKey(SubTask, on_delete=models.CASCADE, null=True, blank=True)
    completed = models.BooleanField(default=False)
    completed_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f'Progress for {self.user}'
    
