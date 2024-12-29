from django.contrib import admin
from .models import Form, Question, Response, Answer

admin.site.register(Form)
admin.site.register(Question)
admin.site.register(Response)
admin.site.register(Answer)