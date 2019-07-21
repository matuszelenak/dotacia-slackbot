from django.conf import settings
from django.contrib.auth.models import User, AbstractUser, UserManager
from django.core.validators import RegexValidator
from django.db import models
from slack import WebClient


class SlackUserManager(UserManager):
    def for_user_id(self, user_id):
        try:
            return self.filter(slack_user_id=user_id).get()
        except SlackUser.DoesNotExist:
            client = WebClient(token=settings.SLACK_BOT_USER_TOKEN)
            user_info = client.users_info(user=user_id)['user']
            channel_id = client.im_open(user=user_id)['channel']['id']
            user = SlackUser.objects.create(
                slack_user_id=user_id,
                slack_channel_id=channel_id,
                username=user_info['name'],
                email=user_info['profile']['email'],
                first_name=user_info['profile'].get('first_name', ''),
                last_name=user_info['profile'].get('last_name', '')
            )
            user.set_unusable_password()
            user.save()
            return user


class SlackUser(AbstractUser):
    slack_user_id = models.CharField(max_length=20, null=True, blank=True, unique=True)
    slack_channel_id = models.CharField(max_length=20, null=True, blank=True, unique=True)
    objects = SlackUserManager()

    def __str__(self):
        return f'{self.username} ({self.slack_user_id})'


class ISICQuerySet(models.QuerySet):
    def usable(self):
        return self.filter(active=True, usages__lt=ISIC.MAX_DAILY_USAGES)

    def prioritized(self):
        return self.usable().order_by('-priority', 'usages', '?')


class ISIC(models.Model):
    MAX_DAILY_USAGES = 5

    PRIORITY_LOW = 1
    PRIORITY_MEDIUM = 2
    PRIORITY_HIGH = 3
    PRIORITY_CHOICES = (
        (PRIORITY_LOW, 'low'),
        (PRIORITY_MEDIUM, 'medium'),
        (PRIORITY_HIGH, 'high')
    )

    holder = models.ForeignKey('bot.SlackUser', on_delete=models.CASCADE, related_name='isics')
    number = models.CharField(blank=False, max_length=17, validators=[
        RegexValidator(
            regex='^[0-9]{17}$',
            message='ISIC number must have 17 digits',
            code='invalid_number'
        )
    ])

    active = models.BooleanField(default=True)
    usages = models.PositiveIntegerField(default=0)

    priority = models.PositiveIntegerField(choices=PRIORITY_CHOICES, default=PRIORITY_HIGH)

    objects = ISICQuerySet.as_manager()

    @property
    def number_pretty_print(self):
        return f'*{self.number[:1]} {self.number[1:5]} {self.number[5:9]} {self.number[9:13]} {self.number[13:]}*'

    def __str__(self):
        return f'ISIC {self.number} ({self.holder.username}) : {self.usages} usages, priority {self.priority}'


class ISICUsageLog(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    requested_by = models.ForeignKey('bot.SlackUser', related_name='usage_logs', on_delete=models.CASCADE)
    isic = models.ForeignKey('bot.ISIC', on_delete=models.CASCADE, related_name='usage_logs')

    def __str__(self):
        return f'{self.requested_by.username} requested {self.isic.number_pretty_print} on {self.date_created}'


class Meme(models.Model):
    title = models.CharField(max_length=128, blank=True)
    file = models.FileField()
