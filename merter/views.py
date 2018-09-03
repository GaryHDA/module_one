
from django.shortcuts import render

def merTer(request):
    return render(request, 'merter/MerTer.html')
def index(request):
    return render(request, 'dirt/index.html')
