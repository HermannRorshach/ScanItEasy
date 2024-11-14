import os
import shutil
from io import BytesIO

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView

from .convertation import Converter
from .forms import DocumentTemplateForm
from .models import DocumentTemplate


class DocumentTemplateView(View):

    def get(self, request):
        form = DocumentTemplateForm()
        return render(request, 'scanner/document_template_form.html', {'form': form})


    # Функция для удаления файлов в директории
    def clear_directory(self, directory_path):
        if os.path.exists(directory_path):
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

    def post(self, request):
        form = DocumentTemplateForm(request.POST, request.FILES)
        output_dir = os.path.join(settings.MEDIA_ROOT, 'output')
        self.clear_directory(output_dir)

        if form.is_valid():
            # Сохраняем данные формы в модель
            document_template = form.save()
            documents_dir = document_template.get_documents_directory()
            scans_dir = document_template.get_scans_directory()
            print('scans_dir =', scans_dir)
            print('documents_dir =', documents_dir)

            # Получаем загруженные файлы
            docx_file = document_template.docx_file
            last_page_scan = document_template.last_page_scan

            # Определяем путь для результата
            original_filename = os.path.splitext(docx_file.name)[0]
            print(original_filename)
            output_pdf_path = os.path.join('media', f'{original_filename}.pdf')

            # Создаем экземпляр Converter
            converter = Converter(docx_file.path, output_pdf_path)

            # Преобразуем DOCX в PDF
            converter.docx_to_pdf()

            # Преобразуем PDF в черно-белые изображения и сохраняем их
            temp_images = converter.pdf_to_bw()

            # Создаем новый PDF из изображений
            converter.pngs_to_pdf(output_pdf_path, temp_images)

            # Добавляем изображения (ленточки) в PDF
            first_page_image = os.path.join(settings.BASE_DIR, 'static', 'doc_decorations', 'Красная лента. Первая страница.png')
            other_pages_image = os.path.join(settings.BASE_DIR, 'static', 'doc_decorations', 'Уголок с красной лентой.png')
            last_page_image = os.path.join(settings.BASE_DIR, 'static', 'doc_decorations', 'Подпись переводчика.png')
            converter.add_image_to_pdf(first_page_image, other_pages_image, last_page_image)

            converter.add_last_page_scan(last_page_scan)
            # Сжимаем PDF
            compressed_pdf_path = os.path.join(settings.BASE_DIR, 'media', 'output', f'compressed_output_{document_template.id}.pdf')
            converter.compress_pdf(output_pdf=compressed_pdf_path, input_pdf=output_pdf_path)

            # Очистка временных изображений
            converter.clean_temp_images()

            with open(compressed_pdf_path, 'rb') as pdf_file:
                # Создаем поток, в который считываем данные из файла
                pdf_output_stream = BytesIO(pdf_file.read())

                # Перемещаем указатель потока в начало
                pdf_output_stream.seek(0)
                # Очистка содержимого папок 'documents' и 'scans'
                self.clear_directory(documents_dir)
                print('Очищаем содержимое папок')
                self.clear_directory(scans_dir)

                # Используем FileResponse для отправки файла с флагом as_attachment=True
                return FileResponse(
                    pdf_output_stream,
                    as_attachment=True,
                    filename=f"{original_filename.replace('_', ' ')}.pdf"
                )


            return response

        return render(request, 'document_template_form.html', {'form': form})


def MyTemplatesView(request):
    return render(request, 'scanner/my_templates.html')


def upload_files(request):
    return render(request, 'scanner/upload_files.html')


def faq(request):
    return render(request, 'scanner/FAQ.html')


def contacts(request):
    return render(request, 'scanner/contacts.html')


# views.py

# views.py

import os

import pythoncom
import win32com.client
from django.conf import settings
from django.http import HttpResponse


def check_word_com(request):
    try:
        # Инициализация COM
        pythoncom.CoInitialize()

        # Путь для сохранения файла в папке media
        save_path = os.path.join(settings.MEDIA_ROOT, "test.docx")

        # Попытаться создать объект Word через COM
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = True  # Показать Word
        doc = word.Documents.Add()  # Создать новый документ
        doc.Content.Text = "Hello from Python!"  # Написать текст

        # Проверяем, существует ли директория для сохранения
        if not os.path.exists(settings.MEDIA_ROOT):
            return HttpResponse(f"Ошибка: Папка для сохранения файлов ({settings.MEDIA_ROOT}) не существует.")

        # Сохранить документ
        doc.SaveAs(save_path)  # Сохранить документ в папку media
        doc.Close()
        word.Quit()

        # Завершаем работу с COM
        pythoncom.CoUninitialize()

        return HttpResponse(f"Word доступен и файл успешно сохранен по пути: {save_path}")

    except Exception as e:
        # Завершаем работу с COM в случае ошибки
        pythoncom.CoUninitialize()
        return HttpResponse(f"Ошибка: {e}")
