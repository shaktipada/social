from django import forms
from django.forms import ModelForm

from social_core.models import Post, Comment, Message


class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = ('status', 'status_image')

    def clean(self):
        cleaned_data = super(PostForm, self).clean()
        return cleaned_data

    def save(self, user=None):
        if not user:
            return super(PostForm, self).save()
        instance = super(PostForm, self).save(commit=False)
        instance.posted_by = user
        instance.save()
        return instance

class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ('comment',)

    def clean(self):
        cleaned_data = super(CommentForm, self).clean()
        return cleaned_data

    def save(self, user=None, comments_on=None):
        instance = super(CommentForm, self).save(commit=False)
        instance.commented_by = user
        instance.commented_on = comments_on
        instance.save()
        return instance


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('message',)

    def clean(self):
        cleaned_data = super(MessageForm, self).clean()
        return cleaned_data

    def save(self, message_from=None, message_to=None):
        instance = super(MessageForm, self).save(commit=False)
        instance.message_by = message_from
        instance.message_for = message_to
        instance.save()
        return instance