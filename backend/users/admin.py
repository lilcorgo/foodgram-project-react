from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
    )
    list_filter = ('email', 'username',)
    search_fields = ('email', 'username',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'follower',
        'to_follow',
    )
    search_fields = ('follower__username', 'to_follow__username')
    empty_value_display = '-пусто-'
