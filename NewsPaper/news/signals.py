from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post
from django.core.mail import send_mail


@receiver(post_save, sender=Post)
def notify_subscribers_news(sender, instance, created, **kwargs):
    if created:
        subscribers_emailed = set()
        post_categories= instance.postcategory_set.all()
        for post_category in post_categories:
            category = post_category.categoryThrough
            subscribers = category.subscribers.all()
            for user in subscribers:
                if user.email and user not in subscribers_emailed:
                    subject =f'{instance.categoryType}: {instance.title}'
                    message = instance.text[:50]

                    send_mail(
                    subject=subject,
                    message=message,
                    from_email = 'Irakhimzyanovmars@yandex.ru',
                    recipient_list = [user.email],
                    fail_silently = True,
                    )
                    subscribers_emailed.add(user)