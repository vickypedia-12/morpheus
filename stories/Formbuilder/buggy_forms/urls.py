from django.urls import path, include
from .views import (
     create_form, register, 
     add_question, list_forms, 
     submit_response, view_analytics, 
     Base, edit_form, edit_question, 
     reorder_questions, delete_question,
     generate_form_qr, delete_form, 
     login_view
)
from django.conf.urls import handler404, handler500
from django.contrib.auth.views import LogoutView
from rest_framework.routers import DefaultRouter
from .api.views_api import FormViewSet, QuestionViewSet, ResponseViewSet, CustomAuthToken, RegisterView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

router = DefaultRouter()
router.register(r'forms', FormViewSet, basename='form')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'responses', ResponseViewSet, basename='response')

schema_view = get_schema_view(
   openapi.Info(
        title="Forms API",
        default_version='v1',
        description="API for form management",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

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
    path('delete-form/<int:form_id>/', delete_form, name='delete_form'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='list_forms'), name='logout'),
    path('api/', include(router.urls)),
    path('api/auth/', CustomAuthToken.as_view(), name='api_token_auth'),  # Token Auth
    path('api-auth/', include('rest_framework.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
]