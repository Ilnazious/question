from django_filters import FilterSet
import django_filters
from django import forms
from .models import Post, User

class PostFilter(FilterSet):
    username = django_filters.CharFilter(field_name='author__authorUser__username',lookup_expr='icontains', label='Автор')
    date_after = django_filters.DateFilter(field_name='dataCreation',lookup_expr='gte',label='Дата публикации (не ранее)',widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],
        }