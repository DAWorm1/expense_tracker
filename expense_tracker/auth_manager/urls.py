from django.urls import path
from . import views as AuthViews

app_name = "auth_manager"

urlpatterns = [
    path('login/', AuthViews.login_page,name="auth-login"),
    path('logout/', AuthViews.logout_page,name="auth-logout"),
]
