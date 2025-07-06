from django import forms
from .models import Post, Category
from django.contrib.auth.models import Group
from allauth.account.forms import SignupForm

class PostForm(forms.ModelForm):
    postCategory = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Категории'
    )

    class Meta:
        model = Post
        fields = ['title', 'text', 'categoryType', 'postCategory']
        widgets = {
            'categoryType': forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['postCategory'].initial = self.instance.postCategory.all()

class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        common_group = Group.objects.get(name='common')
        user.groups.add(common_group)
        return user