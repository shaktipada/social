from django.contrib.auth.models import User
from django import template

from social_core.models import (Friend, Notification,
    Message, Like, Follow)

register = template.Library()


@register.inclusion_tag('includes/_are_connected.html')
def are_connected(request_from, request_to):
    friend, friend_request, follow = Friend.are_connected(
        request_from, request_to)

    return {'friend': friend, 'friend_request': friend_request,
    'request_from': request_from, 'request_to': request_to,
    'follow': follow}

# this notify is used in the template header
@register.assignment_tag
def notify(user):
    notify = Notification.objects.filter(
        notification_for=user, seen=False)
    return notify

@register.assignment_tag
def unread_messages(user):
    messages = Message.objects.filter(
        message_for=user, unread=True)
    return messages

@register.assignment_tag
def check_liked(content_object, id, user):
    return content_object.like(id, user)