from celery.task import Task
from django.conf import settings
from django.db import transaction
from slack import WebClient

from bot.models import ISIC, ISICUsageLog


class ISICDailyResetTask(Task):

    @transaction.atomic
    def run(self, *args, **kwargs):
        ISIC.objects.all().update(usages=0)


class NotifyHoldersOfUsageTask(Task):
    def run(self, usage_log_pks, *args, **kwargs):
        logs = ISICUsageLog.objects.select_related('isic__holder', 'requested_by').filter(id__in=usage_log_pks)
        client = WebClient(token=settings.SLACK_BOT_USER_TOKEN)

        for log in logs:
            client.chat_postMessage(
                channel=log.isic.holder.slack_channel_id,
                text=f'Your ISIC ({log.isic.number_pretty_print}) has just been used by <@{log.requested_by.slack_user_id}>'
            )
