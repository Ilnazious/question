from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from .models import Post
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post
from .tasks import notify_subscribers

@receiver(m2m_changed, sender=Post.postCategory.through)
def notify_subscribers_new_post(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        from .models import Category
        subscribers_notified = set()
        post_url = settings.SITE_URL + reverse('post_detail', args=[instance.id])

        for category in Category.objects.filter(pk__in=pk_set):
            for user in category.subscribers.exclude(id__in=[u.id for u in subscribers_notified]):
                if user.email:
                    send_mail(
                        subject=f'Новый материал в категории "{category.name}"',
                        message=(
                            f"Здравствуйте, {user.username}!\n\n"
                            f"Новый {instance.get_categoryType_display().lower()}:\n"
                            f"«{instance.title}»\n\n"
                            f"{instance.preview()}\n\n"
                            f"Читать полностью: {post_url}\n\n"
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True,
                    )
                    subscribers_notified.add(user)

User = get_user_model()

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created and instance.email:
        subject = 'Добро пожаловать на наш новостной портал!'
        message = f"""
        Здравствуйте, {instance.username}!

        Спасибо за регистрацию на {settings.SITE_NAME}.

        Теперь вы можете:
        - Комментировать статьи
        - Подписываться на категории
        - Создавать публикации (после получения статуса автора)

        Начните знакомство: {settings.SITE_URL}
        """
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=False,
        )

@receiver(m2m_changed, sender=Post.postCategory.through)
def post_created(sender, instance, created, **kwargs):
    if created:
        notify_subscribers.delay(instance.id)