from django.shortcuts import render

# Create your views here.
# 关注某个帖子
from django.shortcuts import render, redirect, get_object_or_404, Http404, HttpResponseRedirect
from django.views.generic.base import View
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from .models import Follow
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import urlresolvers
from apps.community.models import Post
from apps.commenta.models import Comment
from apps.notifications.signals import notify


class FollowLoginRequiredMixin(LoginRequiredMixin):
    """
    for likes,the default LoginRequired is not satisfied our demand,
    since we want when we use the get method to the like create view
    url that redirect to the post detail page.
    so the temp solution is custom a LoginRequiredMixin,but need a more elegant method further.
    """

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        ctype_pk = self.kwargs.get('content_type_id')
        object_pk = self.kwargs.get("object_id")
        content_type = get_object_or_404(ContentType, pk=int(ctype_pk))
        content_object = content_type.get_object_for_this_type(pk=int(object_pk))

        return redirect_to_login(content_object.get_absolute_url(), self.get_login_url(),
                                 self.get_redirect_field_name())


class FollowToggleView(FollowLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        content_type = get_object_or_404(ContentType, pk=self.kwargs.get("content_type_id"))
        try:
            obj = content_type.get_object_for_this_type(pk=self.kwargs.get("object_id"))
        except ObjectDoesNotExist:
            raise Http404("Object not found.")
        follow, followed = Follow.objects.follow_toggle(request.user, content_type, obj.id)
        if followed:
            if obj.author != self.request.user:  # 用于关注人点赞人是否是作者，不够通用！因为obj的author命名可能不同
                description = '用户 {user} 关注了你的帖子 {post}' \
                    .format(user=self.request.user.username, post=obj.title)
                notify.send(self.request.user, recipient=obj.author,
                            actor=self.request.user,
                            verb='关注',
                            description=description,
                            action_object=obj)
            else:
                # 不能关注自己发表的帖子
                print(obj.author, self.request.user)
                follow.delete()
                print('88888')
            print('------------')
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

    def get_login_url(self):
        return urlresolvers.reverse('usera:sign_in')
