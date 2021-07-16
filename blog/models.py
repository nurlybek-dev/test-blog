from django.db import models
from django.core import mail
from django.conf import settings
from django.db.models.signals import post_save


"""
В качестве блога выступает сам пользователь, так как на одного пользователя один блог.
В данном случаи не видел смысла создавать отдельную модель для блога.
Но если бы он нужен был, то он выглядел бы так.

class Blog(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
"""


def notify_subscribers(sender, instance, created, **kwargs):
    """ Оповещания всех подписчиков о новой записи """
    if created:
        subscriptions = instance.author.subscribers.all()

        connection = mail.get_connection()
        connection.open()
        
        messages = []
        for subscription in subscriptions:
            messages.append(mail.EmailMessage(
                'New post', 
                f'Created new post {instance.title}', 
                settings.NOTIFICATION_EMAIL, 
                [subscription.subscriber.email],
                connection=connection
                )
            )
    
        connection.send_messages(messages)
        connection.close()


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='posts', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at', )

    def __str__(self) -> str:
        return self.title


class Subscription(models.Model):
    subscriber = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='subscriptions', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='subscribers', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.subscriber.username} subscribed to {self.author.username}'


class ReadedPost(models.Model):
    subscription = models.ForeignKey(Subscription, related_name='readed_posts', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='readed_posts', on_delete=models.CASCADE)

    models.UniqueConstraint(name='unique-record', fields=['subscription', 'post'])

    def __str__(self) -> str:
        return f'{self.post.title}'


post_save.connect(notify_subscribers, Post)
