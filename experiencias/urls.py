from django.conf.urls import url
from . import views

app_name = 'experiencias'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url('^(?P<user_post_id>[0-9]+)/$', views.userpost, name='userpost'),
    url('^register/$', views.register, name='register'),
    url(r'^registeruser/$', views.registeruser, name='registeruser'),
    url('^login/$', views.userlogin, name='userlogin'),
    url(r'^loginuser/$', views.loginuser, name='loginuser'),
    url(r'^logout/$', views.logoutuser, name='logoutuser'),
    url('^makepost/$', views.makepost, name='makepost'),
    url(r'^createpost/$', views.createpost, name='createpost'),
    url(r'^(?P<user_post_id>[0-9]+)/createcomment/$', views.createcomment, name='createcomment'),
    url(r'^(?P<user_comment_id>[0-9]+)/deletecomment/$', views.deletecomment, name='deletecomment'),
    url(r'^deletepost/(?P<user_post_id>[0-9]+)/$', views.deletepost, name='deletepost'),
    url(r'^(?P<user_post_id>[0-9]+)/editpost/$', views.editpost, name='editpost'),
    url(r'^(?P<user_post_id>[0-9]+)/editLogicPost/$', views.editLogicPost, name='editLogicPost'),
    url(r'^showAll', views.showAll, name='showAll'),
    url(r'^aboutUs', views.aboutUs, name='aboutUs'),
    url(r'^activate/(?P<user_id>[0-9]+)/$', views.activate, name='activate'),
    url(r'^activateuser', views.activateuser, name='activateuser'),
]
