from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.views.generic.edit import FormView, View
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Q

from social_core.forms import PostForm, CommentForm, MessageForm
from social_core.models import (Post, Comment,
    Friend, Notification, Message, Like, Follow)


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):

        context = super(HomeView, self).get_context_data(**kwargs)

        context["post_form"] = PostForm()
        context["comment_form"] = CommentForm()

        friends = Friend.friends(self.request.user)

        post_list = []
        for friend in friends:
            post_list.extend(Post.objects.filter(posted_by=friend))

        paginator = Paginator(post_list, 5)
        page = self.request.GET.get('page')

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context["posts"] = posts

        return context


class ListPostView(View):

    form_class = PostForm
    template_name = 'social_core/posts.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            current_user = self.request.user
            form.save(current_user)
            return redirect(reverse('home'))
        return render(request, self.template_name, {'form': form})

    def get(self, request, *args, **kwargs):
        comment_form = CommentForm()
        post_list = Post.objects.all()
        paginator = Paginator(post_list, 5)
        page = request.GET.get('page')

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        return render(request, self.template_name, {'posts': posts,
            'comment_form': comment_form})


@login_required(login_url='login.html')
def post_view(request, id):
    post = Post.objects.get(id=id)
    comment_form = CommentForm()
    return render(request, 'social_core/postdisplay.html', {'post': post,
        'comment_form': comment_form})


@login_required(login_url='login.html')
def user_posts_view(request, id):
    post_list = Post.objects.filter(posted_by=User.objects.get(id=id))
    comment_form = CommentForm()
    paginator = Paginator(post_list, 5)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'social_core/posts.html', {
        'posts': posts, 'comment_form': comment_form})


@login_required(login_url='login.html')
def post_edit_view(request, id):
    post = Post.objects.get(id=id)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect(reverse('post', args=[post.id]))
        else:
            print form.errors
    else:
        form = PostForm()

    return render(request, 'social_core/postedit.html', {'post': post, 'form': form})


@login_required(login_url='login.html')
def post_delete_view(request, id=None):
    Post.objects.get(id=id).delete()
    return redirect(reverse('posts'))
    # for all post delete for the logged in user
    # if id:
    #     Post.objects.get(id=id).delete()
    # else:
    #     current_user = request.user
    #     posts = Post.objects.filter(posted_by=current_user)
    #     for post in posts:
    #         post.delete()
    # return redirect(reverse('posts'))


@login_required(login_url='login.html')
def comment_view(request, id=None):

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post = Post.objects.get(id=id)
            current_user = request.user
            comment = form.save(current_user, post)
            if post.posted_by != current_user:
                Notification.notify(comment, post.posted_by)
            return redirect(reverse('posts'))
        else:
            print form.errors

    return redirect(reverse('posts'))


@login_required(login_url='login.html')
def comment_delete_view(request, id=None):
    Comment.objects.get(id=id).delete()
    return redirect(reverse('posts'))


@login_required(login_url="login.html")
def user_list_view(request):

    users = User.objects.all()
    if request.method == 'POST':
        users = User.objects.filter(
            Q(first_name__icontains= request.POST['first_name']) |
            Q(last_name__icontains=request.POST['last_name']) |
            Q(email__icontains=request.POST['email']) |
            Q(username__icontains=request.POST['username'])
        )
        context_instance = RequestContext(request, {'users': users})
        user_html = render_to_string("includes/_user.html", context_instance)
        # request.user won't be directly available in the template when using render_to_string
        # we either have to pass it in the dictionary like
        # render_to_string("includes/_user.html", {'users': users, 'user': request.user})
        # or pass it as context_instance as above
        return HttpResponse(user_html)

    return render(request, 'social_core/addfriend.html', {'users': users})


@login_required(login_url="login.html")
def user_addasfriend_view(request, id):
    current_user = request.user
    request_to_user = User.objects.get(id=id)
    Friend.add_friend(current_user, request_to_user)
    friend = Friend.objects.get(request_from=current_user,
        request_to=request_to_user, accepted=False)
    Notification.notify(friend, request_to_user)
    return redirect(reverse('user', args=[id]))


