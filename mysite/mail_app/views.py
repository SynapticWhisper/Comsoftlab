from http.client import HTTPException
from django.db import IntegrityError
from django.shortcuts import render
from django.http import HttpResponseRedirect


from .imap_client import IMAPService
from .models import User, Message



def index(request):
    accounts = User.objects.all()
    context = {
        'accounts': accounts,
    }
    return render(request, "home/index.html", context)


def select_account(request, user_id):
    messages = Message.objects.filter(user=user_id).order_by("-delivery_date")[:20]
    messages = [
        {
            'message_uid': message.message_uid.tobytes(),
            'from_user': message.from_user,
            'theme': message.theme,
            'delivery_date': message.delivery_date.strftime('%d %b %Y %H:%M:%S'),
            'message_text': message.message_text,
            'attachments': message.attachments
        } for message in messages
    ]
    context = {
        'user_id': user_id,
        'messages': messages
    }
    return render(request, "mail/index.html", context)


def sign_in(request):
    return render(request, "auth/index.html")


def sign_up(request):
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
            "auth/index.html",
            {
                "error_message": "Incorrect email or password",
            },
        )
    except IntegrityError:
        return render(
            request,
            "auth/index.html",
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

