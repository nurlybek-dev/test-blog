from blog.models import Post, ReadedPost, Subscription
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls.base import reverse


class PostCreateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='test', email='test@email.com', password='testpass')
        self.client.login(username='test', password='testpass')

    def test_get(self):
        response = self.client.get(reverse('post_new'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_post(self):
        response = self.client.post(reverse('post_new'), data={'title': 'new post', 'text': 'new post body'})
        self.assertRedirects(response, reverse('blog_detail', kwargs={'pk': self.user.pk}))
        self.assertEqual(Post.objects.count(), 1)

    def test_invalid_post(self):
        response = self.client.post(reverse('post_new'), data={'title': 'new post'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')
        self.assertEqual(Post.objects.count(), 0)


class BlogViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='test', email='test@email.com', password='testpass')
        Post.objects.create(title='post title', text='post text', author=self.user)
        self.client.login(username='test', password='testpass')
    
    def test_list_view(self):
        response = self.client.get(reverse('blog_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test')
        self.assertContains(response, '/blog/1')

    def test_detail_view(self):
        response = self.client.get(reverse('blog_detail', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New post')
        self.assertContains(response, 'post title')


class FeedViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='test', email='test@email.com', password='testpass')
        self.user2 = User.objects.create_user(
            username='test2', email='test2@email.com', password='testpass')
        Post.objects.create(title='post title', text='post text', author=self.user2)
        self.client.login(username='test', password='testpass')

    def test_no_subscriptions(self):
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'post title')
        self.assertNotContains(response, 'Mark readed')

    def test_with_subscriptions(self):
        Subscription.objects.create(subscriber=self.user, author=self.user2)
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'post title')
        self.assertContains(response, 'Mark readed')


class SubscribeTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='test', email='test@email.com', password='testpass')
        self.user2 = User.objects.create_user(
            username='test2', email='test2@email.com', password='testpass')
        self.client.login(username='test', password='testpass')

    def test_no_subscribe(self):
        response = self.client.get(reverse('blog_detail', kwargs={'pk': self.user2.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Subscribe')
    
    def test_subscribe(self):
        response = self.client.post(reverse('subscribe'), data={'author_id': self.user2.pk})
        self.assertRedirects(response, reverse('blog_detail', kwargs={'pk': self.user2.pk}))
        self.assertEqual(Subscription.objects.count(), 1)
    
    def test_subscribes(self):
        Subscription.objects.create(subscriber=self.user, author=self.user2)
        response = self.client.get(reverse('blog_detail', kwargs={'pk': self.user2.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unsubscribe')

    def test_unsubscribe(self):
        Subscription.objects.create(subscriber=self.user, author=self.user2)
        response = self.client.post(reverse('unsubscribe'), data={'author_id': self.user2.pk})
        self.assertRedirects(response, reverse('blog_detail', kwargs={'pk': self.user2.pk}))
        self.assertEqual(Subscription.objects.count(), 0)


class ReadedPostTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='test', email='test@email.com', password='testpass')
        self.user2 = User.objects.create_user(
            username='test2', email='test2@email.com', password='testpass')
        self.post = Post.objects.create(title='post title', text='post text', author=self.user2)
        self.subscription = Subscription.objects.create(subscriber=self.user, author=self.user2)
        self.client.login(username='test', password='testpass')

    def test_no_marked(self):
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'post title')
        self.assertContains(response, 'Mark readed')
    
    def test_mark(self):
        response = self.client.post(reverse('mark_readed'), data={'post_id': self.post.pk})
        self.assertRedirects(response, reverse('feed'))

    def test_marked(self):
        ReadedPost.objects.create(post=self.post, subscription=self.subscription)

        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'post title')
        self.assertContains(response, 'You readed this post')
