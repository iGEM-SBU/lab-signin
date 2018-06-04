from django.db import models
from django.utils import timezone
from . import constants


# Create your models here.
class Member(models.Model):
    name = models.CharField(max_length=9, choices=constants.MEMBER_NAMES, blank=False)
    sign_in_time = models.DateTimeField(auto_now=False, default=timezone.now)
    sign_out_time = models.DateTimeField(auto_now=False, default=timezone.now)
    is_signed_in = models.BooleanField(default=False, editable=True)
    last_time_block = models.PositiveIntegerField(default=0)  # measured in minutes
    total_time = models.PositiveIntegerField(default=0)  # measured in minutes

    def __str__(self):
        return self.name

    def sign_in(self, time):
        if self.is_signed_in:
            print('User tried to sign in but user is already signed in')
            return
        self.sign_in_time = time
        print(time)
        print(self.sign_in_time)
        self.is_signed_in = True
        print(self.is_signed_in)

    def sign_out(self, time):
        if not self.is_signed_in:
            print('User tried to sign out but user is already signed out')
            return
        self.sign_out_time = time
        self.last_time_block = int((self.sign_out_time - self.sign_in_time).seconds/60)
        self.total_time += self.last_time_block
        self.is_signed_in = False

    def get_hours(self):
        return self.total_time/60
