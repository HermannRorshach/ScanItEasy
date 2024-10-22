from django.urls import path

from . import views

app_name = 'CreatePresentation'

urlpatterns = [
    path('', views.upload_files, name='upload_files'),
    path('faq', views.faq, name='faq'),
    path('contacts/', views.contacts, name='contacts'),
]
