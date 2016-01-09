from django.contrib import admin

from social_core.models import (Post, Comment,
    FriendBase, Friend, DeletedFriend,
    Notification, Message, Like, Follow)

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(FriendBase)
admin.site.register(Friend)
admin.site.register(DeletedFriend)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(Like)
admin.site.register(Follow)