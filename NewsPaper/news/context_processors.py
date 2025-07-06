from django.contrib.auth.models import Group

def authors_group(request):
    try:
        return {'authors_group': Group.objects.get(name='authors')}
    except Group.DoesNotExist:
        return {'authors_group': None}