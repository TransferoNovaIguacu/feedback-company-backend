from django.db import models
from django.conf import settings

class TokenWallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} - {self.balance} tokens'

    def add_tokens(self, amount):
        self.balance += amount
        self.save()

    def remove_tokens(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False