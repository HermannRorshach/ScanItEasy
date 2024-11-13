from django import forms
from .models import DocumentTemplate

class DocumentTemplateForm(forms.ModelForm):
    class Meta:
        model = DocumentTemplate
        fields = ['ribbon_color', 'translator', 'page_count', 'docx_file', 'last_page_scan']
        widgets = {
            # Для поля выбора цвета ленточки можно установить специальный виджет, если нужно
            'ribbon_color': forms.Select(attrs={'class': 'form-select'}),
            'translator': forms.Select(attrs={'class': 'form-select'}),
            'page_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'docx_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'last_page_scan': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    # Кастомная валидация поля "Количество страниц"
    def clean_page_count(self):
        page_count = self.cleaned_data.get('page_count')
        if page_count < 1:
            raise forms.ValidationError("Количество страниц не может быть меньше 1.")
        return page_count

    # Кастомная валидация для поля "Файл DOCX"
    def clean_docx_file(self):
        docx_file = self.cleaned_data.get('docx_file')
        if docx_file and not docx_file.name.endswith('.docx'):
            raise forms.ValidationError("Пожалуйста, загрузите файл в формате .docx")
        return docx_file

    # Кастомная валидация для поля "Скан последней страницы"
    def clean_last_page_scan(self):
        scan = self.cleaned_data.get('last_page_scan')
        if scan:
            if not scan.name.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf')):
                raise forms.ValidationError("Файл должен быть в формате JPG, PNG или PDF.")
        return scan
