from django.shortcuts import render


def index(request):
    # Vista principal
    return render(request, "index.html")
