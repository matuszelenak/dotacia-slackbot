from django.core.exceptions import ValidationError
from django.db import transaction

from bot.models import SlackUser, ISIC, ISICUsageLog
from bot.tasks import NotifyHoldersOfUsageTask


def requires_isic(func):
    def wrapper(*args, **kwargs):
        slack_user_id = kwargs.pop('slack_user_id')
        holder = SlackUser.objects.for_user_id(slack_user_id)
        if not holder.isic:
            return 'You do not have any ISIC number registered'
        kwargs.update({
            'isic': holder.isic
        })
        return func(*args, **kwargs)

    return wrapper


def register_number(slack_user_id, *args, **kwargs):
    holder = SlackUser.objects.for_user_id(slack_user_id)
    if holder.isic:
        if kwargs.get('number') == holder.isic.number:
            return 'You already registered an ISIC with this number'
        holder.isic.delete()
        holder.isic.save()

    try:
        holder.isic = ISIC.objects.create(
            holder=holder,
            number=kwargs.get('number'),
        )
        holder.save()
    except ValidationError as e:
        return e.message

    return f'Number {holder.isic.number_pretty_print} successfully registered'


def give_number(*args, **kwargs):
    amount = int(kwargs.get('amount', 1))
    requested_by = SlackUser.objects.get(slack_user_id=kwargs.pop('slack_user_id'))
    isics = ISIC.objects.exclude(holder=requested_by).prioritized()

    if not isics.exists():
        return 'Unfortunately, the pool of ISIC numbers for today has been exhausted'

    msg_parts, acc = [], 0
    usage_log_pks = []
    for isic in isics:
        withdrawn_usages = ISIC.MAX_DAILY_USAGES - isic.usages
        acc += withdrawn_usages
        if acc >= amount:
            withdrawn_usages -= (acc - amount)

        isic.usages += withdrawn_usages
        isic.save()

        msg_parts.append(isic.number_pretty_print + (f' (x{withdrawn_usages})' if withdrawn_usages > 1 else ''))
        for _ in range(withdrawn_usages):
            log = ISICUsageLog.objects.create(
                isic=isic,
                requested_by=requested_by
            )
            usage_log_pks.append(log.pk)

        if acc >= amount:
            break

    transaction.on_commit(lambda: NotifyHoldersOfUsageTask().delay(usage_log_pks=usage_log_pks))

    return '\n'.join(msg_parts)


@requires_isic
def enable_number(isic=None):
    isic.enabled = True
    isic.save()
    return 'Sharing of your ISIC number enabled'


@requires_isic
def disable_number(isic=None):
    isic.enabled = False
    isic.save()
    return 'Sharing of your ISIC number disabled'


@requires_isic
def use_number(isic=None):
    isic.usages += 1
    isic.save()

    msg = isic.number_pretty_print
    if isic.usages > ISIC.MAX_DAILY_USAGES:
        msg += ':warning: It seems you have no dotations left'

    return msg


@requires_isic
def set_number_priority(isic=None, **kwargs):
    priority = kwargs.pop('priority')
    for v, k in ISIC.PRIORITY_CHOICES:
        if k == priority:
            isic.priority = v
            isic.save()
            return 'Priority successfully changed'
    return 'Invalid priority specified'
