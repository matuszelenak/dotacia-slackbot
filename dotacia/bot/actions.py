from django.core.exceptions import ValidationError
from django.db import transaction

from bot.models import SlackUser, ISIC, ISICUsageLog
from bot.tasks import NotifyHoldersOfUsageTask


def requires_isic(func):
    def wrapper(*args, **kwargs):
        slack_user_id = kwargs.pop('slack_user_id')
        last_4 = kwargs.get('last_4')

        holder = SlackUser.objects.for_user_id(slack_user_id)
        if not ISIC.objects.filter(holder=holder).exists():
            return 'You do not have any ISIC number registered'

        if last_4:
            isic = ISIC.objects.filter(holder=holder, number__endswith=last_4).first()
            if not isic:
                return 'None of your ISICs end with these digits'
            else:
                kwargs.update({'isic': isic})

        else:
            if ISIC.objects.filter(holder=holder).count() > 1:
                return 'Please specify the last 4 digits of the ISIC'

            kwargs.update({'isic': ISIC.objects.get(holder=holder)})

        return func(*args, **kwargs)

    return wrapper


def register_number(slack_user_id, number=None, **kwargs):
    holder = SlackUser.objects.for_user_id(slack_user_id)
    if ISIC.objects.filter(number=number, holder=holder).exists():
        return 'You already registered an ISIC with this number'

    try:
        isic = ISIC(
            holder=holder,
            number=number,
        )
        isic.full_clean()
        isic.save()
    except ValidationError:
        return 'Invalid number'

    return f'Number {number} successfully registered'


def give_number(slack_user_id=None, amount=1, **kwargs):
    amount = int(amount)
    requested_by = SlackUser.objects.get(slack_user_id=slack_user_id)
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
def enable_number(isic=None, **kwargs):
    isic.enabled = True
    isic.save()
    return f'Sharing of {isic.number_pretty_print} number enabled'


@requires_isic
def disable_number(isic=None, **kwargs):
    isic.enabled = False
    isic.save()
    return f'Sharing of {isic.number_pretty_print} disabled'


@requires_isic
def use_number(isic=None, **kwargs):
    isic.usages += 1
    isic.save()

    msg = isic.number_pretty_print
    if isic.usages > ISIC.MAX_DAILY_USAGES:
        msg += ' :warning: It seems you have no dotations left :warning:'

    return msg


@requires_isic
def set_number_priority(isic=None, **kwargs):
    priority = kwargs.pop('priority')
    for v, k in ISIC.PRIORITY_CHOICES:
        if k == priority:
            isic.priority = v
            isic.save()
            return f'Priority of {isic.number_pretty_print} successfully changed'
    return 'Invalid priority specified'


def print_info(slack_user_id, **kwargs):
    holder = SlackUser.objects.for_user_id(slack_user_id)
    return '\n'.join(
        [
            f'ISIC {x.number_pretty_print}, {x.get_priority_display()} priority, used {x.usages} dotations today'
            for x in ISIC.objects.filter(holder=holder)
        ]
    )
