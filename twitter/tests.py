from django.db import IntegrityError
from django.test import TestCase

from .models import User, FollowRelation, Post

# Create your tests here.


class UserModelTests(TestCase):
    def setUp(self):
        self.u = User.objects.create_user('user', password='password0')

    def test_user_created(self):
        User.objects.get(username='user')

    def test_blank_following_field(self):
        self.assertEqual(self.u.followings.count(), 0)

    def test_blank_followers_field(self):
        self.assertEqual(self.u.followers.count(), 0)


class FollowRelationModelTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user('user1', password='password123')
        self.u2 = User.objects.create_user('user2', password='password456')
        self.u3 = User.objects.create_user('user3', password='password789')
        self.u1.followings.add(self.u2)

    def test_user_following_another_user(self):
        self.assertEqual(self.u1.followings.count(), 1)
        self.assertIn(self.u2, self.u1.followings.all())

        self.u1.followings.add(self.u3)
        self.assertEqual(self.u1.followings.count(), 2)
        self.assertIn(self.u2, self.u1.followings.all())
        self.assertIn(self.u3, self.u1.followings.all())

    def test_following_is_not_symmetrical(self):
        self.assertEqual(self.u2.followings.count(), 0)
        self.assertNotIn(self.u1, self.u2.followings.all())

    def test_user_has_followers(self):
        self.assertEqual(self.u2.followers.count(), 1)
        self.assertIn(self.u1, self.u2.followers.all())

        self.u2.followers.add(self.u3)
        self.assertEqual(self.u2.followers.count(), 2)
        self.assertIn(self.u1, self.u2.followers.all())
        self.assertIn(self.u3, self.u2.followers.all())

    def test_user_cannot_follow_themselves(self):
        with self.assertRaises(IntegrityError):
            self.u1.followings.add(self.u1)

    def test_unique_follow(self):
        with self.assertRaises(IntegrityError):
            FollowRelation.objects.create(follower=self.u1, followee=self.u2)

    def test_unfollow(self):
        self.u1.followings.remove(self.u2)
        self.assertEqual(self.u1.followings.count(), 0)
        self.assertEqual(self.u2.followers.count(), 0)


class PostModelTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user('user1', password='password123')
        self.u2 = User.objects.create_user('user2', password='password456')
        self.p = Post.objects.create(
            author=self.u1, body='This is a test post.'
        )

    def test_post_creation(self):
        self.assertEqual(self.p.author, self.u1)
        self.assertEqual(self.p.body, 'This is a test post.')

    def test_like_a_post(self):
        self.p.likes.add(self.u2)
        self.assertEqual(self.p.likes.count(), 1)
        self.assertIn(self.u2, self.p.likes.all())

    def test_unlike_a_post(self):
        self.p.likes.add(self.u2)
        self.p.likes.remove(self.u2)
        self.assertEqual(self.p.likes.count(), 0)
        self.assertNotIn(self.u2, self.p.likes.all())

    def test_blank_likes_field(self):
        self.assertEqual(self.p.likes.count(), 0)

    def test_like_post_by_multiple_users(self):
        self.u2.likes.add(self.p)
        another_user = User.objects.create_user(
            'user3', password='password789'
        )
        another_user.likes.add(self.p)
        self.assertEqual(self.p.likes.count(), 2)

    def test_str_post(self):
        self.assertTrue(str(self.p).startswith('user1 ('))
        self.assertTrue(str(self.p).endswith('): This is a ...'))

    def test_str_short_post(self):
        short_post = Post.objects.create(author=self.u1, body='short')
        self.assertTrue(str(short_post).startswith('user1 ('))
        self.assertTrue(str(short_post).endswith('): short'))
