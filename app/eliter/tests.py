from datetime import timedelta

from django.utils import timezone
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.cache import cache

from .models import Post, Rating
from .rating import get_average_ratings



class PostRatingTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")



    def test_get_average_ratings_all_in_cache(self):

        # Create posts
        posts = [
            Post.objects.create(title=f"Post {i}", content=f"Content for post {i}")
            for i in range(1, 10)
        ]

        post_ids = []


        for i, post in enumerate(posts, start=1):
            Rating.objects.create(post=post, user=self.user, rating=4)
            post_ids.append(post.id)
            cache.set(f'post_{post.id}_average_rating', 2, timeout=3000)



        post_averages = get_average_ratings(post_ids)

        expected_averages = {post.id: 2 for _, post in enumerate(posts, start=1)}

        self.assertEqual(post_averages, expected_averages)
        cache.clear()



    def test_get_average_ratings_all_in_db(self):

        posts = [
            Post.objects.create(title=f"Post {i}", content=f"Content for post {i}")
            for i in range(1, 10)
        ]

        post_ids = []

        for i, post in enumerate(posts, start=1):
            Rating.objects.create(post=post, user=self.user, rating=4)
            post_ids.append(post.id)

        post_averages = get_average_ratings(post_ids)

        expected_averages = {post.id: 4 for _, post in enumerate(posts, start=1)}

        self.assertEqual(post_averages, expected_averages)
        cache.clear()

    def test_get_average_ratings_cache_and_db(self):
        posts = [
            Post.objects.create(title=f"Post {i}", content=f"Content for post {i}")
            for i in range(1, 10)
        ]

        post_ids = []


        for i, post in enumerate(posts, start=1):
            Rating.objects.create(post=post, user=self.user, rating=4)
            post_ids.append(post.id)
            if post.id % 2 == 0:
                cache.set(f'post_{post.id}_average_rating', 2, timeout=3000)

        post_averages = get_average_ratings(post_ids)

        expected_averages = {post.id: 4 for i, post in enumerate(posts, start=1)}
        for id, rate in expected_averages.items():
            if id % 2 == 0:
                expected_averages[id] = 2

        self.assertEqual(post_averages, expected_averages)
        cache.clear()


    def test_calculate_average_ratings(self):
        user1 = User.objects.create_user(username="testuser1", password="<PASSWORD>")
        user2 = User.objects.create_user(username="testuser2", password="<PASSWORD>")
        user3 = User.objects.create_user(username="testuser3", password="<PASSWORD>")

        post = Post.objects.create(title=f"test", content=f"test")

        rating1 = Rating.objects.create(post=post, user=user1, rating=5)
        t1 = timezone.now() - timedelta(days=1)
        Rating.objects.filter(id=rating1.id).update(created_at=t1)

        rating2 = Rating.objects.create(post=post, user=user2, rating=3)
        t2 = timezone.now() - timedelta(days=2)
        Rating.objects.filter(id=rating2.id).update(created_at=t2)


        rating3 = Rating.objects.create(post=post, user=user3, rating=1)
        t3 = timezone.now() - timedelta(days=3)
        Rating.objects.filter(id=rating3.id).update(created_at=t3)

        avg = get_average_ratings([post.id])[post.id]

        self.assertEqual(avg, 3.0)
        cache.clear()

    def test_calculate_average_ratings_unbalance(self):
        user1 = User.objects.create_user(username="testuser1", password="<PASSWORD>")
        user2 = User.objects.create_user(username="testuser2", password="<PASSWORD>")
        user3 = User.objects.create_user(username="testuser3", password="<PASSWORD>")
        user4 = User.objects.create_user(username="testuser4", password="<PASSWORD>")

        post = Post.objects.create(title=f"test", content=f"test")

        rating1 = Rating.objects.create(post=post, user=user1, rating=7)
        t1 = timezone.now() - timedelta(days=1)
        Rating.objects.filter(id=rating1.id).update(created_at=t1)

        rating2 = Rating.objects.create(post=post, user=user2, rating=3)
        t2 = timezone.now() - timedelta(days=2)
        Rating.objects.filter(id=rating2.id).update(created_at=t2)


        rating3 = Rating.objects.create(post=post, user=user3, rating=1)
        t3 = timezone.now() - timedelta(days=3)
        Rating.objects.filter(id=rating3.id).update(created_at=t3)

        rating4 = Rating.objects.create(post=post, user=user4, rating=3)
        t4 = timezone.now() - timedelta(days=3)
        Rating.objects.filter(id=rating4.id).update(created_at=t4)

        avg = get_average_ratings([post.id])[post.id]

        self.assertEqual(avg, 4.0)
        cache.clear()














