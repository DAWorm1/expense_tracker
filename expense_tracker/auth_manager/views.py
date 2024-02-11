from django.shortcuts import render
from django.http.response import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate,logout,login
from django.urls import reverse

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http.request import HttpRequest

# Create your views here.
def login_page(request: 'HttpRequest'):
    if request.method == "GET":
        return render(request,"auth_manager/login.html")
    
    # Username/Password has been submitted
    if request.method == "POST":
        username_provided = request.POST.get('username')
        password_provided = request.POST.get('password')

        if username_provided is None or password_provided is None:
            raise NotImplementedError("PENDING.")
        
        user = authenticate(username=username_provided,password=password_provided)
        if user is not None:
            login(request,user)
            if request.GET.get("redirect"):
                return HttpResponseRedirect(request.GET.get("redirect"))
            return HttpResponseRedirect(reverse("index"))
        else:
            raise NotImplementedError("PENDING")


def logout_page(request: 'HttpRequest'):
    logout(request)
    return HttpResponseRedirect("/")