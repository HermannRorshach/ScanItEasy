import os
import shutil
from io import BytesIO

from django.conf import settings

from django.http import FileResponse
from django.shortcuts import render



def upload_files(request):
    return render(request, 'scanner/upload_files.html')


def faq(request):
    return render(request, 'scanner/FAQ.html')


def contacts(request):
    return render(request, 'scanner/contacts.html')
