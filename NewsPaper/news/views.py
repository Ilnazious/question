from django.contrib.auth.models import Group
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.http import urlencode
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Post, Author, Category
from .filters import PostFilter
from .forms import PostForm
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.cache import cache

from django.http import HttpResponse

from django.utils.translation import get_language
from django.utils.translation import activate

# from django.utils.translation import gettext as _
# from django.utils.translation import activate, get_supported_language_variant, LANGUAGE_SESSION_KEY

class PostsList(ListView):
    model = Post
    ordering = 'title'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        current_language = get_language()
        activate(current_language)
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['all_posts'] = Post.objects.all()
        context['filterset'] = self.filterset
        if self.request.user.is_authenticated:
            context['subscribed_categories'] = self.request.user.subscribed_categories.all()
        return context

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return HttpResponse(render(request, self.template_name, context))

class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

    def get_object(self, *args, **kwargs):
        obj = cache.get(f'product-{self.kwargs["pk"]}', None)
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'product-{self.kwargs["pk"]}', obj)

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_language'] = get_language()
        if self.request.user.is_authenticated:
            categories = self.object.postCategory.all()
            if categories.exists():
                context['is_subscribed'] = categories.first().subscribers.filter(
                    id=self.request.user.id
                ).exists()
                context['category'] = categories.first()
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return HttpResponse(render(request, self.template_name, context))

class CategoryPostsView(ListView):
    model = Post
    template_name = 'category_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['category_id'])
        return Post.objects.filter(category=self.category).order_by('-dateCreation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        if self.request.user.is_authenticated:
            context['is_subscribed'] = self.category.subscribers.filter(id=self.request.user.id).exists()
        return context

#Функции создания, обновления и удаления


class NewsCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'

    def get_success_url(self):
        return reverse_lazy('news_list') + '?page=1'

    def form_valid(self, form):
        today_news = Post.objects.filter(
            author__authorUser=self.request.user,
            categoryType=Post.NEWS,
            dataCreation__date=timezone.now().date()
        ).count()

        if today_news >= 3:
            form.add_error(None, 'Нельзя публиковать более 3 новостей в сутки')
            return self.form_invalid(form)

        form.instance.author = Author.objects.get_or_create(authorUser=self.request.user)[0]
        form.instance.categoryType = Post.NEWS
        return super().form_valid(form)

class NewsUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'

    def get_success_url(self):
        base_url = reverse_lazy('news_list')
        query_params = urlencode({'page': 1})
        return f"{base_url}?{query_params}"

    def get_queryset(self):
        return super().get_queryset().filter(categoryType=Post.NEWS)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author.authorUser != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class NewsDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'post_confirm_delete.html'

    def get_success_url(self):
        base_url = reverse_lazy('news_list')
        query_params = urlencode({'page': 1})
        return f"{base_url}?{query_params}"

    def get_queryset(self):
        return super().get_queryset().filter(categoryType=Post.NEWS)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author.authorUser != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ArticleCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'

    def get_success_url(self):
        base_url = reverse_lazy('news_list')
        query_params = urlencode({'page': 1})
        return f"{base_url}?{query_params}"

    def form_valid(self, form):
        # Проверка ограничения (3 статьи в день)
        today_articles = Post.objects.filter(
            author__authorUser=self.request.user,
            categoryType=Post.ARTICLE,
            dataCreation__date=timezone.now().date()
        ).count()

        if today_articles >= 3:
            form.add_error(None, 'Нельзя публиковать более 3 статей в сутки')
            return self.form_invalid(form)

        # Оригинальная логика
        author, created = Author.objects.get_or_create(authorUser=self.request.user)
        form.instance.author = author
        form.instance.categoryType = Post.ARTICLE
        return super().form_valid(form)

class ArticleUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'

    def get_success_url(self):
        base_url = reverse_lazy('news_list')
        query_params = urlencode({'page': 1})
        return f"{base_url}?{query_params}"

    def get_queryset(self):
        return super().get_queryset().filter(categoryType=Post.ARTICLE)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author.authorUser != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class ArticleDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'post_confirm_delete.html'

    def get_success_url(self):
        base_url = reverse_lazy('news_list')
        query_params = urlencode({'page': 1})
        return f"{base_url}?{query_params}"

    def get_queryset(self):
        return super().get_queryset().filter(categoryType=Post.ARTICLE)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author.authorUser != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

@login_required
def become_author(request):
    authors_group = Group.objects.get(name='authors')
    request.user.groups.add(authors_group)
    return redirect('/accounts/email')

@login_required
def subscribe_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.user in category.subscribers.all():
        category.subscribers.remove(request.user)
    else:
        category.subscribers.add(request.user)
    return redirect('news_list')