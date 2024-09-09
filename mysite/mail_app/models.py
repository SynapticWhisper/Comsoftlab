import datetime
from django.db import models


# Create your models here.
class User(models.Model):
    username: str = models.EmailField(max_length=200, unique=True)
    password: str = models.CharField(max_length=255)


class Message(models.Model):
    message_uid = models.BinaryField(primary_key=True)
    from_user: str = models.CharField(max_length=200)
    theme: str = models.CharField(max_length=200)
    dispatch_date: datetime = models.DateTimeField("dispatch date")
    delivery_date: datetime = models.DateTimeField("delivery date")
    message_text: str = models.TextField()
    attachments = models.JSONField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

