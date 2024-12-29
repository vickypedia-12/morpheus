from django.db import models
from django.contrib.auth.models import User

class Form(models.Model):
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, related_name='forms', null=True, default=None, blank=True , on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Question(models.Model):
    TEXT = 'text'
    DROPDOWN = 'dropdown'
    CHECKBOX = 'checkbox'
    QUESTION_TYPES = [
        (TEXT, 'Text'),
        (DROPDOWN, 'Dropdown'),
        (CHECKBOX, 'Checkbox'),
    ]
    form = models.ForeignKey(Form, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=200, help_text="Enter the Question")
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    choices = models.TextField(
        blank = True,
        null = True,
        help_text="Enter the choices for the Dropdown or CheckBox separated by Comma"
    )

    def __str__(self):
        return f"{self.text}"

    def get_choices_list(self):
        return [choice.strip() for choice in self.choices.split(',')] if self.choices else []

    
    

class Response(models.Model):
    form = models.ForeignKey(Form, related_name='responses', on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

class Answer(models.Model):
    response = models.ForeignKey(Response, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text_answer = models.TextField(max_length=500, blank=True, null=True)
    selected_options = models.JSONField(max_length=500,blank=True, null=True)

    def __str__(self):
        return f'Answer to {self.question.text}'