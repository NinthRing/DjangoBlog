from .models import Tag


def tags(request):
    tag_list = Tag.objects.all()[:10]
    return {'tag_list': tag_list}
