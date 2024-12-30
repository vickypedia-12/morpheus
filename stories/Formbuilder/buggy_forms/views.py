from django.shortcuts import render, redirect, get_object_or_404
from .models import Form, Question, Response, Answer
from .forms import FormForm, QuestionForm, ResponseForm
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect, csrf_exempt, ensure_csrf_cookie
from django.core.exceptions import PermissionDenied
from .forms import UserRegisterForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Max
from django.db import transaction
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
from django.urls import reverse
from django.contrib.auth import authenticate, login


# Admin: Create a new form
@csrf_protect
def Base(request):
    """
    Renders the base template.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Rendered base HTML page.
    """
    return render(request, 'buggy_forms/base.html')

def register(request):
    """
    Handles user registration.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Redirects to login on successful registration or renders the registration form.
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def create_form(request):
    """
    Allows authenticated users to create a new form.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Redirects to add questions on successful form creation or renders the form creation page.
    """
    if request.method == 'POST':
        form = FormForm(request.POST)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.created_by = request.user 
            new_form.save()
            return redirect('add_question', form_id=new_form.id)
    else:
        form = FormForm()
    return render(request, 'buggy_forms/create_form.html', {'form': form})

# Admin: Add questions to a form
@login_required
def add_question(request, form_id):
    form_obj = get_object_or_404(Form, id=form_id)
    if form_obj.created_by != request.user:
        raise PermissionDenied  # Only form owner can add questions
    if form_obj.questions.count() >= 100:
        messages.error(request, "Maximum 100 questions allowed per form")
        return redirect('list_forms')
    if request.method == 'POST':
        q_form = QuestionForm(request.POST)
        if q_form.is_valid():
            question = q_form.save(commit=False)
            question.form = form_obj
            max_order = form_obj.questions.aggregate(Max('order'))['order__max'] or 0
            question.order = max_order + 1
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
    """
    Displays a list of forms based on user authentication and permissions.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Rendered HTML page with the list of forms.
    """
    if request.user.is_authenticated:
        if request.user.is_superuser:
            forms_list = Form.objects.all()
        else:
            forms_list = Form.objects.filter(created_by=request.user)
    else:
        forms_list = Form.objects.none()
        
    return render(request, 'buggy_forms/list_forms.html', {'forms': forms_list})


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
    total_responses = form.responses.count()
    question_analytics = []

    for question in form.questions.all():
        data = {}
        if question.question_type == Question.TEXT:
            # Count word occurrences (words with 5 or more characters)
            responses = Answer.objects.filter(question=question).values_list('text_answer', flat=True)
            word_counts = defaultdict(int)
            for response in responses:
                if response:
                    words = response.split()
                    for word in words:
                        if len(word) >= 5:
                            word_counts[word.lower()] += 1
            # Get top 5 words
            sorted_words = sorted(word_counts.items(), key=lambda item: item[1], reverse=True)
            top_words = sorted_words[:5]
            others_count = sum(count for _, count in sorted_words[5:])
            top_words.append(('Others', others_count))
            data = dict(top_words)

        elif question.question_type == Question.DROPDOWN:
            # Count each option selection
            choices = question.get_choices_list()
            selected_counts = {choice: 0 for choice in choices}
            responses = Answer.objects.filter(question=question).values_list('text_answer', flat=True)
            for choice in responses:
                if choice in selected_counts:
                    selected_counts[choice] += 1
            # Get top 5 options
            sorted_options = sorted(selected_counts.items(), key=lambda item: item[1], reverse=True)
            top_options = sorted_options[:5]
            others_count = sum(count for _, count in sorted_options[5:])
            top_options.append(('Others', others_count))
            data = dict(top_options)

        elif question.question_type == Question.CHECKBOX:
            # Count each selection
            choices = question.get_choices_list()
            combo_counts = defaultdict(int)
            responses = Answer.objects.filter(question=question).values_list('selected_options', flat=True)
            for response_choices in responses:
                if response_choices:
                    for choice in response_choices:
                        choice = choice.strip()
                        if choice in choices:
                            combo_counts[choice] += 1
            # Get top 5 selections
            sorted_combos = sorted(combo_counts.items(), key=lambda item: item[1], reverse=True)
            top_combos = sorted_combos[:5]
            others_count = sum(count for _, count in sorted_combos[5:])
            top_combos.append(('Others', others_count))
            data = dict(top_combos)

        question_analytics.append({
            'question': question,
            'data': data
        })

    context = {
        'form': form,
        'total_responses': total_responses,
        'question_analytics': question_analytics
    }

    return render(request, 'buggy_forms/analytics.html', context)

@require_POST
@login_required
def reorder_questions(request, form_id):
    form = get_object_or_404(Form, id=form_id)
    if form.created_by != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        question_ids = request.POST.getlist('questions[]')
        with transaction.atomic():
            for index, question_id in enumerate(question_ids):
                Question.objects.filter(
                    id=question_id, 
                    form=form
                ).update(order=index)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def edit_form(request, form_id):
    form_obj = get_object_or_404(Form, id=form_id)
    if form_obj.created_by != request.user:
        raise PermissionDenied
        
    if request.method == 'POST':
        form = FormForm(request.POST, instance=form_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Form updated successfully.')
            return redirect('list_forms')
    else:
        form = FormForm(instance=form_obj)
    
    questions = form_obj.questions.all().order_by('order')
    return render(request, 'buggy_forms/list_form_edit.html', {
        'form': form,
        'form_id': form_id,
        'questions': questions,
        'form_obj': form_obj
    })

@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if question.form.created_by != request.user:
        raise PermissionDenied
    
    form_id = question.form.id
    question.delete()
    messages.success(request, 'Question deleted successfully.')
    return redirect('edit_form', form_id=form_id)
# Admin: Edit an existing question
@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if question.form.created_by != request.user:
        raise PermissionDenied  # Only form owner can edit questions
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

@login_required
def generate_form_qr(request, form_id):
    form = get_object_or_404(Form, id=form_id)
    if form.created_by != request.user:
        raise PermissionDenied
    
    # Generate submission URL
    submit_url = request.build_absolute_uri(reverse('submit_response', args=[form_id]))
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(submit_url)
    qr.make(fit=True)
    
    # Create QR code image
    img_buffer = BytesIO()
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(img_buffer, format='PNG')
    qr_image = base64.b64encode(img_buffer.getvalue()).decode()
    
    return JsonResponse({
        'qr_code': qr_image,
        'submit_url': submit_url
    })

def custom_404(request, exception):
    return render(request, 'buggy_forms/404.html', status=404)

def custom_500(request):
    return render(request, 'buggy_forms/500.html', status=500)

@ensure_csrf_cookie
@csrf_protect
@login_required
def delete_form(request, form_id):
    form = get_object_or_404(Form, id=form_id)
    if form.created_by != request.user:
        raise PermissionDenied
    
    if request.method == 'POST':
        form.delete()
        messages.success(request, 'Form deleted successfully.')
        return redirect('list_forms')
    return redirect('edit_form', form_id=form_id)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            print("Usser found")
            messages.success(request, f'Welcome back, {username}!')
            return redirect('list_forms')
        else:
            messages.error(request, 'Invalid email or password. Please try again.')
            return render(request, 'registration/login.html')
    
    return render(request, 'registration/login.html')