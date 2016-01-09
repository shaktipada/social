from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.urlresolvers import reverse


class DateTimeBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract =  True
        ordering = ["-created_at"]

class Like(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    liked_by = models.ForeignKey(User,
        limit_choices_to={'is_active': True})
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.liked_by.username

    @classmethod
    def liked(cls, content_object, user):
        liked = cls.objects.create(
            content_object=content_object, liked_by=user)


class Follow(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    followed_by = models.ForeignKey(User,
        limit_choices_to={'is_active': True})
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.followed_by.username

    @classmethod
    def following(cls, content_object, user):
        followed = cls.objects.create(
            content_object=content_object, followed_by=user)


class Post(DateTimeBase):
    posted_by = models.ForeignKey(User,
        limit_choices_to={'is_active': True})
    status = models.CharField(max_length=400)
    status_image = models.ImageField(upload_to='posts',
        null=True, blank=True)

    def __unicode__(self):
        return self.posted_by.username

    @classmethod
    def like(cls, id, user):
        post_type = ContentType.objects.get_for_model(Post)

        try:
            Like.objects.get(
                object_id=id, liked_by=user,
                content_type=post_type)
            result = True
        except Like.DoesNotExist:
            result = False

        return result


class Comment(DateTimeBase):
    commented_by = models.ForeignKey(User,
        limit_choices_to={'is_active': True})
    commented_on = models.ForeignKey(Post)
    comment = models.CharField(max_length=300)

    def __unicode__(self):
        return self.comment[:20]

    @classmethod
    def like(cls, id, user):
        comment_type = ContentType.objects.get_for_model(Comment)
        try:
            Like.objects.get(
                object_id=id, liked_by=user,
                content_type=comment_type)
            result = True
        except Like.DoesNotExist:
            result = False

        return result


class Message(DateTimeBase):
    message_by = models.ForeignKey(User,
        limit_choices_to={'is_active': True},
        related_name='sent_by')
    message_for = models.ForeignKey(User,
        limit_choices_to={'is_active': True},
        related_name='sent_to')
    message = models.TextField()
    unread = models.BooleanField(default=True)

    def __unicode__(self):
        return self.message_for.username

    def display(self):
        message_from = self.message_by
        message = self.message[:50]
        message = "User %s has sent you a message '%s'. click to read" % (
            message_from.username, message)
        return message


class FriendBase(DateTimeBase):
    request_from = models.ForeignKey(User, related_name='sent_requests')
    request_to = models.ForeignKey(User, related_name='received_requests')


class Friend(FriendBase):
    accepted = models.BooleanField(default=False)

    class Meta:
        abstract = False

    @classmethod
    def are_connected(cls, request_from, request_to):
        friends = cls.objects.filter(
            Q(request_from=request_from, request_to=request_to,
                accepted=True) |
            Q(request_from=request_to, request_to=request_from,
                accepted=True)
        )
        friend_requests = cls.objects.filter(
            Q(request_from=request_from, request_to=request_to,
                accepted=False) |
            Q(request_from=request_to, request_to=request_from,
                accepted=False)
        )

        try:
            Follow.objects.get(object_id=request_to.id,
                followed_by=request_from)
            follow = True
        except Follow.DoesNotExist:
            follow = False

        return friends.count(), friend_requests.count(), follow

    @classmethod
    def add_friend(cls, request_from, request_to):
        friend, friend_request, follow = cls.are_connected(request_from, request_to)
        if not friend or not friend_request:
            instance = cls.objects.create(request_from=request_from,
                request_to=request_to)
            return instance

    @classmethod
    def delete_friend(cls, request_from, request_to):
        friend = cls.objects.get(
            Q(request_from=request_from, request_to=request_to) |
            Q(request_from=request_to, request_to=request_from)
        )
        friend.delete()
        delete_friend = DeletedFriend(request_from=friend.request_from,
            request_to=friend.request_to)
        delete_friend.save()

    @classmethod
    def friends(cls, user):
        friend_list = Friend.objects.filter(
            Q(request_from=user, accepted=True) |
            Q(request_to=user, accepted=True))

        user_list = []
        for friend in friend_list:
            from_user = User.objects.get(id=friend.request_from.id)
            to_user = User.objects.get(id=friend.request_to.id)
            if from_user != user:
                if from_user not in user_list:
                    user_list.append(from_user)
            elif to_user != user:
                if to_user not in user_list:
                    user_list.append(to_user)

        return user_list


class DeletedFriend(FriendBase):
    class Meta:
        abstract = False


class Notification(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    seen = models.BooleanField(default=False)
    notification_for = models.ForeignKey(User,
        limit_choices_to={'is_active': True})


    def __unicode__(self):
        return self.notification_for.username

    @classmethod
    def notify(cls, content_object, user ):
        notify = cls.objects.create(content_object=content_object,
            notification_for=user)

    def display(self):
        comment_type = ContentType.objects.get_for_model(Comment)
        friend_type = ContentType.objects.get_for_model(Friend)
        if self.content_type == comment_type:

            comment_id = self.content_object.id
            user = Comment.objects.get(
                id=comment_id).commented_by.username

            message = "User %s commented on your post" % user

        elif self.content_type == friend_type:

            friend_id = self.content_object.id
            username = Friend.objects.get(
                id=friend_id).request_from.username
            userid = Friend.objects.get(
                id=friend_id).request_from.id

            accept = reverse('accept', args=[userid])
            cancel = reverse('deletefriend', args=[userid])
            profile = reverse('user', args=[userid])

            message = """User %s has sent you a friend request
            <a class='btn btn-primary' href='%s'>Accept request</a>
            <a class='btn btn-primary' href='%s'>Cancel request</a>
            <a class='btn btn-primary' href='%s'>view profile</a>""" % (username,
                accept, cancel, profile)

        return message