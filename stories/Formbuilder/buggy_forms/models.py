from django.db import models

class Form(models.Model):
    title = models.CharField(max_length=200)

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
        return f"{self.form.title} - {self.text}"

    def get_choices_list(self):
        if self.choices:
            return [(choice.strip(), choice.strip()) for choice in self.choices.split(',')]
        return []
    
    

class Response(models.Model):
    form = models.ForeignKey(Form, related_name='responses', on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

class Answer(models.Model):
    response = models.ForeignKey(Response, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text_answer = models.TextField(blank=True, null=True)
    selected_options = models.JSONField(blank=True, null=True)
