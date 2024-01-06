
from django.urls import path
from django.urls import include, re_path
from .import views

app_name='music'

'''
urlpatterns = [
path("<str:album_id>/",views.detail,name="detail"),
                path("",views.index,name="index"),
                path("<str:album_id>/favorite/",views.favorite,name="favorite"),
                
    ]
'''

urlpatterns = [
re_path(r'(?P<pk>[0-9]+)/$',views.DetailView.as_view(),name="detail"),
path("",views.IndexView.as_view(),name="index"),
re_path(r'album/add/$',views.AlbumCreate.as_view(),name='album-add'),
re_path(r'album/(?P<pk>[0-9]+)/$',views.AlbumUpdate.as_view(),name='album-update'),
re_path(r'album/(?P<pk>[0-9]+)/delete/$',views.AlbumDelete.as_view(),name='album-delete'),
]


#path("register/",views.UserFormView.as_view(),name='register'),
