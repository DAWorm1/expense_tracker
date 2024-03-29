"""
URL configuration for expense_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import index as HomePage
from .htmx_views import change_sort

urlpatterns = [
    path('', HomePage,name="index"),
    path('account/',include("account_manager.urls")),
    path('auth/', include("auth_manager.urls")),
    path('admin/', admin.site.urls),
]

htmx_patterns = [
    path('change_sort/',change_sort),
]

urlpatterns += htmx_patterns