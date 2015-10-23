from django.conf.urls import url
from django.conf import settings
from . import views

urlpatterns = [
    url(r'^create_new/$', views.create_new, name='create_new'),
    url(r'^get_new/nid=(?P<new_id>[\w.\d\/\-]+)/$', views.get_new, name='get_new'),
    url(r'^get_new_media/media=(?P<media_id>[\w]+)/$', views.get_new_by_media, name='get_new_by_media'),
]