from bot.models import ISICHolder, ISIC


def requires_isic(func):
    def wrapper(*args, **kwargs):
        slack_user_id = kwargs.pop('slack_user_id')
        holder = ISICHolder.objects.for_user_id(slack_user_id)
        if not holder.isic:
            return 'You do not have any ISIC number registered'
        kwargs.update({
            'isic': holder.isic
        })
        return func(*args, **kwargs)

    return wrapper


def register_number(slack_user_id, *args, **kwargs):
    holder = ISICHolder.objects.for_user_id(slack_user_id)
    if holder.isic:
        if kwargs.get('number') == holder.isic.number:
            return 'You already registered an ISIC with this number'
        holder.isic.delete()
        holder.isic.save()

    print(kwargs)
    holder.isic = ISIC.objects.create(
        holder=holder,
        number=kwargs.get('number'),
        priority=kwargs.get('priority')
    )
    holder.save()

    return f'Number {holder.isic.number_pretty_print} successfully registered'


def give_number(*args, **kwargs):
    pass


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
def set_number_priority(isic=None, priority=ISIC.MAX_PRIORITY):
    isic.priority = priority
    isic.save()
    return 'Priority successfully changed'


def print_help(*args, **kwargs):
    pass