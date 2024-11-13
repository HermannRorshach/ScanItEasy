from django.db import models

class DocumentTemplate(models.Model):

    LENTICOLOR_CHOICES = [
        ('red', 'Красный'),
        ('blue', 'Синий'),
    ]

    # Выбор имени переводчика
    TRANSLATOR_CHOICES = [
        ('translator_1', 'Бяшимов Довран'),
        ('translator_2', 'Шевчук Мария'),
        ('translator_3', 'Слуцкий Андрей'),
    ]

    # Поля модели
    ribbon_color = models.CharField(
        max_length=20,
        choices=LENTICOLOR_CHOICES,
        default='red',
        verbose_name='Цвет ленточки'
    )
    translator = models.CharField(
        max_length=50,
        choices=TRANSLATOR_CHOICES,
        default='translator_1',
        verbose_name='Имя переводчика'
    )
    page_count = models.IntegerField(
        default=3,
        verbose_name='Количество страниц'
    )
    docx_file = models.FileField(
        upload_to='documents/',
        verbose_name='Файл DOCX'
    )
    last_page_scan = models.ImageField(
        upload_to='scans/',
        verbose_name='Скан последней страницы',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Шаблон {self.translator} - {self.ribbon_color}"

    class Meta:
        verbose_name = 'Шаблон документа'
        verbose_name_plural = 'Шаблоны документов'
