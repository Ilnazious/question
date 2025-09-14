from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.cache import cache

from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    ratingAuthor = models.SmallIntegerField(default=0)

    def update_rating(self):
        postRate = self.post_set.all().aggregate(postRating=Coalesce(Sum('rating'), 0))
        pRate = 0
        pRate += postRate.get('postRating')

        commentRate = self.authorUser.comment_set.all().aggregate(commentRating=Coalesce(Sum('rating'), 0))
        cRate = 0
        cRate += commentRate.get('commentRating')

        commentpostRate = Comment.objects.filter(commentPost__author=self).aggregate(commentpostRating=Coalesce(Sum('rating'), 0))
        cpRate = 0
        cpRate = commentpostRate.get('commentpostRating')

        self.ratingAuthor = pRate * 3 + cRate + cpRate
        self.save()

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True, help_text= _('category name'))
    subscribers = models.ManyToManyField(User, related_name='subscribed_categories', blank=True)

    def __str__(self):
        return self.name.title()

class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    ARTICLE = 'AR'
    NEWS = 'NW'
    CATEGORY_CHOICES= (
        (NEWS, _('News')),
        (ARTICLE, _('Article')),
    )
    categoryType = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=ARTICLE, verbose_name=_('Type'), help_text= _('post category'))
    dataCreation = models.DateTimeField(auto_now_add=True)
    postCategory = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=128, help_text= _('post title'))
    text = models.TextField(help_text= _('post text'))
    rating = models.SmallIntegerField(default=0)

    def __str__(self):
        return f'{self.title}: {self.text}'

    def like(self):
        self.rating +=1
        self.save()

    def dislike(self):
        self.rating -=1
        self.save()

    def preview(self):
        return self.text[0:128] + '...'

#Успешный url
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('post_detail', args=[str(self.id)])

    def clean(self):
        if self.categoryType == self.NEWS:
            today_posts = Post.objects.filter(
                author__authorUser=self.author.authorUser,
                categoryType=self.NEWS,
                dataCreation__date=timezone.now().date()
            ).count()

            if today_posts >= 3:
                raise ValidationError('Нельзя публиковать более трёх новостей в сутки')
        super().clean()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'product-{self.pk}')

class PostCategory(models.Model):
    postThrough = models.ForeignKey(Post, on_delete=models.CASCADE)
    categoryThrough = models.ForeignKey(Category, on_delete=models.CASCADE)

class Comment(models.Model):
    commentPost= models.ForeignKey(Post, on_delete=models.CASCADE)
    commentUser= models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    rating = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.commentUser.username

    def like(self):
        self.rating +=1
        self.save()

    def dislike(self):
        self.rating -=1
        self.save()

@receiver(post_save, sender=User)
def add_user_to_common_group(sender, instance, created, **kwargs):
    if created:
        common_group = Group.objects.get(name='common')
        instance.groups.add(common_group)