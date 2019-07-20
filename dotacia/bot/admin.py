from django.contrib import admin

# Register your models here.
from bot.models import ISIC, ISICHolder


@admin.register(ISIC)
class ISICAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        print(ISIC.objects.prioritized())
        return super().get_queryset(request)


@admin.register(ISICHolder)
class ISICHolderAdmin(admin.ModelAdmin):
    pass
