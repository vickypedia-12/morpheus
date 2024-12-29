from django.shortcuts import render, redirect, get_object_or_404
from .models import Form, Question, Response, Answer
from .forms import FormForm, QuestionForm, ResponseForm
from collections import defaultdict
# Admin: Create a new form
def Base(request):
    return render(request, 'buggy_forms/base.html')

def create_form(request):
    if request.method == 'POST':
        form = FormForm(request.POST)
        if form.is_valid():
            new_form = form.save()
            return redirect('add_question', form_id=new_form.id)
    else:
        form = FormForm()
    return render(request, 'buggy_forms/create_form.html', {'form': form})

# Admin: Add questions to a form
def add_question(request, form_id):
    form_obj = get_object_or_404(Form, id=form_id)
    if request.method == 'POST':
        q_form = QuestionForm(request.POST)
        if q_form.is_valid():
            question = q_form.save(commit=False)
            question.form = form_obj
            question.save()
            return redirect('add_question', form_id=form_id)
    else:
        q_form = QuestionForm()
    
    # Fetch existing questions for the form
    questions = form_obj.questions.all()
    return render(request, 'buggy_forms/add_question.html', {
        'form_obj': form_obj,
        'q_form': q_form,
        'questions': questions
    })

# Admin: List all forms
def list_forms(request):
    forms_list = Form.objects.all()
    return render(request, 'buggy_forms/list_forms.html', {'forms': forms_list})

# User: Submit responses to a form
def submit_response(request, form_id):
    form_obj = get_object_or_404(Form, id=form_id)
    if request.method == 'POST':
        r_form = ResponseForm(request.POST, form_obj=form_obj)
        if r_form.is_valid():
            # Create a new response
            response = Response.objects.create(form=form_obj)
            # Process each question's answer
            for question in form_obj.questions.all():
                field_name = f'question_{question.pk}'
                answer_data = r_form.cleaned_data.get(field_name)

                if question.question_type == Question.TEXT:
                    Answer.objects.create(
                        response=response,
                        question=question,
                        text_answer=answer_data
                    )
                elif question.question_type == Question.DROPDOWN:
                    Answer.objects.create(
                        response=response,
                        question=question,
                        text_answer=answer_data
                    )
                elif question.question_type == Question.CHECKBOX:
                    Answer.objects.create(
                        response=response,
                        question=question,
                        selected_options=answer_data
                    )
            return redirect('list_forms')
    else:
        r_form = ResponseForm(form_obj=form_obj)
    return render(request, 'buggy_forms/submit_response.html', {
        'form_obj': form_obj,
        'r_form': r_form
    })

# Shared: View analytics for a form
def view_analytics(request, form_id):
    form = get_object_or_404(Form, id=form_id)
    analytics = {
        'total_responses': form.responses.count(),
        'question_analytics': defaultdict(dict)
    }

    for question in form.questions.all():
        if question.question_type == Question.TEXT:
            # Example: Count word occurrences
            responses = form.responses.values_list('answers__text', flat=True)
            word_counts = defaultdict(int)
            for response in responses:
                words = response.split()
                for word in words:
                    word_counts[word.lower()] += 1
            analytics['question_analytics'][question.id] = word_counts

        elif question.question_type == Question.DROPDOWN:
            # Example: Count each option selection
            choices = question.get_choices_list()
            selected_counts = {choice: 0 for choice in choices}
            responses = form.responses.values_list('answers__choice', flat=True)
            for choice in responses:
                if choice in selected_counts:
                    selected_counts[choice] += 1
            analytics['question_analytics'][question.id] = selected_counts

        elif question.question_type == Question.CHECKBOX:
            # Example: Count each combination of selections
            choices = question.get_choices_list()
            combo_counts = defaultdict(int)
            responses = form.responses.values_list('answers__choices', flat=True)
            for response_choices in responses:
                for choice in response_choices.split(','):
                    choice = choice.strip()
                    if choice in choices:
                        combo_counts[choice] += 1
            analytics['question_analytics'][question.id] = combo_counts

    context = {
        'form': form,
        'analytics': analytics
    }

    return render(request, 'buggy_forms/analytics.html', context)

# Admin: Edit an existing question
def edit_form(request, form_id):
    form_obj = get_object_or_404(Form, id=form_id)
    if request.method == 'POST':
        form = FormForm(request.POST, instance=form_obj)
        if form.is_valid():
            form.save()
            return redirect('list_forms')
    else:
        form = FormForm(instance=form_obj)
    return render(request, 'buggy_forms/list_form_edit.html', {'form': form, 'form_id': form_id})

# Admin: Edit an existing question
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        q_form = QuestionForm(request.POST, instance=question)
        if q_form.is_valid():
            q_form.save()
            return redirect('add_question', form_id=question.form.id)
    else:
        q_form = QuestionForm(instance=question)
    return render(request, 'buggy_forms/add_questions_edit.html', {
        'q_form': q_form,
        'form_obj': question.form,
        'question': question
    })