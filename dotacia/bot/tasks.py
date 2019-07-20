from celery.task import Task
from django.db import transaction

from bot.models import ISIC


class ISICDailyResetTask(Task):

    @transaction.atomic
    def run(self, *args, **kwargs):
        ISIC.objects.all().update(usages=0)