@login_required(login_url="login.html")
def accepted_view(request, id):
    request_to = request.user
    request_from = User.objects.get(id=id)
    instance = Friend.objects.get(
        request_from=request_from, request_to=request_to,
        accepted=False)
    instance.accepted = True
    instance.save()
    friend_type = ContentType.objects.get_for_model(Friend)
    notification = Notification.objects.get(
        notification_for=request.user, seen=False,
        content_type=friend_type, object_id=instance.id)
    if notification:
        notification.seen = True
        notification.save()
    return redirect(reverse('user', args=[id]))


@login_required(login_url="login.html")
def user_deletefriend_view(request, id):
    request_from = User.objects.get(id=id)
    request_to = request.user
    try:
        instance = Friend.objects.get(
            request_from=request_from, request_to=request_to,
            accepted=False)
        friend_type = ContentType.objects.get_for_model(Friend)
        notification = Notification.objects.get(
            notification_for=request.user, seen=False,
            content_type=friend_type, object_id=instance.id)
        if notification:
            notification.seen = True
            notification.save()
    except Friend.DoesNotExist:
        pass
    Friend.delete_friend(request_from, request_to)
    return redirect(reverse('home'))


@login_required(login_url="login.html")
def notification_view(request):

    notifications = Notification.objects.filter(
        notification_for=request.user, seen=False)
    for notification in notifications:
        notification.seen = True
        notification.save()

    return redirect(reverse('posts'))


@login_required(login_url="login.html")
def user_friend_view(request):
    current_user = request.user
    friend_list = Friend.objects.filter(
        Q(request_from=current_user, accepted=True) |
        Q(request_to=current_user, accepted=True))

    paginator = Paginator(friend_list, 5)
    page = request.GET.get('page')
    try:
        friends = paginator.page(page)
    except PageNotAnInteger:
        friends = paginator.page(1)
    except EmptyPage:
        friends = paginator.page(paginator.num_pages)

    return render(request, 'social_core/friends.html',
        {"friends": friends})


@login_required(login_url="login.html")
def message_send_view(request, id):
    message_from = request.user
    message_for = User.objects.get(id=id)

    messages = Message.objects.filter(message_by=message_from,
        message_for=message_for)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            form.save(message_from, message_for)
            return redirect(reverse('send_message', args=[id]))
        else:
            print form.errors
    else:
        form = MessageForm()

    return render(request, 'social_core/sendmessage.html',
        {'message_form': form, 'messages': messages})


@login_required(login_url="login.html")
def message_read_view(request):

    messages = Message.objects.filter(
        message_for=request.user, unread=True)
    for message in messages:
        message.unread = False
        message.save()

    return redirect(reverse('posts'))


@login_required(login_url="login.html")
def message_view(request, id):
    current_user = request.user
    message_from = Message.objects.get(id=id).message_by
    messages = Message.objects.filter(
        message_by=message_from, message_for=current_user).order_by('created_at')

    return render(request, 'social_core/message.html',
        {'messages': messages})


@login_required(login_url="login.html")
def like_post_view(request, id):
    current_user = request.user
    content_type = Post.objects.get(id=id)
    Like.liked(content_type, current_user)
    return redirect(reverse('home'))


@login_required(login_url="login.html")
def like_comment_view(request, id):
    current_user = request.user
    content_type = Comment.objects.get(id=id)
    Like.liked(content_type, current_user)

    return redirect(reverse('home'))


@login_required(login_url="login.html")
def unlike_post_view(request, id):
    current_user = request.user
    post_type = ContentType.objects.get_for_model(Post)
    Like.objects.get(
        object_id=id, liked_by=current_user,
        content_type=post_type).delete()
    return redirect(reverse('home'))


@login_required(login_url="login.html")
def unlike_comment_view(request, id):
    current_user = request.user
    comment_type = ContentType.objects.get_for_model(Comment)
    Like.objects.get(object_id=id, liked_by=current_user,
        content_type=comment_type).delete()
    return redirect(reverse('home'))


@login_required(login_url="login.html")
def follow_user_view(request, id):
    current_user = request.user
    content_type = User.objects.get(id=id)
    Follow.following(content_type, current_user)
    return redirect(reverse('user', args=[id]))


@login_required(login_url="login.html")
def unfollow_user_view(request, id):
    current_user = request.user
    Follow.objects.get(object_id=id, followed_by=current_user).delete()
    return redirect(reverse('user', args=[id]))


@login_required(login_url="login.html")
def user_profile_view(request, id):
    profile_user = User.objects.get(id=id)
    return render(request, 'social_core/userprofile.html', {"profile_user": profile_user})