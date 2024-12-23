# Generated by Django 5.1.2 on 2024-11-13 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ribbon_color', models.CharField(choices=[('red', 'Красный'), ('blue', 'Синий')], default='red', max_length=20, verbose_name='Цвет ленточки')),
                ('translator', models.CharField(choices=[('translator_1', 'Бяшимов Довран'), ('translator_2', 'Шевчук Мария'), ('translator_3', 'Слуцкий Андрей')], default='translator_1', max_length=50, verbose_name='Имя переводчика')),
                ('page_count', models.IntegerField(default=3, verbose_name='Количество страниц')),
                ('docx_file', models.FileField(upload_to='documents/', verbose_name='Файл DOCX')),
                ('last_page_scan', models.ImageField(blank=True, null=True, upload_to='scans/', verbose_name='Скан последней страницы')),
            ],
            options={
                'verbose_name': 'Шаблон документа',
                'verbose_name_plural': 'Шаблоны документов',
            },
        ),
    ]
