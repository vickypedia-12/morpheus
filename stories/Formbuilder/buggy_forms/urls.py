from django.urls import path
from .views import create_form, register, add_question, list_forms, submit_response, view_analytics, Base, edit_form, edit_question, reorder_questions, delete_question,generate_form_qr
from django.conf.urls import handler404, handler500

handler404 = 'buggy_forms.views.custom_404'
handler500 = 'buggy_forms.views.custom_500'

urlpatterns = [
    path('base/', Base , name='base'),
    path('', list_forms, name='list_forms'),
    path('create/', create_form, name='create_form'),
    path('add_question/<int:form_id>/', add_question, name='add_question'),
    path('submit/<int:form_id>/', submit_response, name='submit_response'),
    path('analytics/<int:form_id>/', view_analytics, name='view_analytics'),
    path('edit_form/<int:form_id>/', edit_form, name='edit_form'),
    path('edit_question/<int:question_id>/', edit_question, name='edit_question'),
    path('register/', register, name='register'),
    path('forms/<int:form_id>/reorder/', reorder_questions, name='reorder_questions'),
    path('delete-question/<int:question_id>/',delete_question, name='delete_question'),
    path('generate-form-qr/<int:form_id>/', generate_form_qr, name='generate_form_qr'), 
]