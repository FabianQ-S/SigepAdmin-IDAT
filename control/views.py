from django.shortcuts import render


def index(request):
    """Vista principal del sistema"""
    return render(request, 'index.html')
