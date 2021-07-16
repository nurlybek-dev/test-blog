from django.contrib import admin

from blog.models import Post, Subscription, ReadedPost


admin.site.register(Post)
admin.site.register(Subscription)
admin.site.register(ReadedPost)
