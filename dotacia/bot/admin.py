from django.contrib import admin

from bot.models import ISIC, SlackUser, ISICUsageLog, Meme


@admin.register(ISIC)
class ISICAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        a = ISIC.objects.prioritized()
        print(a)
        return a


@admin.register(SlackUser)
class SlackUserAdmin(admin.ModelAdmin):
    pass


@admin.register(ISICUsageLog)
class ISICUsageLogAdmin(admin.ModelAdmin):
    pass


@admin.register(Meme)
class MemeAdmin(admin.ModelAdmin):
    pass
