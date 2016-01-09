from django.test import TestCase
from django.utils import unittest
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.contrib.contenttypes.models import ContentType

from social_core.models import (Post, Comment, Friend, Like,
    Follow, Notification, Message)

class SimpleTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        self.user_1 = User.objects.create_user("abc",
            email="abc@xyz.com", password="123",
            **{
                'first_name': "abc",
                'last_name': "xyz"
            })
        self.user_2 = User.objects.create_user("def",
            email="def@uvw.com", password="123",
            **{
                'first_name': "def",
                'last_name': "uvw"
            })
        self.user_3 = User.objects.create_user("ghi",
            email="ghi@rst.com", password="123",
            **{
                'first_name': "ghi",
                'last_name': "rst"
            })
        self.user_4 = User.objects.create_user("jkl",
            email="jkl@opq.com", password="123",
            **{
                'first_name': "jkl",
                'last_name': "opq"
            })
        self.user_5 = User.objects.create_user("m",
            email="m@n.com", password="123",
            **{
                'first_name': "m",
                'last_name': "n"
            })

    def tearDown(self):
        self.user_1.delete()
        self.user_2.delete()
        self.user_3.delete()
        self.user_4.delete()
        self.user_5.delete()
        del self.client


    def test_response(self):

        self.client.login(username='abc', password='123')

        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('posts'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('posts'),
            {'status': "1.1"})
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse('posts'),
            {'status': "1.2"})
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse('posts'),
            {'status': "1.3"})
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('post', args=[1]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('user', args=[2]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('user_posts', args=[1]))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('edit_post', args=[1]),
            {'status': '1.1.1'})
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('delete_post', args=[1]))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('follow', args=[2]))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('unfollow', args=[2]))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

        self.client.login(username='m', password='123')

        response = self.client.post(reverse('posts'),
            {'status': "5.1"})
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse('posts'),
            {'status': "5.2"})
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse('comment', args=[2]),
            {'comment': "5.1.(1.2)"})
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse('comment', args=[3]),
            {'comment': "5.1.(1.3)"})
        self.assertEqual(response.status_code, 302)

        # response = self.client.get(reverse('delete_all_posts'))
        # self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('addfriend'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('addasfriend', args=[3]))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('deletefriend', args=[3]))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('addasfriend', args=[3]))
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse('send_message', args=[3]),
            {'message': "5.1.(message 3.1)"})
        self.assertEqual(response.status_code, 302)

        self.client.logout()

        self.client.login(username='ghi', password='123')

        response = self.client.get(reverse('accept', args=[5]))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('notification_seen'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('message', args=[1]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('messages_read'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('like_comment', args=[1]))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('unlike_comment', args=[1]))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('like_post', args=[2]))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('unlike_post', args=[2]))
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse('comment', args=[3]),
            {'comment': "5.1.(1.3)"})
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('delete_comment', args=[3]))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('user_friends'))
        self.assertEqual(response.status_code, 200)

        self.client.logout()

    def test_models(self):

        friends, friend_requests, follow = Friend.are_connected(
            self.user_1, self.user_2)
        self.assertEqual(friends, 0)
        self.assertEqual(friend_requests, 0)
        self.assertEqual(follow, False)

        friend_list = Friend.friends(self.user_1)
        self.assertEqual(len(friend_list), 0)

        self.client.login(username='abc', password='123')

        response = self.client.post(reverse('posts'),
            {'status': "1.1"})
        self.assertEqual(response.status_code, 302)

        self.client.logout()

        self.client.login(username='def', password='123')

        response = self.client.post(reverse('comment', args=[1]),
            {'comment': "5.1.(1.2)"})
        self.assertEqual(response.status_code, 302)

        self.client.logout()

        self.client.login(username='abc', password='123')

        notification = Notification.objects.get(id=1)
        message = notification.display()
        self.assertEqual(message, "User def commented on your post" )

        self.client.logout()