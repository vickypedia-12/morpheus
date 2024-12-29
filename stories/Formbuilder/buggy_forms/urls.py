from django.urls import path
from .views import create_form, register, add_question, list_forms, submit_response, view_analytics, Base, edit_form, edit_question

urlpatterns = [
    path('', Base , name='base'),
    path('list/', list_forms, name='list_forms'),
    path('create/', create_form, name='create_form'),
    path('add_question/<int:form_id>/', add_question, name='add_question'),
    path('submit/<int:form_id>/', submit_response, name='submit_response'),
    path('analytics/<int:form_id>/', view_analytics, name='view_analytics'),
    path('edit_form/<int:form_id>/', edit_form, name='edit_form'),
    path('edit_question/<int:question_id>/', edit_question, name='edit_question'),
    path('register/', register, name='register'),
]