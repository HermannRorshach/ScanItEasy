from django.urls import path

from . import views

app_name = 'scanner'

urlpatterns = [
    path('', views.DocumentTemplateCreateView.as_view(), name='document_template'),
    path('upload_files', views.upload_files, name='upload_files'),
    path('faq', views.faq, name='faq'),
    path('contacts/', views.contacts, name='contacts'),
    path('my-templates/', views.MyTemplatesView, name='my_templates'),
]
