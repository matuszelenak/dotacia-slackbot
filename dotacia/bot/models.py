from django.conf import settings
from django.contrib.auth.models import User, AbstractUser, UserManager
from django.db import models
from slack import WebClient


class ISICHolderManager(UserManager):
    def for_user_id(self, user_id):
        try:
            return self.filter(slack_user_id=user_id).get()
        except ISICHolder.DoesNotExist:
            client = WebClient(token=settings.SLACK_BOT_USER_TOKEN)
            user_info = client.users_info(user=user_id)['user']
            user = ISICHolder.objects.create(
                slack_user_id=user_id,
                username=user_info['name'],
                email=user_info['profile']['email'],
                first_name=user_info['profile']['first_name'],
                last_name=user_info['profile']['last_name']
            )
            user.set_unusable_password()
            user.save()
            return user


class ISICHolder(AbstractUser):
    slack_user_id = models.CharField(max_length=20, null=True, unique=True)
    isic = models.OneToOneField('bot.ISIC', on_delete=models.CASCADE, related_name='holder', null=True, blank=True)
    objects = ISICHolderManager()


class ISICQuerySet(models.QuerySet):
    def usable(self):
        return self.filter(active=True, usages__lt=ISIC.MAX_DAILY_USAGES)

    def prioritized(self):
        return self.usable()


class ISIC(models.Model):
    MAX_DAILY_USAGES = 2
    MAX_PRIORITY = 5

    number = models.CharField(max_length=17)

    active = models.BooleanField(default=True)
    usages = models.IntegerField(default=0)

    priority = models.PositiveIntegerField(default=MAX_PRIORITY)

    objects = ISICQuerySet.as_manager()

    @property
    def number_pretty_print(self):
        return f'*{self.number[:5]} {self.number[5:9]} {self.number[9:13]} {self.number[13:]}*'
