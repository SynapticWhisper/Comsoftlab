from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import User


def index(request):
    accounts = User.objects.all()  # Получаем список всех пользователей из базы данных
    context = {
        'accounts': accounts,  # Передаем список аккаунтов в шаблон
    }
    return render(request, "main_page/index.html", context)

def login(request):
    return render(request, "login/index.html")
    
def register(request):
    # Do some stuff
    a = 0
    if a:
        return HttpResponseRedirect("/mail_app/")
    else:
        return render(
            request,
            "login/index.html",
            {
                "error_message": "Incorrect email or password",
            },
        )
