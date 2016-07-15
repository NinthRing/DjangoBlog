from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^create-post/$', views.PostCreateView.as_view(), name='create_post'),
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^follows/$', views.UserFollowsListView.as_view(), name='follow'),
    url(r'^post/(?P<post_id>\d+)$', views.PostDetailView.as_view(), name='detail'),
    url(r'^tags/$', views.TagsListView.as_view(), name='tag'),
    url(r'^tag/(?P<tag_id>\d+)/$', views.TagPostListView.as_view(), name='tag_post'),
    url(r'^profile/$', views.profile, name='profile'),
]
