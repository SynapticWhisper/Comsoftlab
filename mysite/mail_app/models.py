from django.db import models


class User(models.Model):
    username = models.EmailField(max_length=200, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username


class Message(models.Model):
    message_uid = models.BinaryField(primary_key=True)
    from_user = models.CharField(max_length=200)
    theme = models.CharField(max_length=200)
    delivery_date = models.DateTimeField("delivery date")
    message_text = models.TextField()
    attachments = models.JSONField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.theme
