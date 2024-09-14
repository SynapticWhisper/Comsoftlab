from django.urls import path

from . import views
from .consumer import MailConsumer

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.sign_in, name="login"),
    path("register", views.sign_up, name="register"),
    path("<int:user_id>", views.select_account, name="select_account")
]