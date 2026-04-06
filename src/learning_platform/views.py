from django.shortcuts import render
from django.db import transaction

def homepage(request, *args, **kwargs):
    template_name = "home.html"
    print(f'path: {request.path}')
    return render(request, template_name)