from django.urls import path
from .views import PostsList, PostDetail, NewsCreateView, NewsUpdateView, NewsDeleteView, ArticleCreateView, ArticleUpdateView, ArticleDeleteView, become_author, subscribe_category
from django.contrib.auth import views as auth_views
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', cache_page(60*1)(PostsList.as_view()), name='news_list'),
    path('<int:pk>', cache_page(60*5)(PostDetail.as_view()), name='post_detail'),
    path('search/', PostsList.as_view()),
# Новости
    path('create/', NewsCreateView.as_view(), name='news_create'),
    path('<int:pk>/edit/', NewsUpdateView.as_view(), name='news_edit'),
    path('<int:pk>/delete/', NewsDeleteView.as_view(), name='news_delete'),
# Статьи
    path('articles/create/', ArticleCreateView.as_view(), name='article_create'),
    path('articles/<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_edit'),
    path('articles/<int:pk>/delete/', ArticleDeleteView.as_view(), name='article_delete'),

    path('become-author/', become_author, name='become_author'),
    path('category/<int:category_id>/subscribe/', subscribe_category, name='subscribe_category'),
]