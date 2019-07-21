from django.contrib import admin

from bot.models import ISIC, SlackUser, ISICUsageLog


@admin.register(ISIC)
class ISICAdmin(admin.ModelAdmin):
    pass


@admin.register(SlackUser)
class SlackUserAdmin(admin.ModelAdmin):
    pass


@admin.register(ISICUsageLog)
class ISICUsageLogAdmin(admin.ModelAdmin):
    pass
