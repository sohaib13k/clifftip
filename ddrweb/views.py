from django.shortcuts import render
from django.http import HttpResponse

def ddrweb(request):
    return render(request, 'ddrweb/ddrweb.html')