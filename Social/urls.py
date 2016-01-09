from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required

from accounts.views import AnonymousHomeView, LogoutView
#, SignupView

from social_core.views import (HomeView, user_profile_view,
    ListPostView, post_view, post_edit_view, post_delete_view,
    user_posts_view, comment_view, comment_delete_view,
    user_addasfriend_view, user_list_view, user_deletefriend_view,
    notification_view, accepted_view, user_friend_view,
    message_view, message_read_view, message_send_view,
    like_comment_view, like_post_view, unlike_post_view,
    unlike_comment_view, follow_user_view, unfollow_user_view)

admin.autodiscover()

urlpatterns = patterns('',
    (r'^accounts/', include('allauth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^$', SignupView.as_view(), name='signup'),
    url(r'^$', AnonymousHomeView.as_view(), name='anonymoushome'),
    url(r'^users/(?P<id>[0-9]+)$', user_profile_view, name='user'),

    url(r'^addfriends/$', user_list_view, name='addfriend'),
    url(r'^accepted/(?P<id>[0-9]+)$', accepted_view, name='accept'),
    url(r'^friends/$', user_friend_view, name='user_friends'),
    url(r'^addasfriend/(?P<id>[0-9]+)$', user_addasfriend_view, name='addasfriend'),
    url(r'^deletefriend/(?P<id>[0-9]+)$', user_deletefriend_view, name='deletefriend'),

    url(r'^accounts/profile/$', TemplateView.as_view(template_name=
        'profile.html'), name='profile'),

    url(r'^home/$', login_required(HomeView.as_view()) , name='home'),
    url(r'^posts/$', login_required(ListPostView.as_view()), name='posts'),
    url(r'^posts/(?P<id>[0-9]+)$', post_view, name='post'),
    url(r'^posts/(?P<id>[0-9]+)/edit$', post_edit_view, name='edit_post'),
    url(r'^posts/(?P<id>[0-9]+)/delete$', post_delete_view, name='delete_post'),
    # url(r'^posts/delete/all$', post_delete_view, name='delete_all_posts'),
    url(r'^users/(?P<id>[0-9]+)/posts$', user_posts_view, name='user_posts'),
    url(r'^posts/(?P<id>[0-9]+)/comments$', comment_view, name='comment'),
    url(r'^posts/(?P<id>[0-9]+)/comments/delete$', comment_delete_view, name='delete_comment'),

    url(r'^notifications/markasseen$', notification_view, name='notification_seen'),

    url(r'^users/message/(?P<id>[0-9]+)$', message_view, name='message'),
    url(r'^messages/markasread$', message_read_view, name='messages_read'),
    url(r'^sendmessage/(?P<id>[0-9]+)$', message_send_view, name='send_message'),

    url(r'^likecomment/(?P<id>[0-9]+)$', like_comment_view, name='like_comment'),
    url(r'^unlikecomment/(?P<id>[0-9]+)$', unlike_comment_view, name='unlike_comment'),
    url(r'^likepost/(?P<id>[0-9]+)$', like_post_view, name='like_post'),
    url(r'^unlikepost/(?P<id>[0-9]+)$', unlike_post_view, name='unlike_post'),

    url(r'^followuser/(?P<id>[0-9]+)$', follow_user_view, name='follow'),
    url(r'^unfollow/(?P<id>[0-9]+)$', unfollow_user_view, name='unfollow'),

    url(r'^logout/$', LogoutView.as_view(), name='logout'),
)