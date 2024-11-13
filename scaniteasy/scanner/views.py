import os
import shutil
from io import BytesIO

from django.conf import settings
from django.http import FileResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import DocumentTemplateForm
from .models import DocumentTemplate


class DocumentTemplateCreateView(CreateView):
    model = DocumentTemplate
    form_class = DocumentTemplateForm  # форма, которую нужно создать
    template_name = 'scanner/document_form.html'  # шаблон, который будет использоваться
    success_url = reverse_lazy('template_list')  # Путь, куда перенаправлять после успешного сохранения

    def form_valid(self, form):
        # Здесь можно добавить дополнительную логику перед сохранением формы
        # Например, можно модифицировать данные перед сохранением
        response = super().form_valid(form)
        # Дополнительная логика (например, уведомления, обработка данных) может быть добавлена здесь
        return response

    def form_invalid(self, form):
        # Обрабатываем случай, если форма невалидна (например, ошибки валидации)
        return self.render_to_response({'form': form})

def MyTemplatesView(request):
    return render(request, 'scanner/my_templates.html')


def upload_files(request):
    return render(request, 'scanner/upload_files.html')


def faq(request):
    return render(request, 'scanner/FAQ.html')


def contacts(request):
    return render(request, 'scanner/contacts.html')
