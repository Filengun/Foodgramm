from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'password',
        'first_name',
        'last_name',
        'email'
    )
    list_filter = ('username',)
    empty_value_display = 'нет информации'


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'subscriber',
        'author'
    )


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
