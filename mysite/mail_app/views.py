from http.client import HTTPException
from django.db import IntegrityError
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .imap_client import IMAPService
from .models import User, Message



def index(request):
    accounts = User.objects.all()
    context = {
        'accounts': accounts,
    }
    return render(request, "main_page/index.html", context)


def login(request):
    return render(request, "login/index.html")


def select_account(request, account_id):
    messages = Message.objects.filter(user=account_id).order_by("-delivery_date")[:20]
    context = {
        'messages': messages
    }
    return render(request, "mail/index.html", context)


def register(request):
    email = request.POST.get("email")
    password = request.POST.get("password")
    imap_server = request.POST.get("imap-server")

    try:
        IMAPService(email, password, imap_server)
        new_user = User(email=email, password=password, imap_server=imap_server)
        new_user.save()
        return HttpResponseRedirect("/mail_app/")
    except HTTPException:
        return render(
            request,
            "login/index.html",
            {
                "error_message": "Incorrect email or password",
            },
        )
    except IntegrityError:
        return render(
            request,
            "login/index.html",
            {
                "error_message": "Accaunt already exists",
            },
        )
    except Exception:
        return render(
            request,
            "login/index.html",
            {
                "error_message": "Initial server error",
            },
        )

