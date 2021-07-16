from django.urls import path

from blog.views import FeedView, BlogListView, BlogDetaiView, PostCreateView, SubscribeView, UnsubscribeView, MarkReadedView

urlpatterns = [
    path('', FeedView.as_view(), name='feed'),
    path('blog/', BlogListView.as_view(), name='blog_list'),
    path('blog/<int:pk>/', BlogDetaiView.as_view(), name='blog_detail'),
    path('blog/subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('blog/unsubscribe/', UnsubscribeView.as_view(), name='unsubscribe'),
    path('post/new/', PostCreateView.as_view(), name='post_new'),
    path('post/mark-readed/', MarkReadedView.as_view(), name='mark_readed'),
]
