from django_filters import FilterSet
import django_filters
from django import forms
from .models import Post, User

from django.utils.translation import gettext_lazy as _

class PostFilter(FilterSet):
    username = django_filters.CharFilter(field_name='author__authorUser__username',lookup_expr='icontains', label=_('Author'))
    date_after = django_filters.DateFilter(field_name='dataCreation',lookup_expr='gte',label=_('Publication date(since)'),widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],
        }