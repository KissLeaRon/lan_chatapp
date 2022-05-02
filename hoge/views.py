from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("this msg is wrote in hoge/viwes.py")

# Create your views here.
