from django.conf.urls import url
from django.conf import settings
from . import views

urlpatterns = [
    url(r'^create_new/$', views.create_new, name='create_new'),
    url(r'^new/nid=(?P<new_id>[\w.\d\/\-]+)/$', views.get_new, name='get_new'),
    url(r'^new/media/media=(?P<media_id>[\w]+)&limit=(?P<limit>[\d]+)/$', views.get_new_by_media, name='get_new_by_media'),
    url(r'^new/place=(?P<place>[\w]*)&person=(?P<person>[\w]*)&fact=(?P<fact>[\w]*)/$', views.filter_new, name='filter_new'),
    url(r'^news/limit=(?P<limit>[\d]+)/$', views.get_news, name='get_news'),
]
