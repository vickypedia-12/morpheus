from django import forms
from .models import Form, Question, Response, Answer
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegisterForm(UserCreationForm):
    """
    Form for registering a new user.

    Attributes:
        email (EmailField): The user's email address.
    """
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ['email','username',  'password1', 'password2']

class FormForm(forms.ModelForm):
    """
    Form for creating a new Form.

    Meta:
        model (Form): The associated model.
        fields (list): Fields to include in the form.
    """
    class Meta:
        model = Form
        fields = ['title']

class QuestionForm(forms.ModelForm):
    """
    Form for creating a new Question.

    Meta:
        model (Question): The associated model.
        fields (list): Fields to include in the form.
        widgets (dict): Widgets to use for specific fields.
    """
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'choices']
        widgets = {
            'choices': forms.TextInput(attrs={'placeholder': 'Enter choices separated by commas'}),
        }

    def clean(self):
        """
        Validates the form data.

        Ensures that choices are provided for Dropdown and Checkbox question types.

        Returns:
            dict: Cleaned data.
        """
        cleaned_data = super().clean()
        question_type = cleaned_data.get('question_type')
        choices = cleaned_data.get('choices')
        if question_type in [Question.DROPDOWN, Question.CHECKBOX] and not choices:
            self.add_error('choices', 'Choices are required for Dropdown and Checkbox questions.')
        return cleaned_data

class ResponseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        form_obj = kwargs.pop('form_obj')
        super().__init__(*args, **kwargs)
        for question in form_obj.questions.all():
            field_name = f'question_{question.pk}'
            if question.question_type == Question.TEXT:
                self.fields[field_name] = forms.CharField(
                    label=question.text,
                    required=False,
                    widget=forms.Textarea(attrs={'rows': 3, 'cols': 40})
                )
            elif question.question_type == Question.DROPDOWN:
                choices = question.get_choices_list()
                choices_with_empty = [('','Select')] + [(choice, choice) for choice in choices]
                self.fields[field_name] = forms.ChoiceField(
                    label=question.text,
                    choices=choices_with_empty,
                    required=False,
                    widget=forms.Select()
                )
            elif question.question_type == Question.CHECKBOX:
                choices = question.get_choices_list()
                self.fields[field_name] = forms.MultipleChoiceField(
                    label=question.text,
                    choices=[(choice, choice) for choice in choices],  # Ensure choices are tuples
                    required=False,
                    widget=forms.CheckboxSelectMultiple
                )