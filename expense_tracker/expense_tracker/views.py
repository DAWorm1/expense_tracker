from django.shortcuts import render
from django.http.response import HttpResponseRedirect,HttpResponse
from django.http.request import HttpRequest

def index(request: HttpRequest):
    return render(request,"index.html")
    