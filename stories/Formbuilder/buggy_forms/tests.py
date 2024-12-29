from django.test import TestCase
from django.urls import reverse
from .models import Form, Question, Response, Answer
from .forms import FormForm, QuestionForm, ResponseForm

class FormBuilderTestCase(TestCase):
    def setUp(self):
        self.form = Form.objects.create(title="Sample Form")
        self.question = Question.objects.create(
            form=self.form,
            text="Sample Question?",
            question_type=Question.TEXT
        )

    def test_form_creation(self):
        form_instance = Form.objects.create(title="Another Form")
        self.assertEqual(Form.objects.count(), 2)
        self.assertEqual(form_instance.title, "Another Form")

    def test_question_creation(self):
        self.assertEqual(self.form.questions.count(), 1)
        self.assertEqual(self.question.text, "Sample Question?")

    def test_response_submission(self):
        response_obj = Response.objects.create(form=self.form)
        Answer.objects.create(
            response=response_obj, 
            question=self.question, 
            text_answer="Sample Answer"
        )
        self.assertEqual(response_obj.answers.count(), 1)
        self.assertEqual(response_obj.answers.first().text_answer, "Sample Answer")

    def test_form_form(self):
        form_data = {"title": "Test Form"}
        form_form = FormForm(data=form_data)
        self.assertTrue(form_form.is_valid())

    def test_question_form(self):
        q_data = {
            "text": "New Question",
            "question_type": Question.CHECKBOX
        }
        q_form = QuestionForm(data=q_data)
        self.assertTrue(q_form.is_valid())

    def test_response_form(self):
        # Creating a ResponseForm should succeed if no conflicting data is passed
        r_form = ResponseForm(form_obj=self.form)
        self.assertIn(f"question_{self.question.pk}", r_form.fields)