from django.shortcuts import render, redirect, get_object_or_404, Http404, HttpResponseRedirect
from django.views.generic.base import View
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from .models import Like
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import urlresolvers
from apps.community.models import Post
from apps.commenta.models import Comment
from apps.notifications.signals import notify


class LikesLoginRequiredMixin(LoginRequiredMixin):
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

        print(content_object._meta.model)
        print(issubclass(content_object._meta.model, Comment))

        # when like comment without login ,we need redirect to post url, so we have to get the post url form comment
        if issubclass(content_object._meta.model, Comment):
            post_pk = content_object.object_id
            content_object = Post.objects.get(pk=post_pk)

        return redirect_to_login(content_object.get_absolute_url(), self.get_login_url(),
                                 self.get_redirect_field_name())


class LikeToggleView(LikesLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        content_type = get_object_or_404(ContentType, pk=self.kwargs.get("content_type_id"))
        try:
            obj = content_type.get_object_for_this_type(pk=self.kwargs.get("object_id"))
        except ObjectDoesNotExist:
            raise Http404("Object not found.")
        like, liked = Like.objects.like_toggle(request.user, content_type, obj.id)
        if liked:
            if obj.author != self.request.user:  # 用于判断点赞人是否是作者，不够通用！因为obj的author命名可能不同
                description = ''
                if isinstance(obj, Post):
                    description = '用户 <a href="">{user}</a> 赞了你的帖子 <a href="{post_url}">{post}</a>' \
                        .format(user=self.request.user.username, post=obj.title[:30], post_url=obj.get_absolute_url())
                if isinstance(obj, Comment):
                    description = '用户 {user} 赞了你的回复 {comment}' \
                        .format(user=self.request.user.username, comment=obj.body[:30])
                notify.send(self.request.user, recipient=obj.author,
                            actor=self.request.user,
                            verb='赞',
                            description=description,
                            action_object=obj)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

    def get_login_url(self):
        return urlresolvers.reverse('usera:sign_in')
