from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Post, Category
from datetime import datetime, timedelta


@shared_task
def notify_subscribers(post_id):
    post = Post.objects.get(id=post_id)
    categories = post.categories.all()
    subscribers = Subscriber.objects.filter(category__in=categories).distinct()

    for subscriber in subscribers:
        html_content = render_to_string('email/post_notification.html', {
            'post': post,
            'user': subscriber.user,
        })

        send_mail(
            subject=f'Новая статья в категории {", ".join([cat.name for cat in categories])}',
            message='',
            from_email='admin@newspaper.com',
            recipient_list=[subscriber.user.email],
            html_message=html_content,
        )


@shared_task
def weekly_newsletter():
    last_week = datetime.now() - timedelta(days=7)
    new_posts = Post.objects.filter(created_at__gte=last_week)

    for category in Category.objects.all():
        subscribers = Subscriber.objects.filter(category=category)
        posts = new_posts.filter(categories=category)

        if posts.exists() and subscribers.exists():
            for subscriber in subscribers:
                html_content = render_to_string('email/weekly_digest.html', {
                    'posts': posts,
                    'category': category,
                    'user': subscriber.user,
                })

                send_mail(
                    subject=f'Еженедельная подборка новостей в категории {category.name}',
                    message='',
                    from_email='admin@newspaper.com',
                    recipient_list=[subscriber.user.email],
                    html_message=html_content,
                )