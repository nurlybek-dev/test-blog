from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Q, Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import CreateView, ListView, DetailView

from blog.models import Post, Subscription, ReadedPost


User = get_user_model()


class FeedView(LoginRequiredMixin, ListView):
    """ Лента новостей пользователя. 
    Берутся все посты пользователей на которых он подписан.
    К каждому посту добавляется метка о прочтений.
    """
    model = Post
    template_name = 'blog/feed.html'
    context_object_name = 'posts'

    def get_queryset(self):
        is_readed = Count('readed_posts', filter=Q(readed_posts__subscription__subscriber=self.request.user))
        subscriptions = Subscription.objects.filter(subscriber=self.request.user).values('author')
        return Post.objects.filter(author__in=subscriptions).annotate(is_readed=is_readed).order_by('-created_at')


class BlogListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'blog/blog_list.html'
    context_object_name = 'users'


class BlogDetaiView(LoginRequiredMixin, DetailView):
    """ Представление блога пользователя.
    Для проверки статуса в контексте добавляется метка о подписке
    """
    model = User
    template_name = 'blog/blog_detail.html'
    context_object_name = 'author'

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['is_subscribed'] = Subscription.objects.filter(author=kwargs['author'], subscriber=self.request.user)
        return kwargs


class PostCreateView(LoginRequiredMixin, CreateView):
    """ Форма создания поста """
    model = Post
    fields = ['title', 'text']
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog_detail', kwargs={'pk': self.request.user.pk})


class SubscribeView(LoginRequiredMixin, View):
    """ Подписка к блогу.
    Используется get_or_create что бы не проверять дубликаты
    """
    def post(self, request, *args, **kwargs):
        author_id = request.POST.get('author_id', None)
        subscriber = request.user

        Subscription.objects.get_or_create(author_id=author_id, subscriber=subscriber)

        return redirect(reverse('blog_detail', kwargs={'pk': author_id}))


class UnsubscribeView(LoginRequiredMixin, View):
    """ Подписка от блога """
    def post(self, request, *args, **kwargs):
        author_id = request.POST.get('author_id', None)
        Subscription.objects.filter(author_id=author_id, subscriber=request.user).delete()
        return redirect(reverse('blog_detail', kwargs={'pk': author_id}))


class MarkReadedView(LoginRequiredMixin, View):
    """ Форма пометки о прочтений поста. 
    Проверка на дубликат не нужна, так как комбинация subscription и post уникальна.
    """
    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('post_id', None)
        post = get_object_or_404(Post, pk=post_id)

        subscription = Subscription.objects.filter(author=post.author, subscriber=request.user).first()

        ReadedPost.objects.create(subscription=subscription, post=post)

        return redirect(reverse('feed'))
