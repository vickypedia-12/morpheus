from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.db.models import Count
from django.core.exceptions import ValidationError
from ..models import Form, Question, Response as FormResponse, Answer
from .serializers import (
    FormSerializer, QuestionSerializer, ResponseSerializer, 
    AnswerSerializer, UserRegistrationSerializer
)

class CustomAuthToken(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            
            if not username or not password:
                return Response({
                    'error': 'Both username and password are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = authenticate(username=username, password=password)
            if not user:
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email,
                'username': user.username
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'user_id': user.id,
                'email': user.email,
                'username': user.username
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FormViewSet(viewsets.ModelViewSet):
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Form.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        try:
            serializer.save(created_by=self.request.user)
        except Exception as e:
            raise ValidationError(str(e))
            
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        try:
            form = self.get_object()
            response_count = FormResponse.objects.filter(form=form).count()
            question_stats = []
            
            for question in form.questions.all():
                answers = Answer.objects.filter(question=question)
                if question.question_type in ['text', 'dropdown']:
                    stats = answers.values('text_answer').annotate(
                        count=Count('text_answer')
                    )
                else:  # checkbox
                    stats = answers.values('selected_options').annotate(
                        count=Count('selected_options')
                    )
                question_stats.append({
                    'question_id': question.id,
                    'question_text': question.text,
                    'stats': stats
                })
                
            return Response({
                'total_responses': response_count,
                'questions': question_stats
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Question.objects.filter(form__created_by=self.request.user)

    def perform_create(self, serializer):
        try:
            form_id = self.request.data.get('form')
            form = get_object_or_404(Form, id=form_id, created_by=self.request.user)
            serializer.save(form=form)
        except Exception as e:
            raise ValidationError(str(e))

    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        try:
            question = self.get_object()
            new_order = request.data.get('order')
            if new_order is None:
                return Response({
                    'error': 'Order value required'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            question.order = new_order
            question.save()
            return Response({'status': 'success'})
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ResponseViewSet(viewsets.ModelViewSet):
    serializer_class = ResponseSerializer
    permission_classes = [AllowAny]  # Allow anonymous responses
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return FormResponse.objects.filter(form__created_by=self.request.user)
        return FormResponse.objects.none()
    
    def create(self, request, *args, **kwargs):
        try:
            form_id = request.data.get('form')
            form = get_object_or_404(Form, id=form_id)
            
            # Create response
            response = FormResponse.objects.create(form=form)
            
            # Process answers
            answers_data = request.data.get('answers', [])
            for answer_data in answers_data:
                question = get_object_or_404(
                    Question, 
                    id=answer_data.get('question'),
                    form=form
                )
                
                Answer.objects.create(
                    response=response,
                    question=question,
                    text_answer=answer_data.get('text_answer', ''),
                    selected_options=answer_data.get('selected_options', [])
                )
                
            return Response({
                'id': response.id,
                'message': 'Response submitted successfully'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def answers(self, request, pk=None):
        try:
            response = self.get_object()
            answers = Answer.objects.filter(response=response)
            serializer = AnswerSerializer(answers, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Please provide both username and password'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        user = authenticate(username=username, password=password)
        
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserRegistrationSerializer(user).data
            })
            
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)