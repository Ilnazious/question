from django.contrib import admin
from .models import Category, Post
from modeltranslation.admin import TranslationAdmin

def delcategory(modeladmin, request, queryset):
    deleted_count, _ = queryset.delete()
    modeladmin.message_user(request, f'Удалено категорий: {deleted_count}')
delcategory.short_description = '🗑️ Удалить категории'


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'dataCreation', 'categoryType')
    list_filter = ('title', 'dataCreation', 'categoryType')
    search_fields = ('title', 'title')
    actions = [delcategory]

class CategoryAdmin(TranslationAdmin):
    model = Category

class PostAdmin(TranslationAdmin):
    model = Post

admin.site.register(Category)
admin.site.register(Post, PostAdmin)